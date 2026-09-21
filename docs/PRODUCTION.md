# Production checklist

- Configure HTTPS and Telegram webhook.
- Set strong secrets.
- Use a real migration runner instead of `create_all`.
- Replace placeholder REST paths and schemas with the existing backend contract.
- Use backend-issued scoped integration tokens.
- Enforce backend RBAC for every write.
- Add document upload to object storage; pass references to backend, never store documents in Telegram state.
- Add callback authorization by loading current backend object before mutation.
- Add rate limits.
- Add structured logging without tokens/payment/PII.
- Add OpenTelemetry/Sentry or equivalent.
- Add event retry queue.
- Add webhook replay protection using timestamp + event ID.
- Add CI with lint/type checks/unit/integration tests.
- Add automated translation key consistency check.
- Add tests for every money-moving endpoint and destructive product action.
- Verify GDPR/privacy/data retention requirements for the actual deployment jurisdiction.
