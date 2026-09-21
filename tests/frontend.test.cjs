const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { webcrypto } = require('node:crypto');

const app = fs.readFileSync(path.join(__dirname, '../assets/js/app.js'), 'utf8');
const template = fs.readFileSync(path.join(__dirname, '../layouts/index.html'), 'utf8');

// Run the real script against a small DOM boundary, without a browser, provider,
// or live form submission. Network completion is controlled by each scenario.
function fixture() {
  const nodes = new Map();
  let focused = null;
  class Element {
    constructor(tagName, name) {
      this.tagName = tagName.toUpperCase();
      this.name = name;
      this.value = '';
      this.disabled = false;
      this.readOnly = false;
      this.dataset = {};
      this.attributes = new Map();
      this.listeners = new Map();
      this.textContent = '';
      this.validity = { valid: true };
    }
    setAttribute(name, value) { this.attributes.set(name, value); }
    getAttribute(name) { return this.attributes.get(name) ?? null; }
    removeAttribute(name) { this.attributes.delete(name); }
    addEventListener(type, callback) {
      if (!this.listeners.has(type)) this.listeners.set(type, []);
      this.listeners.get(type).push(callback);
    }
    async emit(type) {
      for (const callback of this.listeners.get(type) || []) {
        await callback({ target: this, preventDefault() {} });
      }
    }
    focus() { focused = this; }
    closest(selector) {
      return selector === '.form-context' && ['service', 'budget', 'timeline'].includes(this.name) ? context : null;
    }
  }
  const root = new Element('html');
  const context = new Element('details');
  const form = new Element('form');
  const button = new Element('button');
  const buttonLabel = new Element('span');
  button.querySelector = () => buttonLabel;
  const errors = [];
  form.elements = {};
  for (const match of template.matchAll(/<(input|textarea|select)\b[^>]*name="([^"]+)"[^>]*>/g)) {
    const field = new Element(match[1], match[2]);
    const describedBy = match[0].match(/aria-describedby="([^"]+)"/);
    if (describedBy) field.setAttribute('aria-describedby', describedBy[1]);
    form.elements[match[2]] = field;
  }
  for (const match of template.matchAll(/class="field-error" id="([^"]+)"/g)) {
    const error = new Element('span');
    nodes.set(match[1], error);
    errors.push(error);
  }
  for (const id of ['contact-verification', 'verification-status', 'message-count', 'form-status']) {
    nodes.set(id, new Element('div'));
  }
  nodes.set('contact-form', form);
  const fields = Object.values(form.elements);
  form.querySelector = selector => {
    if (selector === 'button[type=submit]') return button;
    if (selector === '.form-context') return context;
    if (selector === '[aria-invalid=true], :invalid') return fields.find(field => field.getAttribute('aria-invalid') === 'true');
    throw new Error('Unexpected selector: ' + selector);
  };
  form.querySelectorAll = selector => {
    if (selector === '[aria-invalid]') return fields.filter(field => field.getAttribute('aria-invalid'));
    if (selector === '.field-error') return errors;
    if (selector === 'input, textarea, select') return fields;
    throw new Error('Unexpected selector: ' + selector);
  };
  form.checkValidity = () => true;
  form.dataset = { endpoint: '/api/leads', sitekey: 'local-fixture-key' };
  form.elements.email.value = 'Founder+Project@Example.com';
  form.elements.message.value = 'A useful project inquiry.';
  const links = ['hero', 'header', 'service-ai'].map(cta => {
    const link = new Element('a');
    link.dataset.cta = cta;
    if (cta === 'service-ai') link.dataset.service = 'ai';
    link.setAttribute('href', '#contact');
    return link;
  });
  const document = {
    documentElement: root, referrer: 'https://Example.com/a-private-path',
    getElementById: id => nodes.get(id),
    querySelector: () => null,
    querySelectorAll: selector => selector === '[data-cta]' ? links : [],
  };
  let verify;
  let token = 0;
  const requests = [];
  const timers = new Map();
  let timer = 0;
  const window = {
    matchMedia: () => ({ matches: false, addEventListener() {} }),
    location: { search: '?utm_campaign=launch' },
    crypto: webcrypto,
    setTimeout: callback => { timers.set(++timer, callback); return timer; },
    clearTimeout: id => timers.delete(id),
    turnstile: {
      render(_target, options) { verify = options.callback; verify('token-' + ++token); return 'widget'; },
      reset() { verify('token-' + ++token); },
    },
  };
  const sandbox = {
    window, document, localStorage: { getItem: () => null, setItem() {} },
    URL, URLSearchParams, AbortController,
    fetch: (_url, options) => new Promise((resolve, reject) => {
      requests.push({ data: JSON.parse(options.body), resolve, reject });
    }),
  };
  vm.runInNewContext(app, sandbox);
  return {
    form, button, buttonLabel, fields: form.elements, context, links, requests,
    nodes, focus: () => focused,
    submit: () => form.emit('submit'),
    settle: (index, body, status = 200) => requests[index].resolve({ ok: status < 400, status, json: async () => body }),
  };
}
async function tick() { await new Promise(resolve => setImmediate(resolve)); }

test('an ambiguous failure retries the same inquiry and attribution after a different CTA', async () => {
  const f = fixture();
  await f.links[0].emit('click');
  const first = f.submit();
  await tick();
  f.requests[0].reject(new Error('Connection lost after the server may have saved it'));
  await first;
  assert.equal(f.fields.message.value, 'A useful project inquiry.');
  assert.equal(f.fields.email.value, 'Founder+Project@Example.com');
  assert.equal(f.fields.message.readOnly, false);
  assert.equal(f.button.disabled, false);
  await f.links[1].emit('click');
  const retry = f.submit();
  await tick();
  assert.equal(f.requests[1].data.submissionId, f.requests[0].data.submissionId);
  assert.deepEqual(f.requests[1].data.source, f.requests[0].data.source);
  assert.equal(f.requests[1].data.source.cta, 'hero');
  assert.equal(f.requests[1].data.source.referrer, 'example.com');
  assert.equal(f.requests[1].data.email, 'Founder+Project@Example.com');
  f.settle(1, { ok: true, id: f.requests[1].data.submissionId });
  await retry;
  await f.links[1].emit('click');
  await f.submit();
  assert.equal(f.requests.length, 2, 'Already accepted content is not posted again');
  f.fields.message.value += ' An actual change.';
  const edited = f.submit();
  await tick();
  assert.notEqual(f.requests[2].data.submissionId, f.requests[1].data.submissionId);
  assert.equal(f.requests[2].data.source.cta, 'header');
  f.settle(2, { ok: true, id: f.requests[2].data.submissionId });
  await edited;
});

test('an in-flight inquiry locks user-editable fields and restores their original states', async () => {
  const f = fixture();
  f.fields.name.readOnly = true;
  f.fields.budget.disabled = true;
  const sent = f.submit();
  await tick();
  assert.equal(f.fields.email.readOnly, true);
  assert.equal(f.fields.message.readOnly, true);
  assert.equal(f.fields.service.disabled, true);
  assert.equal(f.button.disabled, true);
  await f.links[2].emit('click');
  assert.equal(f.fields.service.value, '', 'Service CTA cannot alter an in-flight snapshot');
  await f.submit();
  assert.equal(f.requests.length, 1, 'Double submission is ignored');
  f.settle(0, { ok: false, error: { code: 'unavailable' } }, 503);
  await sent;
  assert.equal(f.fields.email.readOnly, false);
  assert.equal(f.fields.message.readOnly, false);
  assert.equal(f.fields.service.disabled, false);
  assert.equal(f.fields.name.readOnly, true);
  assert.equal(f.fields.budget.disabled, true);
  assert.equal(f.fields.message.value, 'A useful project inquiry.');
  assert.equal(f.button.disabled, false);
  f.fields.message.value += ' A new detail after the request finishes.';
  const edited = f.submit();
  await tick();
  assert.equal(f.requests[1].data.source.cta, 'direct', 'Busy service CTA cannot change subsequent attribution');
  assert.equal(f.requests[1].data.service, '', 'Busy service CTA cannot mutate the selected service');
  f.settle(1, { ok: true, id: f.requests[1].data.submissionId });
  await edited;
});

test('server errors on optional context expose an associated error and focus the restored field', async () => {
  const f = fixture();
  const sent = f.submit();
  await tick();
  f.settle(0, { ok: false, error: { code: 'validation_error', fields: { service: 'Choose a listed service.' } } }, 400);
  await sent;
  assert.equal(f.context.open, true);
  assert.equal(f.fields.service.disabled, false);
  assert.equal(f.fields.service.getAttribute('aria-invalid'), 'true');
  assert.equal(f.fields.service.getAttribute('aria-describedby'), 'service-error');
  assert.match(f.nodes.get('service-error').textContent, /check this field/i);
  assert.equal(f.focus(), f.fields.service);
  for (const name of ['name', 'budget', 'timeline']) {
    assert.equal(f.fields[name].getAttribute('aria-describedby'), name + '-error');
    assert.ok(f.nodes.has(name + '-error'));
  }
});

test('client validation enforces server email syntax and UTF-16 limits without sending', async () => {
  const f = fixture();
  f.fields.email.value = 'founder@localhost';
  await f.submit();
  assert.equal(f.requests.length, 0);
  assert.equal(f.focus(), f.fields.email);
  f.fields.email.value = 'Founder@Example.com';
  f.fields.message.value = '😀'.repeat(1250) + 'x';
  await f.submit();
  assert.equal(f.requests.length, 0);
  assert.equal(f.focus(), f.fields.message);
  f.fields.message.value = '😀'.repeat(1250);
  const boundary = f.submit();
  await tick();
  assert.equal(f.requests[0].data.message.length, 2500);
  f.settle(0, { ok: true, id: f.requests[0].data.submissionId });
  await boundary;
  f.fields.message.value = 'A message with\u0000a pasted control character';
  await f.submit();
  assert.equal(f.requests.length, 1);
  assert.match(f.nodes.get('message-error').textContent, /control characters/);
});
