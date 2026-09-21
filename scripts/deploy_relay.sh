#!/usr/bin/env bash
# Deploy only the website relay. Secrets and runtime state never leave the Pi.
set -euo pipefail

LOCAL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
REMOTE_HOST="${REMOTE_HOST:-pi}"
REMOTE_PATH="${REMOTE_PATH:-/data/programming/projects/ermolov.dev}"
COMPOSE_PROJECT=ermolov-site
SERVICE=ermolov-lead-relay

fail() { printf '[relay-deploy] ERROR: %s\n' "$1" >&2; exit 1; }
log() { printf '[relay-deploy] %s\n' "$1"; }
remote() { ssh -n -o BatchMode=yes -o ConnectTimeout=10 "${REMOTE_HOST}" "$1"; }

[[ "${REMOTE_HOST}" =~ ^[a-zA-Z0-9_.@-]+$ && "${REMOTE_HOST}" != -* ]] || fail "unsupported SSH host"
[[ "${REMOTE_PATH}" =~ ^/[a-zA-Z0-9_./-]+$ && "${REMOTE_PATH}" != */../* && "${REMOTE_PATH}" != */.. ]] || fail "unsupported remote path"
[[ "${REMOTE_PATH}" != / ]] || fail "remote path must be a project directory"
[[ -z "$(git -C "${LOCAL_ROOT}" status --porcelain --untracked-files=normal)" ]] || fail "commit or stash local changes before deploy"
[[ "$(git -C "${LOCAL_ROOT}" rev-parse --abbrev-ref HEAD)" != HEAD ]] || fail "detached HEAD is not allowed"

commit="$(git -C "${LOCAL_ROOT}" rev-parse HEAD)"
[[ "${commit}" =~ ^[a-f0-9]{40,64}$ ]] || fail "invalid Git revision"
release="${REMOTE_PATH}/relay-releases/${commit}"
env_file="${REMOTE_PATH}/.env.relay"
image="ermolov-lead-relay:${commit}"
test_image="ermolov-lead-relay-test:${commit}"

# Never read/print credential contents. Refuse broad file permissions and check
# the private bot's readiness before making any deployment changes.
remote "test -f '${env_file}' && test \"\$(stat -c '%a' '${env_file}')\" = 600 && docker network inspect notification-bot --format '{{.Internal}}' | grep -qx true && curl -fsS --max-time 10 http://127.0.0.1:8080/healthz >/dev/null" \
  || fail "private env file (mode 0600), bot network, or Notification Bot readiness is missing"

previous="$(remote "if test -L '${REMOTE_PATH}/relay-current'; then readlink '${REMOTE_PATH}/relay-current'; fi")"
if [[ -n "${previous}" ]]; then
  previous_commit="${previous##*/}"
  [[ "${previous}" == "${REMOTE_PATH}/relay-releases/${previous_commit}" && "${previous_commit}" =~ ^[a-f0-9]{40,64}$ ]] || fail "invalid previous release pointer"
fi

log "Preparing relay commit ${commit}; existing service stays running during tests"
remote "mkdir -p '${release}'"
rsync -az --exclude='.env*' --exclude='state/' --exclude='__pycache__/' \
  --exclude='*.pyc' --exclude='.pytest_cache/' --exclude='.DS_Store' \
  "${LOCAL_ROOT}/services/relay/" "${REMOTE_HOST}:${release}/"

# The Pi needs host networking only while building images. Tests have no network
# and receive no production credentials, host mounts, or runtime data.
remote "docker build --network host --build-arg VCS_REF='${commit}' --target test -t '${test_image}' '${release}'"
remote "docker run --rm --network none '${test_image}' python -m unittest discover -s tests -v"
remote "docker build --network host --build-arg VCS_REF='${commit}' --target runtime -t '${image}' '${release}'"
compose="RELAY_IMAGE='${image}' RELAY_ENV_FILE='${env_file}' docker compose -p '${COMPOSE_PROJECT}' -f '${release}/docker-compose.yml'"
remote "${compose} config --quiet"
# Configuration validation loads only this new service's environment. It does
# not contact either API or print the configured values.
remote "${compose} run --rm --no-deps --entrypoint python '${SERVICE}' -c 'from relay import Settings; Settings.from_env(); print(\"Relay configuration valid\")'"

log "Starting candidate relay"
if ! remote "${compose} up -d --force-recreate --wait --wait-timeout 150 '${SERVICE}'"; then
  if [[ -n "${previous}" && "${previous}" != "${release}" ]]; then
    previous_commit="${previous##*/}"
    log "Candidate unhealthy; restoring previous relay release ${previous_commit}"
    if ! remote "RELAY_IMAGE='ermolov-lead-relay:${previous_commit}' RELAY_ENV_FILE='${env_file}' docker compose -p '${COMPOSE_PROJECT}' -f '${previous}/docker-compose.yml' up -d --force-recreate --wait --wait-timeout 150 '${SERVICE}'"; then
      fail "candidate and rollback failed; inspect this service, preserving its volume and Cloudflare inbox"
    fi
  fi
  fail "candidate failed; previous pointer and all runtime data were preserved"
fi

# Replace the release pointer only after a healthy container exists. No global
# prune, volume deletion, bot recreation, or unrelated Compose operation occurs.
remote "ln -sfn '${release}' '${REMOTE_PATH}/relay-current' && ${compose} ps '${SERVICE}'"
log "Relay deployed. Review redacted Cloudflare /api/internal/status and the controlled end-to-end delivery check."
