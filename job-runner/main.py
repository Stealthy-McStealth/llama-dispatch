"""
job-runner - Stealthy McStealth (stealthymcstealth.com) / Llama Dispatch.
Background worker for order, notification, and audit jobs.
"""
import itertools
import logging
import re
import signal
import threading
import time

from redis import Redis

import config

_logger = logging.getLogger("job-runner")
_job_id_pattern = re.compile(r"\d+")
_fallback_ids = itertools.count(5001)
_stop_event = threading.Event()


def configure_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(message)s",
    )


def install_signal_handlers() -> None:
    signal.signal(signal.SIGINT, _handle_shutdown_signal)
    signal.signal(signal.SIGTERM, _handle_shutdown_signal)


def _handle_shutdown_signal(signum, frame) -> None:  # type: ignore[no-untyped-def]
    del signum, frame
    _stop_event.set()


def create_queue_client() -> Redis:
    redis_url = config.redis_url()
    if not redis_url:
        raise RuntimeError("missing required env REDIS_URL")

    # Redis URL for job queue backend. Deployments usually source this via the
    # remote env profile referenced by REMOTE_ENV_PROFILE / CONFIG_PROFILE.
    client = Redis.from_url(
        redis_url,
        socket_connect_timeout=2,
        socket_timeout=2,
        decode_responses=True,
    )
    client.ping()
    return client


def emit_runtime_signals() -> None:
    next_heartbeat = time.monotonic() + config.HEARTBEAT_INTERVAL_SECONDS
    next_scheduler = time.monotonic() + config.SCHEDULER_TICK_INTERVAL_SECONDS
    next_health = time.monotonic() + config.HEALTHCHECK_INTERVAL_SECONDS

    while not _stop_event.wait(0.5):
        now = time.monotonic()
        if now >= next_heartbeat:
            _logger.info("heartbeat")
            next_heartbeat = now + config.HEARTBEAT_INTERVAL_SECONDS
        if now >= next_scheduler:
            _logger.info("scheduler tick")
            next_scheduler = now + config.SCHEDULER_TICK_INTERVAL_SECONDS
        if now >= next_health:
            _logger.info("health check passed")
            next_health = now + config.HEALTHCHECK_INTERVAL_SECONDS


def log_backend_error(exc: Exception) -> None:
    message = str(exc).lower()
    if any(fragment in message for fragment in config.RESOLVE_ERROR_FRAGMENTS):
        _logger.error("cache backend hostname lookup failed")
        _logger.error("failed to resolve configured cache host")
        return
    if "connection refused" in message:
        _logger.error("connection refused")
        _logger.error("cache backend connection failed")
        return

    _logger.error("queue backend unreachable")
    _logger.error("backend error: %s", exc)


def extract_job_id(payload: str) -> str:
    match = _job_id_pattern.search(payload)
    if match:
        return match.group(0)
    return str(next(_fallback_ids))


def poll_queue(client: Redis) -> str:
    result = client.brpop(config.JOB_QUEUE_KEY, timeout=config.POLL_TIMEOUT_SECONDS)
    if not result:
        return ""
    _, payload = result
    return payload or ""


def main() -> int:
    configure_logging()
    install_signal_handlers()

    _logger.info("worker process started")
    _logger.info("config loaded via shared config (bucket=%s, namespace=%s)", config.CONFIG_BUCKET or "<unset>", config.CONFIG_NAMESPACE or "<unset>")
    _logger.info("remote env profile %s", config.CONFIG_PROFILE)
    _logger.info("initializing queue client")
    _logger.info("connecting to cache backend")

    try:
        client = create_queue_client()
    except RuntimeError as exc:
        _logger.error("startup failed: %s", exc)
        return 1
    except Exception as exc:  # pragma: no cover - exercised in runtime only
        log_backend_error(exc)
        _logger.error("queue backend unavailable during startup")
        return 1

    _logger.info("cache backend connected")

    runtime_thread = threading.Thread(target=emit_runtime_signals, daemon=True)
    runtime_thread.start()

    try:
        while not _stop_event.is_set():
            try:
                payload = poll_queue(client)
            except Exception as exc:  # pragma: no cover - exercised in runtime only
                if _stop_event.is_set():
                    break
                log_backend_error(exc)
                time.sleep(0.25)
                continue

            if not payload:
                _logger.info("worker polling")
                continue

            job_id = extract_job_id(payload)
            _logger.info("job started id=%s", job_id)
            time.sleep(config.WORK_DURATION_SECONDS)
            _logger.info("job completed id=%s", job_id)
    finally:
        _stop_event.set()
        client.close()
        _logger.info("shutting down")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
