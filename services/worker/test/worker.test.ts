import { env } from 'cloudflare:workers';
import { applyD1Migrations, reset } from 'cloudflare:test';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import worker, { cleanup } from '../src/index';
import { botPayload, parseSubmission } from '../src/validation';

interface Claimed {
  id: string; leaseToken: string; notificationId: string | null;
  firstAttemptAt: string; leaseExpiresAt: string;
  payload: { title: string; message: string; level: string };
}
const testEnv: Env = { ...env, LEAD_RATE_LIMITER: { limit: async () => ({ success: true }) } };
function form(extra: Record<string, unknown> = {}) {
  return { submissionId: crypto.randomUUID(), name: 'Alex', email: 'alex@example.com',
    message: 'I need help with a product integration.', service: 'automation',
    turnstileToken: 'test-token', ...extra };
}
function request(path: string, body?: unknown, internal = false, headers: Record<string, string> = {}): Request {
  return new Request(`https://ermolov.dev${path}`, {
    method: body === undefined ? 'GET' : 'POST',
    headers: { 'Content-Type': 'application/json', Origin: 'https://ermolov.dev',
      ...(internal ? { Authorization: `Bearer ${env.RELAY_TOKEN}` } : {}), ...headers },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  });
}
async function submit(body = form()) { return worker.fetch(request('/api/leads', body), testEnv); }
async function claim(): Promise<Claimed[]> {
  const response = await worker.fetch(request('/api/internal/leads/claim', {}, true), testEnv);
  expect(response.status).toBe(200);
  return (await response.json<{ leads: Claimed[] }>()).leads;
}
async function update(lead: Claimed, action: string, extra = {}) {
  return worker.fetch(request(`/api/internal/leads/${lead.id}/update`, { leaseToken: lead.leaseToken, action, ...extra }, true), testEnv);
}
async function due(id: string) {
  await env.DB.prepare('UPDATE leads SET next_attempt_at=?,lease_expires_at=? WHERE id=?').bind(Date.now() - 1, Date.now() - 1, id).run();
}
beforeEach(async () => {
  await applyD1Migrations(env.DB, env.TEST_MIGRATIONS);
  vi.spyOn(globalThis, 'fetch').mockImplementation(async () => Response.json({ success: true, hostname: 'ermolov.dev', action: 'contact' }));
});
afterEach(async () => { vi.restoreAllMocks(); await reset(); });

describe('public intake', () => {
  it('stores the immutable payload before accepting and deduplicates a used challenge', async () => {
    const data = form();
    expect((await submit(data)).status).toBe(202);
    vi.mocked(fetch).mockRejectedValue(new Error('already-used'));
    expect((await submit({ ...data, turnstileToken: '' })).status).toBe(200);
    expect(fetch).toHaveBeenCalledTimes(1);
    const leads = await claim();
    expect(leads).toHaveLength(1);
    expect(leads[0].payload.message).toContain('alex@example.com');
    expect(leads[0].firstAttemptAt).toMatch(/Z$/);
    expect(await env.DB.prepare('SELECT accepted FROM daily_admissions').first('accepted')).toBe(1);
  });

  it('rejects changed content under an existing UUID', async () => {
    const data = form(); await submit(data);
    const response = await submit({ ...data, message: 'Different request' });
    expect(response.status).toBe(409);
    expect(await response.json()).toMatchObject({ error: { code: 'submission_conflict' } });
  });

  it('deduplicates concurrent submissions without consuming the quota twice', async () => {
    const data = form();
    const results = await Promise.all([submit(data), submit(data)]);
    expect(results.map(response => response.status).sort()).toEqual([200, 202]);
    expect(await env.DB.prepare('SELECT accepted FROM daily_admissions').first('accepted')).toBe(1);
    expect(await env.DB.prepare('SELECT unresolved FROM service_state').first('unresolved')).toBe(1);
  });

  it('fails honestly without storing an inquiry when Siteverify is unavailable', async () => {
    vi.mocked(fetch).mockRejectedValue(new Error('network unavailable'));
    const response = await submit();
    expect(response.status).toBe(503);
    expect(await response.json()).toMatchObject({ error: { code: 'challenge_unavailable' } });
    expect(await env.DB.prepare('SELECT COUNT(*) AS n FROM leads').first('n')).toBe(0);
  });

  it.each([
    { success: false }, { success: true, hostname: 'evil.example', action: 'contact' },
    { success: true, hostname: 'ermolov.dev', action: 'login' },
  ])('does not write any rows for invalid Turnstile: %j', async result => {
    vi.mocked(fetch).mockResolvedValue(Response.json(result));
    expect((await submit()).status).toBe(400);
    expect(await env.DB.prepare('SELECT COUNT(*) AS n FROM leads').first('n')).toBe(0);
    expect(await env.DB.prepare('SELECT COUNT(*) AS n FROM daily_admissions').first('n')).toBe(0);
  });

  it('keeps validation retry keys stable for a token and changes them for a new token', async () => {
    const data = form();
    vi.mocked(fetch).mockResolvedValue(Response.json({ success: false }));
    await submit(data); await submit(data); await submit({ ...data, turnstileToken: 'fresh' });
    const keys = vi.mocked(fetch).mock.calls.map(([, init]) => JSON.parse(String(init?.body)).idempotency_key);
    expect(keys[0]).toBe(keys[1]); expect(keys[2]).not.toBe(keys[0]);
  });

  it('does not write honeypots or accept forbidden origins/rate-limited requests', async () => {
    expect((await submit(form({ website: 'spam' }))).status).toBe(202);
    expect(await env.DB.prepare('SELECT COUNT(*) AS n FROM leads').first('n')).toBe(0);
    expect((await worker.fetch(request('/api/leads', form(), false, { Origin: 'https://evil.example' }), testEnv)).status).toBe(403);
    expect((await worker.fetch(request('/api/leads', form()), { ...testEnv,
      LEAD_RATE_LIMITER: { limit: async () => ({ success: false }) } })).status).toBe(429);
    expect(fetch).not.toHaveBeenCalled();
  });

  it('enforces streamed byte bounds even without a content-length header', async () => {
    const bytes = new TextEncoder().encode(JSON.stringify(form({ message: 'x'.repeat(17000) })));
    const response = await worker.fetch(new Request('https://ermolov.dev/api/leads', {
      method: 'POST', headers: { Origin: 'https://ermolov.dev', 'Content-Type': 'application/json' },
      body: new ReadableStream({ start(controller) { controller.enqueue(bytes.slice(0, 8000)); controller.enqueue(bytes.slice(8000)); controller.close(); } }),
    }), testEnv);
    expect(response.status).toBe(413); expect(fetch).not.toHaveBeenCalled();
  });

  it('atomically admits only one contender at the daily cap', async () => {
    await env.DB.prepare('INSERT INTO daily_admissions(day,accepted) VALUES(?,99)').bind(new Date().toISOString().slice(0, 10)).run();
    const results = await Promise.all([submit(), submit(), submit()]);
    expect(results.map(r => r.status).sort()).toEqual([202, 503, 503]);
    expect(await env.DB.prepare('SELECT COUNT(*) AS n FROM leads').first('n')).toBe(1);
    expect(await env.DB.prepare('SELECT unresolved FROM service_state').first('unresolved')).toBe(1);
  });

  it('rolls back admission when the unresolved cap is reached', async () => {
    await env.DB.prepare('UPDATE service_state SET unresolved=1000').run();
    expect((await submit()).status).toBe(503);
    expect(await env.DB.prepare('SELECT COUNT(*) AS n FROM leads').first('n')).toBe(0);
    expect(await env.DB.prepare('SELECT COUNT(*) AS n FROM daily_admissions').first('n')).toBe(0);
  });

  it('accepts the maximum complete Unicode payload within the bot renderer limit', () => {
    const data = form({ name: 'x'.repeat(80), email: `${'x'.repeat(240)}@example.com`, message: '😀'.repeat(1250),
      budget: 'x'.repeat(80), timeline: 'x'.repeat(80), source: { utmSource: 'x'.repeat(80),
        utmMedium: 'x'.repeat(80), utmCampaign: 'x'.repeat(80), referrer: 'x'.repeat(120), cta: 'x'.repeat(40) } });
    const { lead, submissionId } = parseSubmission(data);
    const payload = botPayload(submissionId, lead);
    expect(`[ermolov-site] INFO — ${payload.title}\n\n${payload.message}`.length).toBeLessThanOrEqual(4096);
    expect(() => parseSubmission(form({ message: '\ud800' }))).toThrow();
    expect(() => parseSubmission(form({ message: 'x'.repeat(2501) }))).toThrow();
  });
});

describe('durable delivery', () => {
  it('authenticates every private endpoint', async () => {
    for (const path of ['/api/internal/status', '/api/internal/leads/claim']) {
      expect((await worker.fetch(request(path, {}), testEnv)).status).toBe(401);
    }
  });

  it('leases distinct batches concurrently and fences the old owner after expiry', async () => {
    for (let i = 0; i < 6; i++) await submit();
    const [a, b] = await Promise.all([claim(), claim()]);
    expect(new Set([...a, ...b].map(lead => lead.id)).size).toBe(6);
    expect(a.length + b.length).toBe(6);
    const old = [...a, ...b][0]; await due(old.id);
    const [fresh] = await claim();
    expect(fresh.id).toBe(old.id); expect(fresh.leaseToken).not.toBe(old.leaseToken);
    expect((await update(old, 'progress')).status).toBe(409);
    expect((await update(fresh, 'progress')).status).toBe(200);
  });

  it('persists the bot ID through retry and acknowledges sent only once', async () => {
    await submit(); const [lead] = await claim();
    expect((await update(lead, 'progress', { notificationId: 'bot-123' })).status).toBe(200);
    expect((await update(lead, 'retry', { delaySeconds: 60 })).status).toBe(200);
    expect(await claim()).toHaveLength(0);
    await due(lead.id); const [again] = await claim();
    expect(again.notificationId).toBe('bot-123'); expect(again.payload).toEqual(lead.payload);
    expect(again.firstAttemptAt).toBe(lead.firstAttemptAt);
    expect((await update(again, 'sent')).status).toBe(400);
    expect((await update(again, 'sent', { notificationId: 'different' })).status).toBe(409);
    expect((await update(again, 'sent', { notificationId: 'bot-123' })).status).toBe(200);
    expect((await update(again, 'sent', { notificationId: 'bot-123' })).status).toBe(200);
    expect(await env.DB.prepare('SELECT unresolved FROM service_state').first('unresolved')).toBe(0);
    expect(await claim()).toHaveLength(0);
  });

  it('keeps failed inquiries for attention without automatic resend', async () => {
    await submit(); const [lead] = await claim();
    expect((await update(lead, 'attention', { notificationId: 'bot-failed', errorCode: 'bot_failed' })).status).toBe(200);
    await due(lead.id); expect(await claim()).toHaveLength(0);
    expect(await env.DB.prepare('SELECT lead_json FROM leads WHERE id=?').bind(lead.id).first('lead_json')).toContain('alex@example.com');
    expect(await env.DB.prepare('SELECT unresolved FROM service_state').first('unresolved')).toBe(1);
  });

  it('does not change an already stored notification ID', async () => {
    await submit(); const [lead] = await claim();
    expect((await update(lead, 'progress', { notificationId: 'first-id' })).status).toBe(200);
    expect((await update(lead, 'progress', { notificationId: 'second-id' })).status).toBe(409);
    expect(await env.DB.prepare('SELECT notification_id FROM leads WHERE id=?').bind(lead.id).first('notification_id')).toBe('first-id');
  });

  it('redacts delivered PII at30 days, retains dedup until90, never deletes unresolved', async () => {
    const data = form(); await submit(data); const [lead] = await claim();
    await update(lead, 'sent', { notificationId: 'bot-sent' });
    await submit();
    const now = Date.now();
    await env.DB.prepare('UPDATE leads SET sent_at=? WHERE id=?').bind(now - 31 * 86400000, lead.id).run();
    await cleanup(testEnv, now);
    expect(await env.DB.prepare('SELECT lead_json FROM leads WHERE id=?').bind(lead.id).first('lead_json')).toBeNull();
    expect((await submit({ ...data, turnstileToken: '' })).status).toBe(200);
    await cleanup(testEnv, now + 61 * 86400000);
    expect(await env.DB.prepare('SELECT COUNT(*) AS n FROM leads').first('n')).toBe(1);
  });

  it('reports redacted status without exposing inquiry contents', async () => {
    await submit(); await claim();
    const response = await worker.fetch(request('/api/internal/status', undefined, true), testEnv);
    const text = await response.text();
    expect(text).toContain('"pending":1'); expect(text).not.toContain('alex@example.com');
    expect(JSON.parse(text).lastPoll).toMatch(/Z$/);
  });

  it('resolves attention atomically through the operator trigger and retains dedup', async () => {
    const data = form(); await submit(data); const [lead] = await claim();
    await update(lead, 'attention', { errorCode: 'notification_failed' });
    const resolvedAt = Date.now() - 31 * 86400000;
    const resolve = () => env.DB.prepare("UPDATE leads SET state='resolved',resolved_at=? WHERE id=? AND state='attention'")
      .bind(resolvedAt, lead.id).run();
    await resolve(); await resolve();
    expect(await env.DB.prepare('SELECT unresolved FROM service_state').first('unresolved')).toBe(0);
    expect(await claim()).toHaveLength(0);
    await cleanup(testEnv);
    expect(await env.DB.prepare('SELECT lead_json FROM leads WHERE id=?').bind(lead.id).first('lead_json')).toBeNull();
    expect((await submit({ ...data, turnstileToken: '' })).status).toBe(200);
  });
});
