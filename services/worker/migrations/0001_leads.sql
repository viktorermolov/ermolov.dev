CREATE TABLE leads (
  id TEXT PRIMARY KEY,
  payload_hash TEXT NOT NULL,
  lead_json TEXT,
  bot_payload_json TEXT,
  created_at INTEGER NOT NULL,
  state TEXT NOT NULL DEFAULT 'pending' CHECK (state IN ('pending', 'sent', 'attention', 'resolved')),
  next_attempt_at INTEGER NOT NULL,
  lease_token TEXT,
  lease_expires_at INTEGER,
  first_attempt_at INTEGER,
  notification_id TEXT,
  sent_at INTEGER,
  resolved_at INTEGER,
  error_code TEXT,
  redacted_at INTEGER
);
CREATE INDEX leads_due ON leads(state, next_attempt_at, created_at);
CREATE INDEX leads_sent ON leads(state, sent_at);
CREATE INDEX leads_resolved ON leads(state, resolved_at);
CREATE INDEX leads_created ON leads(created_at);

CREATE TABLE daily_admissions (
  day TEXT PRIMARY KEY,
  accepted INTEGER NOT NULL CHECK (accepted >= 0 AND accepted <= 100)
);
CREATE TABLE service_state (
  singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
  unresolved INTEGER NOT NULL DEFAULT 0 CHECK (unresolved >= 0 AND unresolved <= 1000),
  last_poll_at INTEGER
);
INSERT INTO service_state(singleton, unresolved) VALUES (1, 0);

-- Operator-only resolution is one atomic statement, without a D1 BEGIN command.
-- Normal pending -> sent is accounted for by the Worker's delivery transaction.
CREATE TRIGGER account_operator_resolution
AFTER UPDATE OF state ON leads
WHEN NEW.state = 'resolved' AND OLD.state IN ('pending', 'attention')
BEGIN
  UPDATE service_state SET unresolved = unresolved - 1 WHERE singleton = 1;
END;
