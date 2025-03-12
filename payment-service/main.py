"""
payment-service - Stealthy McStealth (stealthymcstealth.com) / Llama Dispatch.
Payment checks and order status endpoints used by web-api.
"""
import itertools
import logging
import time

from flask import Flask, g, jsonify, request

import config

app = Flask(__name__)
_request_ids = itertools.count(1000)


def configure_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(message)s",
    )


@app.before_request
def start_request():
    g.started_at = time.perf_counter()
    g.request_id = f"req-{next(_request_ids)}"
    app.logger.info("middleware: request started")


@app.after_request
def complete_request(response):
    duration_ms = synthetic_duration_ms(request.path)
    app.logger.info("middleware: request completed")
    app.logger.info("%s completed", g.request_id)
    app.logger.info("%s %s %s %sms", request.method, request.path, response.status_code, duration_ms)
    return response


@app.route("/health")
def health():
    app.logger.info("health check passed")
    return jsonify({"status": "ok"})


@app.route("/api/orders")
def list_orders():
    limit = request.args.get("limit", default=config.ORDER_STATUS_LIMIT, type=int)
    orders = [
        {"order_id": "ord-5001", "status": "processing"},
        {"order_id": "ord-5002", "status": "queued"},
        {"order_id": "ord-5003", "status": "paid"},
    ]
    return jsonify({"orders": orders[:limit], "source": "postgres"})


@app.route("/checkout", methods=["POST"])
def checkout():
    return jsonify({"result": "accepted", "gateway": config.GATEWAY_BASE_URL or "internal"})


def synthetic_duration_ms(path: str) -> int:
    if path == "/health":
        return 1
    if path == "/checkout":
        return 120
    if path == "/api/orders":
        return 45
    return 32


if __name__ == "__main__":
    configure_logging()
    app.logger.info("server starting")
    app.logger.info("config loaded from env")
    app.logger.info("listening on :%s", config.PORT)
    app.run(host="0.0.0.0", port=config.PORT)
