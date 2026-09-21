# Cargo integration

Cargo should integrate with the main marketplace backend, not directly create a second order status machine in Telegram.

Canonical delivery object:
```json
{
  "carrier": "Cargo",
  "tracking_number": "TRK-123",
  "status": "in_transit",
  "location": "Bishkek",
  "pickup_point": "PVZ-17",
  "eta": "2026-09-20"
}
```

Recommended canonical status enum:
`created`, `accepted`, `picked_up`, `in_transit`, `arrived_destination`, `ready_for_pickup`, `delivered`, `cancelled`, `exception`, `returned`.

Map every Cargo provider status to the backend canonical enum. Telegram renders the canonical enum and localized label.

Webhook:
- HMAC SHA-256 signature
- unique provider event ID
- timestamp / replay protection
- idempotency
- retry-safe processing

The exact Cargo API adapter belongs in the main backend or in a dedicated integration service.
