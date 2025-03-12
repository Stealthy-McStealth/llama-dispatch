"""
notify-service - Stealthy McStealth (stealthymcstealth.com) / Llama Dispatch.
Background notification publisher/consumer that creates adjacent incident noise.
"""
import logging

from flask import Flask, jsonify

import config

app = Flask(__name__)


def configure_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(message)s",
    )


@app.route("/health")
def health():
    app.logger.info("health check passed")
    return jsonify({"status": "ok"})


@app.route("/publish", methods=["POST"])
def publish():
    app.logger.info("message published")
    return jsonify({"result": "published"})


@app.route("/consume", methods=["POST"])
def consume():
    app.logger.info("consumer acknowledged")
    return jsonify({"result": "acknowledged"})


@app.route("/batch", methods=["POST"])
def batch():
    app.logger.info("batch processed")
    return jsonify({"result": "processed"})


if __name__ == "__main__":
    configure_logging()
    app.logger.info("server starting")
    app.logger.info("listening on :%s", config.PORT)
    app.run(host="0.0.0.0", port=config.PORT)
