FROM python:3.13-slim AS runtime
ARG VCS_REF=unknown
LABEL org.opencontainers.image.title="ermolov.dev lead relay"
LABEL org.opencontainers.image.revision=$VCS_REF
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
RUN groupadd --gid 10001 relay && useradd --uid 10001 --gid relay --no-create-home relay \
    && mkdir /app/state && chown relay:relay /app/state && chmod 700 /app/state
COPY --chown=relay:relay relay.py healthcheck.py ./
USER 10001:10001
CMD ["python", "relay.py"]

FROM runtime AS test
COPY --chown=relay:relay tests/ tests/
CMD ["python", "-m", "unittest", "discover", "-s", "tests", "-v"]
