# Backend event contract

The backend should publish signed events to `POST /integrations/backend/events`.

Envelope:
```json
{
  "id": "evt_123",
  "type": "order.status_changed",
  "occurred_at": "2026-09-16T12:00:00Z",
  "user_id": "12345",
  "payload": {
    "order_id": "ORD-1",
    "status": "in_transit"
  }
}
```

Supported events:
- order.created
- order.status_changed
- delivery.status_changed
- payment.completed
- subscription.paid
- user.status_changed
- team.member_joined
- team.member_status_changed
- cooperation.application_created
- wallet.operation_created

The event ID is persisted before notification processing, preventing duplicate Telegram notifications after webhook retries.

For scale, move event processing to a queue/outbox worker and acknowledge the webhook immediately after durable persistence.
