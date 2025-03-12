# Stealthy McStealth - Llama Dispatch notify-service
import os

SERVICE_NAME = "notify-service"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
PORT = int(os.getenv("PORT", "9090"))
