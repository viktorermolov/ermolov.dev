"""Outbound-only bridge from the website's durable inbox to Notification Bot.

Only identifiers and fixed error codes enter logs/state. Lead text remains in
Cloudflare and the existing bot's queue. There is no public HTTP listener.
"""

import json
import logging
import os
import random
import re
import signal
import tempfile
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


LOG = logging.getLogger("lead-relay")
UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z")
DAY = 86400
USER_AGENT = "ermolov-lead-relay/1.0 (+https://ermolov.dev)"


def timestamp(value):
    if not isinstance(value, str):
        raise ValueError("Invalid timestamp")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Timestamp requires timezone")
    return parsed.timestamp()


def base_url(value, *, public=False):
    parsed = urlsplit(value)
    allowed = {"https"} if public else {"http", "https"}
    if (parsed.scheme not in allowed or not parsed.hostname or parsed.username
            or parsed.password or parsed.query or parsed.fragment
            or any(char.isspace() for char in value)):
        raise ValueError("Invalid service URL")
    return value.rstrip("/")


@dataclass(frozen=True)
class Settings:
    leads_url: str
    relay_token: str = field(repr=False)
    notification_url: str
    notification_key: str = field(repr=False)
    state_dir: Path

    @classmethod
    def from_env(cls):
        relay_token = os.environ.get("RELAY_TOKEN", "")
        notification_key = os.environ.get("NOTIFICATION_API_KEY", "")
        if any(not re.fullmatch(r"[!-~]{32,256}", key)
               for key in (relay_token, notification_key)):
            raise ValueError("Service credentials must be 32-256 printable ASCII characters")
        return cls(
            base_url(os.environ.get("LEADS_API_URL", "https://ermolov.dev/api"), public=True),
            relay_token,
            base_url(os.environ.get("NOTIFICATION_URL", "http://notification-bot:8080")),
            notification_key,
            Path(os.environ.get("RELAY_STATE_DIR", "/app/state")),
        )


class APIError(Exception):
    def __init__(self, service, code, *, status=0, retry_after=0):
        self.service = service
        self.code = code
        self.status = status
        self.retry_after = retry_after
        super().__init__(f"{service}_{code}")

    @property
    def auth(self):
        return self.status in (401, 403)


class LeaseLost(Exception):
    pass


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Neither API credential may be forwarded to another origin.
        return None


class HTTPClient:
    def __init__(self):
        self.opener = build_opener(NoRedirect)

    def request(self, service, method, url, token, payload=None, key=None):
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json",
                   "User-Agent": USER_AGENT}
        data = None
        if payload is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(payload, ensure_ascii=True, separators=(",", ":")).encode()
        if key is not None:
            headers["Idempotency-Key"] = key
        request = Request(url, data=data, headers=headers, method=method)
        try:
            with self.opener.open(request, timeout=15) as response:
                body = response.read(131073)
                if len(body) > 131072:
                    raise APIError(service, "invalid_response")
                try:
                    result = json.loads(body)
                except (ValueError, UnicodeError):
                    raise APIError(service, "invalid_response") from None
                if not isinstance(result, dict):
                    raise APIError(service, "invalid_response")
                return result
        except HTTPError as error:
            # Never surface server response text or exception URLs in logs.
            retry = 0
            raw_retry = error.headers.get("Retry-After", "")
            try:
                retry = max(0, int(raw_retry))
            except ValueError:
                try:
                    retry = max(0, parsedate_to_datetime(raw_retry).timestamp() - time.time())
                except (ValueError, TypeError, OverflowError):
                    pass
            error.close()
            raise APIError(service, f"http_{error.code}", status=error.code,
                           retry_after=min(retry, DAY)) from None
        except (URLError, TimeoutError, OSError):
            raise APIError(service, "unavailable") from None


def atomic_json(path, value):
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w") as handle:
            json.dump(value, handle, separators=(",", ":"))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Alerts:
    """Durable alert keys close the send/commit gap without storing lead PII."""

    def __init__(self, path, now=time.time):
        self.path = path
        self.now = now
        if path.exists():
            # Fail closed if durable dedup state is corrupt; never silently reset it.
            self.state = json.loads(path.read_text())
            if (not isinstance(self.state, dict) or self.state.get("version") != 1
                    or not isinstance(self.state.get("pending"), list)
                    or not isinstance(self.state.get("attention"), dict)):
                raise ValueError("Invalid alert state")
        else:
            self.state = {"version": 1, "fault": None, "pending": [], "attention": {}}

    def save(self):
        atomic_json(self.path, self.state)

    def enqueue(self, message, level, *, key=None):
        # Bounded local metadata; when full, retain earlier unsent alerts.
        if len(self.state["pending"]) >= 100:
            return False
        self.state["pending"].append({
            "key": key or f"ermolov-relay:{uuid.uuid4()}",
            "created": self.now(),
            "payload": {"title": "Website contact relay", "message": message, "level": level},
        })
        return True

    def fault(self, code):
        if self.state["fault"] is not None:
            return
        self.state["fault"] = {"code": code, "since": self.now()}
        self.enqueue(f"Contact delivery needs attention. Error: {code}. Leads remain in Cloudflare.", "error")
        self.save()

    def recovered(self):
        if self.state["fault"] is None:
            return
        self.enqueue("Contact relay connectivity recovered. Pending leads will continue processing.", "success")
        self.state["fault"] = None
        self.save()

    def attention(self, lead_id, code):
        seen = {key: created for key, created in self.state["attention"].items()
                if created > self.now() - 30 * DAY}
        if lead_id in seen:
            return True
        if self.enqueue(f"A project inquiry needs manual review. Lead: {lead_id}. Error: {code}.",
                        "warning", key=f"ermolov-attention:{lead_id}:v1"):
            seen[lead_id] = self.now()
            self.state["attention"] = dict(sorted(seen.items(), key=lambda item: item[1])[-1000:])
            self.save()
            return True
        return False

    def flush(self, send):
        # At most five per cycle; alert traffic cannot crowd out lead delivery.
        for item in list(self.state["pending"][:5]):
            if self.now() - item["created"] >= 30 * DAY:
                LOG.error("alert_dedup_window_expired")
                self.state["pending"].remove(item)
                self.save()
                continue
            try:
                send(item["payload"], item["key"])
            except APIError:
                return
            self.state["pending"].remove(item)
            self.save()


class Relay:
    def __init__(self, settings, *, client=None, now=time.time, monotonic=time.monotonic):
        self.settings = settings
        self.client = client or HTTPClient()
        self.now = now
        self.monotonic = monotonic
        self.alerts = Alerts(settings.state_dir / "alerts.json", now)
        self.last_success = None

    def cloud(self, method, path, payload=None):
        return self.client.request("cloudflare", method, self.settings.leads_url + path,
                                   self.settings.relay_token, payload)

    def bot(self, method, path, payload=None, key=None):
        return self.client.request("notification", method, self.settings.notification_url + path,
                                   self.settings.notification_key, payload, key)

    def alert_send(self, payload, key):
        self.heartbeat("processing")
        self.bot("POST", "/v1/notifications", payload, key)

    def heartbeat(self, status):
        atomic_json(self.settings.state_dir / "health.json", {
            "heartbeat": self.now(), "status": status, "lastSuccess": self.last_success,
        })

    def check_lease(self, lease):
        if self.monotonic() >= lease["deadline"]:
            raise LeaseLost()

    def update(self, lease, action, **fields):
        self.check_lease(lease)
        started = self.monotonic()
        try:
            result = self.cloud("POST", f"/internal/leads/{lease['id']}/update", {
                "leaseToken": lease["token"], "action": action, **fields,
            })
        except APIError as error:
            if error.status in (404, 409):
                raise LeaseLost() from None
            raise
        if result.get("ok") is not True:
            raise APIError("cloudflare", "invalid_response")
        if action == "progress":
            try:
                remaining = timestamp(result["leaseExpiresAt"]) - self.now()
            except (KeyError, ValueError, TypeError, OverflowError):
                raise APIError("cloudflare", "invalid_response") from None
            lease["deadline"] = min(started + 110, self.monotonic() + remaining - 10)

    def attention(self, lease, code, notification_id=None):
        fields = {"errorCode": code}
        if notification_id:
            fields["notificationId"] = notification_id
        # Persist the warning before removing this lead from the claim queue.
        # A crash after Cloudflare commits attention must not lose its only
        # operator alert. An expired lease can leave an early warning, but its
        # terminal bot failure/ambiguous receipt already warrants attention.
        if not self.alerts.attention(lease["id"], code):
            raise APIError("relay", "alert_queue_full")
        self.update(lease, "attention", **fields)
        LOG.warning("lead_attention id=%s code=%s", lease["id"], code)

    def process(self, item, claim_started):
        try:
            lead_id = item["id"]
            if not isinstance(lead_id, str) or not UUID.fullmatch(lead_id):
                raise ValueError("Invalid lead id")
            remaining = timestamp(item["leaseExpiresAt"]) - self.now()
            lease = {"id": lead_id, "token": item["leaseToken"],
                     "deadline": min(claim_started + 110, self.monotonic() + remaining - 10)}
            first_attempt = timestamp(item["firstAttemptAt"])
            payload = item["payload"]
            notification_id = item.get("notificationId")
            if (not isinstance(lease["token"], str) or not lease["token"]
                    or not isinstance(payload, dict)
                    or set(payload) != {"title", "message", "level"}
                    or not all(isinstance(value, str) for value in payload.values())
                    or (notification_id is not None and not UUID.fullmatch(notification_id))):
                raise ValueError("Invalid lead")
        except (KeyError, TypeError, ValueError, OverflowError):
            raise APIError("cloudflare", "invalid_response") from None

        # Refresh each batch item's lease before any external side effect. If the
        # batch took too long, check_lease fails and the next claim recovers it.
        self.update(lease, "progress", **({"notificationId": notification_id} if notification_id else {}))
        self.check_lease(lease)
        try:
            if notification_id is None:
                if self.now() - first_attempt >= 30 * DAY - 300:
                    self.attention(lease, "dedup_window_expired")
                    return
                result = self.bot("POST", "/v1/notifications", payload, f"ermolov-lead:{lead_id}:v1")
                notification_id = result.get("id")
                if not isinstance(notification_id, str) or not UUID.fullmatch(notification_id):
                    raise APIError("notification", "invalid_response")
                # This is the durable receipt, not a delivery acknowledgement.
                self.update(lease, "progress", notificationId=notification_id)
                self.check_lease(lease)
            result = self.bot("GET", f"/v1/notifications/{notification_id}")
            if result.get("id") != notification_id:
                raise APIError("notification", "invalid_response")
            status = result.get("status")
            if status == "sent":
                self.update(lease, "sent", notificationId=notification_id)
                LOG.info("lead_sent id=%s", lead_id)
            elif status == "queued":
                self.update(lease, "retry", notificationId=notification_id, delaySeconds=60)
            elif status == "failed":
                self.attention(lease, "notification_failed", notification_id)
            else:
                raise APIError("notification", "invalid_response")
        except APIError as error:
            # A Cloudflare failure aborts this batch. In particular, never send
            # another message after an authorization failure or failed renewal.
            if error.service != "notification":
                raise
            if error.status in (400, 404, 409, 413, 415):
                self.attention(lease, f"notification_http_{error.status}", notification_id)
                return
            fields = {"delaySeconds": max(60, int(error.retry_after)),
                      "errorCode": f"notification_{error.code}"}
            if notification_id:
                fields["notificationId"] = notification_id
            self.update(lease, "retry", **fields)
            raise

    def tick(self, stopping=None):
        started = self.monotonic()
        result = self.cloud("POST", "/internal/leads/claim", {})
        items = result.get("leads")
        if not isinstance(items, list) or len(items) > 5:
            raise APIError("cloudflare", "invalid_response")
        if not items:
            # An empty inbox must not falsely announce recovery while the bot
            # remains down. Health is local readiness, not Telegram delivery.
            readiness = self.bot("GET", "/healthz")
            if readiness.get("status") != "ok":
                raise APIError("notification", "unhealthy")
        for item in items:
            if stopping is not None and stopping.is_set():
                break
            self.heartbeat("processing")
            try:
                self.process(item, started)
            except LeaseLost:
                LOG.warning("lead_lease_expired")
        self.last_success = self.now()


def run(settings):
    relay = Relay(settings)
    stopping = threading.Event()
    for signum in (signal.SIGTERM, signal.SIGINT):
        signal.signal(signum, lambda *_: stopping.set())
    failures = 0
    while not stopping.is_set():
        relay.heartbeat("processing")
        try:
            relay.tick(stopping)
        except APIError as error:
            failures += 1
            code = f"{error.service}_{error.code}"
            LOG.warning("relay_unavailable code=%s", code)
            relay.alerts.fault(code)
            # Exponential backoff caps at 15 minutes. Longer server-requested
            # cooldowns are honored; heartbeat continues during either wait.
            delay = max(min(900, 60 * (2 ** min(failures - 1, 4))), error.retry_after)
            status = "degraded"
        else:
            failures = 0
            relay.alerts.recovered()
            delay = 60
            status = "ok"
        if not stopping.is_set():
            relay.alerts.flush(relay.alert_send)
        deadline = time.monotonic() + delay + random.uniform(0, min(10, delay * 0.1))
        while not stopping.is_set():
            relay.heartbeat(status)
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            stopping.wait(min(30, remaining))
    relay.heartbeat("stopped")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    try:
        run(Settings.from_env())
    except Exception:
        # Tracebacks can include HTTP URLs or caller input. Docker supervision
        # restarts unexpected failures; durable Cloudflare leases recover work.
        LOG.error("relay_stopped_unexpectedly; inspect configuration and persistent state")
        raise SystemExit(1) from None
