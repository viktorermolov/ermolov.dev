export class HttpError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
    public fields?: Record<string, string>,
  ) { super(message); }
}

export const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const SERVICES = new Set(['', 'saas', 'ai', 'automation', 'advisory', 'rescue', 'other']);

export interface Lead {
  email: string;
  message: string;
  name: string;
  service: string;
  budget: string;
  timeline: string;
  source: { utmSource: string; utmMedium: string; utmCampaign: string; referrer: string; cta: string };
}
export interface Submission { submissionId: string; lead: Lead; turnstileToken: string; website: string }
export interface BotPayload { title: string; message: string; level: 'info' }

export function object(value: unknown): Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    throw new HttpError(400, 'invalid_request', 'Expected a JSON object.');
  }
  return value as Record<string, unknown>;
}

export function field(value: unknown, name: string, max: number, required = false, multiline = false): string {
  const invalid = () => new HttpError(400, 'validation_error', 'Please check the form.', {
    [name]: required ? `Required; at most ${max} characters.` : `Use at most ${max} characters.`,
  });
  if (value === undefined || value === null) value = '';
  if (typeof value !== 'string' || value.length > max) throw invalid();
  const text = value.trim();
  // Reject unpaired surrogates, which the Telegram renderer cannot encode.
  if ([...text].some(char => {
    const code = char.codePointAt(0)!;
    return code >= 0xd800 && code <= 0xdfff;
  })) throw invalid();
  if ((multiline ? /[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]/ : /[\x00-\x1f\x7f]/).test(text)) throw invalid();
  if (required && !text) throw invalid();
  return text;
}

export async function boundedJson(input: Request | Response, max = 16 * 1024): Promise<unknown> {
  const length = input.headers.get('content-length');
  if (length && Number(length) > max) throw new HttpError(413, 'body_too_large', 'Request is too large.');
  if (!input.body) throw new HttpError(400, 'invalid_json', 'A JSON body is required.');
  const reader = input.body.getReader();
  const chunks: Uint8Array[] = [];
  let size = 0;
  try {
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      size += value.byteLength;
      if (size > max) {
        await reader.cancel();
        throw new HttpError(413, 'body_too_large', 'Request is too large.');
      }
      chunks.push(value);
    }
  } finally { reader.releaseLock(); }
  const bytes = new Uint8Array(size);
  let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.byteLength; }
  try { return JSON.parse(new TextDecoder('utf-8', { fatal: true, ignoreBOM: false }).decode(bytes)); }
  catch { throw new HttpError(400, 'invalid_json', 'Use valid UTF-8 JSON.'); }
}

export function parseSubmission(value: unknown): Submission {
  const raw = object(value);
  const submissionId = field(raw.submissionId, 'submissionId', 36, true).toLowerCase();
  if (!UUID.test(submissionId)) throw new HttpError(400, 'invalid_request', 'Invalid submission identifier.');
  const email = field(raw.email, 'email', 254, true);
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    throw new HttpError(400, 'validation_error', 'Please check the form.', { email: 'Enter a valid email address.' });
  }
  const service = field(raw.service, 'service', 16);
  if (!SERVICES.has(service)) throw new HttpError(400, 'validation_error', 'Choose a listed service.', { service: 'Choose a listed service.' });
  const source = raw.source === undefined ? {} : object(raw.source);
  const referrer = field(source.referrer, 'source.referrer', 120).toLowerCase();
  if (referrer && !/^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$/.test(referrer)) {
    throw new HttpError(400, 'invalid_request', 'Referrer must contain only a hostname.');
  }
  return {
    submissionId,
    turnstileToken: field(raw.turnstileToken, 'turnstileToken', 2048),
    website: field(raw.website, 'website', 200),
    lead: {
      email,
      message: field(raw.message, 'message', 2500, true, true),
      name: field(raw.name, 'name', 80), service,
      budget: field(raw.budget, 'budget', 80),
      timeline: field(raw.timeline, 'timeline', 80),
      source: {
        utmSource: field(source.utmSource, 'source.utmSource', 80),
        utmMedium: field(source.utmMedium, 'source.utmMedium', 80),
        utmCampaign: field(source.utmCampaign, 'source.utmCampaign', 80),
        referrer,
        cta: field(source.cta, 'source.cta', 40),
      },
    },
  };
}

export function botPayload(id: string, lead: Lead): BotPayload {
  const lines = [
    `Inquiry: ${id}`, `Email: ${lead.email}`,
    ...Object.entries({ Name: lead.name, Service: lead.service, Budget: lead.budget, Timeline: lead.timeline })
      .filter(([, value]) => value).map(([label, value]) => `${label}: ${value}`),
    '', lead.message,
  ];
  const attribution = Object.entries(lead.source).filter(([, value]) => value)
    .map(([label, value]) => `${label}: ${value}`);
  if (attribution.length) lines.push('', ...attribution);
  const payload: BotPayload = { title: 'New project inquiry', message: lines.join('\n'), level: 'info' };
  // Mirrors notifications/app.py render() for the fixed ermolov-site source.
  if (`[ermolov-site] INFO — ${payload.title}\n\n${payload.message}`.length > 4096) {
    throw new HttpError(400, 'validation_error', 'Please shorten the message.', { message: 'The full inquiry is too long.' });
  }
  return payload;
}

export async function sha256(text: string): Promise<string> {
  return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text))))
    .map(byte => byte.toString(16).padStart(2, '0')).join('');
}
