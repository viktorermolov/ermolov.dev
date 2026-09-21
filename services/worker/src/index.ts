import { boundedJson, botPayload, field, HttpError, object, parseSubmission, sha256, UUID } from './validation';
import type { BotPayload } from './validation';

const SECOND = 1000;
const DAY = 86_400_000;
const LEASE = 120 * SECOND;
type Database = D1DatabaseSession;
interface LeadRow {
  id: string; payload_hash: string; state: 'pending' | 'sent' | 'attention' | 'resolved';
  bot_payload_json: string | null; notification_id: string | null;
  lease_token: string | null; lease_expires_at: number | null;
  first_attempt_at: number | null;
}
interface ClaimedRow {
  id: string; bot_payload_json: string; notification_id: string | null;
  first_attempt_at: number; lease_expires_at: number;
}

function json(data: unknown, status = 200, origin?: string): Response {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store',
    'X-Content-Type-Options': 'nosniff',
  };
  if (origin) {
    headers['Access-Control-Allow-Origin'] = origin;
    headers.Vary = 'Origin';
  }
  if (status === 429) headers['Retry-After'] = '60';
  if (status === 503) headers['Retry-After'] = '300';
  return new Response(JSON.stringify(data), { status, headers });
}

function iso(value: number | null): string | null { return value === null ? null : new Date(value).toISOString(); }
function db(env: Env): Database { return env.DB.withSession('first-primary'); }
function requireJson(request: Request): void {
  if (request.headers.get('content-type')?.split(';')[0].trim().toLowerCase() !== 'application/json') {
    throw new HttpError(415, 'unsupported_media_type', 'Use application/json.');
  }
}

async function authorized(request: Request, env: Env): Promise<boolean> {
  const token = request.headers.get('authorization') ?? '';
  if (!env.RELAY_TOKEN || env.RELAY_TOKEN.length < 32 || token.length > 1024) return false;
  const encoder = new TextEncoder();
  const [actual, expected] = await Promise.all([
    crypto.subtle.digest('SHA-256', encoder.encode(token)),
    crypto.subtle.digest('SHA-256', encoder.encode(`Bearer ${env.RELAY_TOKEN}`)),
  ]);
  return crypto.subtle.timingSafeEqual(actual, expected);
}

async function verifyTurnstile(request: Request, env: Env, id: string, hash: string, token: string): Promise<void> {
  if (!token) throw new HttpError(400, 'challenge_required', 'Please complete the spam check.');
  if (!env.TURNSTILE_SECRET_KEY) throw new HttpError(503, 'unavailable', 'The form is temporarily unavailable. Please email instead.');
  const digest = await sha256(`${id}:${hash}:${token}`);
  // UUIDv8: a stable key for retrying this exact validation, distinct for a new token.
  const key = `${digest.slice(0, 8)}-${digest.slice(8, 12)}-8${digest.slice(13, 16)}-a${digest.slice(17, 20)}-${digest.slice(20, 32)}`;
  let result: Record<string, unknown>;
  try {
    const response = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ secret: env.TURNSTILE_SECRET_KEY, response: token,
        remoteip: request.headers.get('CF-Connecting-IP') ?? undefined, idempotency_key: key }),
      signal: AbortSignal.timeout(8000),
    });
    if (!response.ok) throw new Error('upstream');
    result = object(await boundedJson(response));
  } catch {
    throw new HttpError(503, 'challenge_unavailable', 'The spam check is temporarily unavailable. Please try again.');
  }
  if (result.success !== true || result.action !== 'contact' ||
      typeof result.hostname !== 'string' || !env.TURNSTILE_HOSTNAMES.split(',').includes(result.hostname)) {
    throw new HttpError(400, 'challenge_failed', 'Please refresh the spam check and try again.');
  }
}

async function submit(request: Request, env: Env): Promise<Response> {
  const origin = request.headers.get('origin');
  if (!origin || !env.ALLOWED_ORIGINS.split(',').includes(origin)) {
    throw new HttpError(403, 'origin_forbidden', 'This origin is not allowed.');
  }
  requireJson(request);
  const input = parseSubmission(await boundedJson(request));
  const limit = await env.LEAD_RATE_LIMITER.limit({ key: request.headers.get('CF-Connecting-IP') ?? 'unknown' });
  if (!limit.success) throw new HttpError(429, 'rate_limited', 'Please wait a minute before trying again.');
  if (input.website) return json({ ok: true, id: input.submissionId }, 202, origin);

  const database = db(env);
  const canonical = JSON.stringify(input.lead);
  const hash = await sha256(canonical);
  const replay = async (): Promise<boolean> => {
    const row = await database.prepare('SELECT payload_hash FROM leads WHERE id = ?').bind(input.submissionId)
      .first<{ payload_hash: string }>();
    if (!row) return false;
    if (row.payload_hash !== hash) throw new HttpError(409, 'submission_conflict', 'This submission identifier was already used.');
    return true;
  };
  if (await replay()) return json({ ok: true, id: input.submissionId }, 200, origin);
  const payload = botPayload(input.submissionId, input.lead);
  await verifyTurnstile(request, env, input.submissionId, hash, input.turnstileToken);
  const now = Date.now();
  const day = new Date(now).toISOString().slice(0, 10);
  try {
    // All changes, including quotas, roll back on duplicate UUID or capacity failure.
    await database.batch([
      database.prepare(`INSERT INTO leads(id,payload_hash,lead_json,bot_payload_json,created_at,next_attempt_at)
        VALUES(?,?,?,?,?,?)`).bind(input.submissionId, hash, canonical, JSON.stringify(payload), now, now),
      database.prepare(`INSERT INTO daily_admissions(day,accepted) VALUES(?,1)
        ON CONFLICT(day) DO UPDATE SET accepted=accepted+1`).bind(day),
      database.prepare('UPDATE service_state SET unresolved=unresolved+1 WHERE singleton=1'),
    ]);
  } catch (error) {
    if (await replay()) return json({ ok: true, id: input.submissionId }, 200, origin);
    if (error instanceof Error && /CHECK constraint failed/.test(error.message)) {
      throw new HttpError(503, 'capacity_reached', 'The form is temporarily full. Please email instead.');
    }
    throw error;
  }
  console.log({ event: 'lead_accepted' });
  return json({ ok: true, id: input.submissionId }, 202, origin);
}

async function claim(env: Env): Promise<Response> {
  const database = db(env);
  const now = Date.now();
  const token = crypto.randomUUID();
  const result = await database.batch<ClaimedRow>([
    database.prepare('UPDATE service_state SET last_poll_at=? WHERE singleton=1').bind(now),
    database.prepare(`UPDATE leads SET lease_token=?,lease_expires_at=?,next_attempt_at=?,
      first_attempt_at=COALESCE(first_attempt_at,?)
      WHERE id IN (SELECT id FROM leads WHERE state='pending' AND next_attempt_at<=?
        ORDER BY next_attempt_at,created_at LIMIT 5)
      RETURNING id,bot_payload_json,notification_id,first_attempt_at,lease_expires_at`)
      .bind(token, now + LEASE, now + LEASE, now, now),
  ]);
  return json({ leads: result[1].results.map(row => ({
    id: row.id, leaseToken: token, payload: JSON.parse(row.bot_payload_json) as BotPayload,
    notificationId: row.notification_id, firstAttemptAt: iso(row.first_attempt_at),
    leaseExpiresAt: iso(row.lease_expires_at),
  })) });
}

async function update(request: Request, env: Env, id: string): Promise<Response> {
  requireJson(request);
  const body = object(await boundedJson(request));
  const token = field(body.leaseToken, 'leaseToken', 36, true);
  if (!UUID.test(token)) throw new HttpError(400, 'invalid_request', 'Invalid lease token.');
  const action = field(body.action, 'action', 16, true);
  if (!['progress', 'sent', 'retry', 'attention'].includes(action)) throw new HttpError(400, 'invalid_request', 'Unknown action.');
  const notification = field(body.notificationId, 'notificationId', 128) || null;
  if (notification && !/^[a-zA-Z0-9_-]+$/.test(notification)) throw new HttpError(400, 'invalid_request', 'Invalid notification identifier.');
  const code = field(body.errorCode, 'errorCode', 64) || null;
  if (code && !/^[a-z0-9_:-]+$/i.test(code)) throw new HttpError(400, 'invalid_request', 'Use a non-sensitive error code.');
  const delay = body.delaySeconds ?? 60;
  if (typeof delay !== 'number' || !Number.isInteger(delay) || delay < 1 || delay > 86400) {
    throw new HttpError(400, 'invalid_request', 'Retry delay must be 1–86400 seconds.');
  }
  const database = db(env);
  const row = await database.prepare(`SELECT id,state,lease_token,lease_expires_at,notification_id
    FROM leads WHERE id=?`).bind(id).first<LeadRow>();
  if (!row) throw new HttpError(404, 'not_found', 'Inquiry not found.');
  if (action === 'sent' && !notification) throw new HttpError(400, 'invalid_request', 'notificationId is required for sent.');
  if (notification && row.notification_id && notification !== row.notification_id) {
    throw new HttpError(409, 'notification_conflict', 'Notification identifier cannot change.');
  }
  if (action === 'sent' && row.state === 'sent' && row.lease_token === token && row.notification_id === notification) {
    return json({ ok: true, id });
  }
  const now = Date.now();
  if (row.state !== 'pending' || row.lease_token !== token || (row.lease_expires_at ?? 0) <= now) {
    throw new HttpError(409, 'lease_conflict', 'The lease is no longer valid.');
  }
  const guard = "id=? AND state='pending' AND lease_token=? AND lease_expires_at>? AND (notification_id IS NULL OR notification_id=?)";
  const expectedNotification = notification ?? row.notification_id;
  let changed: D1Result;
  if (action === 'sent') {
    const results = await database.batch([
      database.prepare(`UPDATE service_state SET unresolved=unresolved-1 WHERE singleton=1
        AND EXISTS(SELECT 1 FROM leads WHERE ${guard})`).bind(id, token, now, expectedNotification),
      database.prepare(`UPDATE leads SET state='sent',notification_id=?,sent_at=?,error_code=NULL
        WHERE ${guard}`).bind(notification, now, id, token, now, expectedNotification),
    ]);
    changed = results[1];
  } else if (action === 'progress') {
    changed = await database.prepare(`UPDATE leads SET notification_id=COALESCE(?,notification_id),
      lease_expires_at=?,next_attempt_at=? WHERE ${guard}`)
      .bind(notification, now + LEASE, now + LEASE, id, token, now, expectedNotification).run();
  } else {
    changed = await database.prepare(`UPDATE leads SET state=?,notification_id=COALESCE(?,notification_id),
      next_attempt_at=?,lease_token=NULL,lease_expires_at=NULL,error_code=? WHERE ${guard}`)
      .bind(action === 'attention' ? 'attention' : 'pending', notification, now + delay * SECOND, code, id, token, now, expectedNotification).run();
  }
  if (changed.meta.changes !== 1) throw new HttpError(409, 'lease_conflict', 'The lease is no longer valid.');
  if (action === 'sent' || action === 'attention') console.log({ event: `lead_${action}`, code });
  return json({ ok: true, id, ...(action === 'progress' ? { leaseExpiresAt: iso(now + LEASE) } : {}) });
}

async function status(env: Env): Promise<Response> {
  const database = db(env);
  const [counts, service, oldest] = await database.batch<{
    state?: 'pending' | 'sent' | 'attention' | 'resolved'; count?: number;
    last_poll_at?: number | null; oldest?: number | null;
  }>([
    database.prepare('SELECT state,COUNT(*) AS count FROM leads GROUP BY state'),
    database.prepare('SELECT last_poll_at FROM service_state WHERE singleton=1'),
    database.prepare("SELECT MIN(created_at) AS oldest FROM leads WHERE state='pending'"),
  ]);
  const totals = { pending: 0, sent: 0, attention: 0, resolved: 0 };
  for (const row of counts.results) {
    if (row.state === 'pending' || row.state === 'sent' || row.state === 'attention' || row.state === 'resolved') totals[row.state] = Number(row.count);
  }
  return json({ ok: true, counts: totals,
    lastPoll: iso(service.results[0]?.last_poll_at ?? null),
    oldestPending: iso(oldest.results[0]?.oldest ?? null),
  });
}

export async function cleanup(env: Env, now = Date.now()): Promise<void> {
  const database = db(env);
  await database.batch([
    database.prepare(`UPDATE leads SET lead_json=NULL,bot_payload_json=NULL,redacted_at=?
      WHERE id IN(SELECT id FROM leads WHERE redacted_at IS NULL AND
        ((state='sent' AND sent_at<?) OR (state='resolved' AND resolved_at<?)) LIMIT 100)`)
      .bind(now, now - 30 * DAY, now - 30 * DAY),
    database.prepare(`DELETE FROM leads WHERE id IN(SELECT id FROM leads WHERE
      (state='sent' AND sent_at<?) OR (state='resolved' AND resolved_at<?) LIMIT 100)`)
      .bind(now - 90 * DAY, now - 90 * DAY),
    database.prepare('DELETE FROM daily_admissions WHERE day IN(SELECT day FROM daily_admissions WHERE day<? LIMIT 100)')
      .bind(new Date(now - 90 * DAY).toISOString().slice(0, 10)),
  ]);
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const path = new URL(request.url).pathname;
    const origin = request.headers.get('origin') ?? '';
    const allowedOrigin = path === '/api/leads' && env.ALLOWED_ORIGINS.split(',').includes(origin) ? origin : undefined;
    try {
      if (path === '/api/leads') {
        if (request.method === 'OPTIONS') {
          if (!allowedOrigin) throw new HttpError(403, 'origin_forbidden', 'This origin is not allowed.');
          return new Response(null, { status: 204, headers: {
            'Access-Control-Allow-Origin': allowedOrigin, 'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type', 'Access-Control-Max-Age': '600',
            Vary: 'Origin', 'Cache-Control': 'no-store',
          } });
        }
        if (request.method !== 'POST') throw new HttpError(405, 'method_not_allowed', 'Use POST.');
        return await submit(request, env);
      }
      if (path.startsWith('/api/internal/')) {
        if (!(await authorized(request, env))) throw new HttpError(401, 'unauthorized', 'Authentication required.');
        if (path === '/api/internal/status' && request.method === 'GET') return await status(env);
        if (path === '/api/internal/leads/claim' && request.method === 'POST') return await claim(env);
        const match = path.match(/^\/api\/internal\/leads\/([^/]+)\/update$/);
        if (match && UUID.test(match[1]) && request.method === 'POST') return await update(request, env, match[1].toLowerCase());
      }
      throw new HttpError(404, 'not_found', 'Endpoint not found.');
    } catch (error) {
      if (error instanceof HttpError) return json({ ok: false, error: {
        code: error.code, message: error.message, ...(error.fields ? { fields: error.fields } : {}),
      } }, error.status, allowedOrigin);
      // Never emit database errors, request contents, tokens, or email addresses.
      console.error({ event: 'worker_error', code: 'unavailable' });
      return json({ ok: false, error: { code: 'unavailable', message: 'The form is temporarily unavailable. Please email instead.' } }, 503, allowedOrigin);
    }
  },
  async scheduled(_controller, env): Promise<void> { await cleanup(env); },
} satisfies ExportedHandler<Env>;
