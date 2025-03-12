# Llama Dispatch

**Stealthy McStealth** (stealthymcstealth.com) - Llama Dispatch is our internal platform for order-related background work, notifications, and audit activity.

## Services

- **web-api** - request-facing edge service for checkout and order status flows. It calls `payment-service` and triggers async work through `job-runner`.
- **payment-service** - payment checks and order lookups for `web-api`; uses shared Postgres infrastructure.
- **job-runner** - Python background worker for order, notification, and audit jobs. It talks to the queue/cache backend and emits audit events.
- **notify-service** - adjacent background consumer that publishes and acknowledges notification work; noisy during incidents but not usually causal.
- **audit-log** - downstream sink for worker audit events.

## Notes

- Shared infrastructure such as `postgres` and the queue/cache backend are not fully modeled as standalone services in this repo.
