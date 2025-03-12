# Stealthy McStealth - Llama Dispatch payment-service
import os

SERVICE_NAME = "payment-service"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/llama_dispatch")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
PORT = int(os.getenv("PORT", "8080"))
ORDER_STATUS_LIMIT = int(os.getenv("ORDER_STATUS_LIMIT", "25"))
GATEWAY_BASE_URL = os.getenv("GATEWAY_BASE_URL", "")
