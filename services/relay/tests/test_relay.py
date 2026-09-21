import copy
import io
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from healthcheck import healthy
from relay import APIError, Alerts, DAY, HTTPClient, LeaseLost, NoRedirect, Relay, Settings, USER_AGENT


LEAD_ID = "d2d312ca-40a7-4a8a-a3bf-a6288d2e1de4"
BOT_ID = "7a7fbbf8-19e2-45f3-af85-d6d28bce1eef"
NOW = 1790027350.0


def iso(seconds):
    return datetime.fromtimestamp(seconds, timezone.utc).isoformat()


def lead(**changes):
    value = {"id": LEAD_ID, "leaseToken": "lease-secret", "leaseExpiresAt": iso(NOW + 120),
             "firstAttemptAt": iso(NOW), "notificationId": None,
             "payload": {"title": "New project inquiry", "message": "Name: User\nEmail: a@example.test\n😀 Привет",
                         "level": "info"}}
    value.update(changes)
    return value


def update_ok():
    return {"ok": True, "id": LEAD_ID, "leaseExpiresAt": iso(NOW + 120)}


class FakeClient:
    def __init__(self, *responses):
        self.responses = list(responses)
        self.calls = []

    def request(self, service, method, url, token, payload=None, key=None):
        self.calls.append({"service": service, "method": method, "url": url,
                           "payload": copy.deepcopy(payload), "key": key})
        if not self.responses:
            raise AssertionError("Unexpected network request")
        result = self.responses.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


class RelayTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.settings = Settings("https://ermolov.dev/api", "r" * 40,
                                 "http://notification-bot:8080", "n" * 40,
                                 Path(self.directory.name))

    def tearDown(self):
        self.directory.cleanup()

    def relay(self, *responses):
        client = FakeClient(*responses)
        return Relay(self.settings, client=client, now=lambda: NOW, monotonic=lambda: 100), client

    def test_durable_receipt_then_delivery_ack_and_exact_unicode_payload(self):
        item = lead()
        relay, client = self.relay(update_ok(), {"id": BOT_ID, "status": "queued"},
                                   update_ok(), {"id": BOT_ID, "status": "sent"}, update_ok())
        relay.process(item, 100)
        self.assertEqual(client.calls[1]["payload"], item["payload"])
        self.assertEqual(client.calls[1]["key"], f"ermolov-lead:{LEAD_ID}:v1")
        self.assertEqual(client.calls[2]["payload"]["notificationId"], BOT_ID)
        self.assertEqual(client.calls[2]["payload"]["action"], "progress")
        self.assertEqual(client.calls[-1]["payload"]["action"], "sent")

    def test_queued_is_not_delivery_and_retains_id(self):
        relay, client = self.relay(update_ok(), {"id": BOT_ID, "status": "queued"}, update_ok())
        relay.process(lead(notificationId=BOT_ID), 100)
        self.assertEqual(client.calls[-1]["payload"]["action"], "retry")
        self.assertEqual(client.calls[-1]["payload"]["notificationId"], BOT_ID)
        self.assertFalse(any(c["service"] == "notification" and c["method"] == "POST" for c in client.calls))

    def test_crash_after_enqueue_before_progress_replays_same_key(self):
        relay, client = self.relay(update_ok(), {"id": BOT_ID, "status": "queued"},
                                   APIError("cloudflare", "unavailable"))
        with self.assertRaises(APIError):
            relay.process(lead(), 100)
        replay, second_client = self.relay(update_ok(), {"id": BOT_ID, "status": "sent"},
                                           update_ok(), {"id": BOT_ID, "status": "sent"}, update_ok())
        replay.process(lead(), 100)
        self.assertEqual(client.calls[1]["key"], second_client.calls[1]["key"])
        self.assertEqual(client.calls[1]["payload"], second_client.calls[1]["payload"])

    def test_timeout_ambiguous_enqueue_is_retryable_with_same_key(self):
        relay, client = self.relay(update_ok(), APIError("notification", "unavailable"), update_ok())
        with self.assertRaises(APIError):
            relay.process(lead(), 100)
        self.assertEqual(client.calls[-1]["payload"]["action"], "retry")
        self.assertNotIn("notificationId", client.calls[-1]["payload"])

    def test_bot_rate_limit_respects_retry_after(self):
        relay, client = self.relay(update_ok(), APIError("notification", "http_429", status=429,
                                                        retry_after=180), update_ok())
        with self.assertRaises(APIError):
            relay.process(lead(), 100)
        self.assertEqual(client.calls[-1]["payload"]["delaySeconds"], 180)

    def test_failed_and_unknown_notifications_preserve_for_attention(self):
        for response, code in (({"id": BOT_ID, "status": "failed"}, "notification_failed"),
                               (APIError("notification", "http_404", status=404), "notification_http_404")):
            with self.subTest(code=code):
                relay, client = self.relay(update_ok(), response, update_ok())
                relay.process(lead(notificationId=BOT_ID), 100)
                self.assertEqual(client.calls[-1]["payload"]["action"], "attention")
                self.assertEqual(client.calls[-1]["payload"]["errorCode"], code)
                self.assertFalse(any(c["service"] == "notification" and c["method"] == "POST" for c in client.calls))

    def test_dedup_window_expired_never_recreates(self):
        relay, client = self.relay(update_ok(), update_ok())
        relay.process(lead(firstAttemptAt=iso(NOW - 30 * DAY)), 100)
        self.assertEqual(client.calls[-1]["payload"]["action"], "attention")
        self.assertEqual(client.calls[-1]["payload"]["errorCode"], "dedup_window_expired")
        self.assertTrue(all(c["service"] == "cloudflare" for c in client.calls))

    def test_payload_conflict_not_retried_with_new_key(self):
        relay, client = self.relay(update_ok(), APIError("notification", "http_409", status=409), update_ok())
        relay.process(lead(), 100)
        self.assertEqual(client.calls[-1]["payload"]["action"], "attention")

    def test_expired_lease_has_no_side_effects(self):
        relay, client = self.relay()
        with self.assertRaises(LeaseLost):
            relay.process(lead(leaseExpiresAt=iso(NOW)), 100)
        self.assertEqual(client.calls, [])

    def test_lost_lease_renewal_never_sends(self):
        relay, client = self.relay(APIError("cloudflare", "http_409", status=409))
        with self.assertRaises(LeaseLost):
            relay.process(lead(), 100)
        self.assertEqual(len(client.calls), 1)

    def test_auth_failure_aborts_remaining_batch_without_sending(self):
        relay, client = self.relay({"leads": [lead(), lead()]},
                                   APIError("cloudflare", "http_401", status=401))
        with self.assertRaises(APIError) as failure:
            relay.tick()
        self.assertTrue(failure.exception.auth)
        self.assertTrue(all(c["service"] == "cloudflare" for c in client.calls))

    def test_auth_failure_after_enqueue_prevents_status_or_second_send(self):
        relay, client = self.relay({"leads": [lead(), lead()]}, update_ok(),
                                   {"id": BOT_ID, "status": "queued"},
                                   APIError("cloudflare", "http_401", status=401))
        with self.assertRaises(APIError):
            relay.tick()
        self.assertEqual(sum(c["service"] == "notification" for c in client.calls), 1)

    def test_empty_inbox_does_not_hide_notification_outage(self):
        relay, _ = self.relay({"leads": []}, APIError("notification", "http_503", status=503))
        with self.assertRaises(APIError):
            relay.tick()
        self.assertIsNone(relay.last_success)

    def test_expiration_after_receipt_stops_before_status_read(self):
        relay, client = self.relay(update_ok(), {"id": BOT_ID, "status": "queued"}, update_ok())
        times = iter([100, 100, 100, 100, 100, 100, 100, 100, 220])
        relay.monotonic = lambda: next(times)
        with self.assertRaises(LeaseLost):
            relay.process(lead(), 100)
        self.assertEqual(len(client.calls), 3)

    def test_saved_id_survives_ack_failure_and_never_reposts(self):
        relay, client = self.relay(update_ok(), {"id": BOT_ID, "status": "sent"},
                                   APIError("cloudflare", "unavailable"))
        with self.assertRaises(APIError):
            relay.process(lead(notificationId=BOT_ID), 100)
        self.assertFalse(any(c["service"] == "notification" and c["method"] == "POST" for c in client.calls))

    def test_alerts_are_deduplicated_across_restart_and_contain_no_pii(self):
        relay, _ = self.relay()
        relay.alerts.fault("cloudflare_http_401")
        original = relay.alerts.state["pending"][0]
        restarted = Alerts(self.settings.state_dir / "alerts.json", now=lambda: NOW)
        restarted.fault("cloudflare_http_401")
        self.assertEqual(len(restarted.state["pending"]), 1)
        restarted.recovered()
        self.assertEqual(len(restarted.state["pending"]), 2)
        self.assertEqual(restarted.state["pending"][0], original)
        self.assertNotIn("a@example.test", (self.settings.state_dir / "alerts.json").read_text())

    def test_alert_send_failure_keeps_stable_key(self):
        relay, _ = self.relay()
        relay.alerts.fault("notification_unavailable")
        keys = []

        def fail(payload, key):
            keys.append(key)
            raise APIError("notification", "unavailable")

        relay.alerts.flush(fail)
        relay.alerts.flush(fail)
        self.assertEqual(keys[0], keys[1])
        self.assertEqual(len(relay.alerts.state["pending"]), 1)

    def test_corrupt_alert_state_does_not_reset_deduplication(self):
        path = self.settings.state_dir / "alerts.json"
        path.write_text("broken")
        with self.assertRaises(ValueError):
            Alerts(path)

    def test_attention_alert_survives_crash_after_cloud_terminal_commit(self):
        relay, client = self.relay(update_ok(), {"id": BOT_ID, "status": "failed"}, update_ok())
        original_update = relay.update

        def commit_then_crash(lease, action, **fields):
            result = original_update(lease, action, **fields)
            if action == "attention":
                raise SystemExit("simulated process crash after successful terminal update")
            return result

        with patch.object(relay, "update", side_effect=commit_then_crash):
            with self.assertRaises(SystemExit):
                relay.process(lead(notificationId=BOT_ID), 100)
        self.assertEqual(client.calls[-1]["payload"]["action"], "attention")
        restarted = Alerts(self.settings.state_dir / "alerts.json", now=lambda: NOW)
        self.assertEqual(len(restarted.state["pending"]), 1)
        self.assertEqual(restarted.state["pending"][0]["key"], f"ermolov-attention:{LEAD_ID}:v1")
        self.assertNotIn("a@example.test", (self.settings.state_dir / "alerts.json").read_text())

    def test_attention_update_failure_reuses_durable_warning_on_retry(self):
        relay, _ = self.relay(update_ok(), {"id": BOT_ID, "status": "failed"},
                              APIError("cloudflare", "unavailable"))
        with self.assertRaises(APIError):
            relay.process(lead(notificationId=BOT_ID), 100)
        restarted, _ = self.relay(update_ok(), {"id": BOT_ID, "status": "failed"}, update_ok())
        restarted.process(lead(notificationId=BOT_ID), 100)
        self.assertEqual(len(restarted.alerts.state["pending"]), 1)

    def test_full_alert_queue_does_not_remove_lead_from_recovery_queue(self):
        relay, client = self.relay(update_ok(), {"id": BOT_ID, "status": "failed"})
        for index in range(100):
            relay.alerts.enqueue(f"test alert {index}", "info")
        relay.alerts.save()
        with self.assertRaises(APIError) as caught:
            relay.process(lead(notificationId=BOT_ID), 100)
        self.assertEqual(caught.exception.code, "alert_queue_full")
        self.assertFalse(any(call["payload"] and call["payload"].get("action") == "attention"
                             for call in client.calls))

    def test_attention_persistence_failure_prevents_terminal_cloud_update(self):
        relay, client = self.relay(update_ok(), {"id": BOT_ID, "status": "failed"})
        with patch.object(relay.alerts, "save", side_effect=OSError("simulated disk failure")):
            with self.assertRaises(OSError):
                relay.process(lead(notificationId=BOT_ID), 100)
        self.assertFalse(any(call["payload"] and call["payload"].get("action") == "attention"
                             for call in client.calls))

    def test_health_distinguishes_stale_or_stopped_from_external_outage(self):
        relay, _ = self.relay()
        relay.heartbeat("degraded")
        path = self.settings.state_dir / "health.json"
        self.assertTrue(healthy(path, NOW + 179))
        self.assertFalse(healthy(path, NOW + 181))
        relay.heartbeat("stopped")
        self.assertFalse(healthy(path, NOW))

    def test_settings_do_not_expose_tokens(self):
        self.assertNotIn("r" * 40, repr(self.settings))
        self.assertNotIn("n" * 40, repr(self.settings))


class HTTPTests(unittest.TestCase):
    def test_identifies_relay_with_explicit_honest_user_agent(self):
        client = HTTPClient()
        response = io.BytesIO(b'{"ok":true}')
        with patch.object(client.opener, "open", return_value=response) as opened:
            self.assertEqual(client.request("cloudflare", "GET", "https://ermolov.dev/api/internal/status",
                                            "test-token"), {"ok": True})
        request = opened.call_args.args[0]
        self.assertEqual(request.get_header("User-agent"), USER_AGENT)
        self.assertEqual(USER_AGENT, "ermolov-lead-relay/1.0 (+https://ermolov.dev)")

    def test_redirect_is_not_followed(self):
        self.assertIsNone(NoRedirect().redirect_request(None, None, 302, "", {}, "https://other.test"))

    def test_http_errors_are_redacted_and_retry_header_preserved(self):
        client = HTTPClient()
        private = "private-person@example.test"
        error = HTTPError(f"https://example.test/{private}", 429, private,
                          {"Retry-After": "120"}, io.BytesIO(private.encode()))
        with patch.object(client.opener, "open", side_effect=error):
            with self.assertRaises(APIError) as caught:
                client.request("cloudflare", "POST", "https://example.test", "secret", {})
        self.assertNotIn(private, str(caught.exception))
        self.assertEqual(caught.exception.retry_after, 120)

    def test_network_errors_do_not_expose_credentials(self):
        client = HTTPClient()
        with patch.object(client.opener, "open", side_effect=URLError("secret credential")):
            with self.assertRaises(APIError) as caught:
                client.request("notification", "GET", "http://notification-bot:8080/healthz", "secret")
        self.assertEqual(str(caught.exception), "notification_unavailable")


if __name__ == "__main__":
    unittest.main()
