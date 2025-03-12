"""
Environment-derived settings for the Llama Dispatch job-runner.

Runtime config is resolved via Stealthy McStealth shared config: bucket and
namespace are read from the environment, and the shared library returns the
default config for this namespace (including REDIS_URL for the job queue backend).
"""
from __future__ import annotations

import os

from stealthy import get_runtime_config

SERVICE_NAME = "job-runner"

# Bucket and namespace come from the shared config library (set at deploy time).
CONFIG_BUCKET = os.environ.get("CONFIG_BUCKET")
CONFIG_NAMESPACE = os.environ.get("CONFIG_NAMESPACE")

# Runtime config for this service from the shared store (blackbox).
_runtime = get_runtime_config(SERVICE_NAME, bucket=CONFIG_BUCKET, namespace=CONFIG_NAMESPACE)

REDIS_URL = _runtime["REDIS_URL"]
LOG_LEVEL = _runtime["LOG_LEVEL"]
JOB_QUEUE_KEY = _runtime["JOB_QUEUE_KEY"]
AUDIT_LOG_TOPIC = _runtime["AUDIT_LOG_TOPIC"]
POLL_TIMEOUT_SECONDS = _runtime["POLL_TIMEOUT_SECONDS"]
WORK_DURATION_SECONDS = _runtime["WORK_DURATION_SECONDS"]
HEARTBEAT_INTERVAL_SECONDS = _runtime["HEARTBEAT_INTERVAL_SECONDS"]
SCHEDULER_TICK_INTERVAL_SECONDS = _runtime["SCHEDULER_TICK_INTERVAL_SECONDS"]
HEALTHCHECK_INTERVAL_SECONDS = _runtime["HEALTHCHECK_INTERVAL_SECONDS"]


def redis_url() -> str:
    """Redis URL for job queue backend. Sourced from shared config for this namespace."""
    return REDIS_URL
