# Marketplace Telegram Interface — Full TЗ Edition

Полноценный Telegram-интерфейс над существующим marketplace backend.

## Принцип
Telegram не является отдельной бизнес-системой. Пользователи, товары, заказы, Cargo, wallet, referral/team, статусы, подписки, сотрудничество и модерация принадлежат основному backend.

Бот:
- читает данные через REST API;
- отправляет разрешённые команды в backend;
- принимает подписанные backend events/webhooks;
- переводит события в Telegram-уведомления;
- хранит только Telegram-specific данные: связь Telegram↔backend user, locale, notification preferences и idempotency.

## Реализованные модули

1. i18n:
   - ru, ky, kk, uz, tg;
   - locale сохраняется;
   - смена языка;
   - JSON переводы без изменения Python.

2. Seller:
   - список;
   - создание;
   - редактирование;
   - цена;
   - наличие;
   - удаление;
   - moderation.

3. Orders/Cargo:
   - список;
   - детали;
   - tracking number;
   - carrier/Cargo;
   - статус;
   - location;
   - PVZ;
   - ETA;
   - webhook/event notifications;
   - единые canonical delivery statuses.

4. Wallet:
   - total/available/frozen;
   - операции;
   - top-up;
   - withdrawal;
   - refunds/fees как данные backend;
   - подтверждение финансовых действий.

5. Team/referral:
   - 1–15 levels;
   - filters;
   - active/inactive;
   - new members;
   - progress;
   - reward;
   - только backend source of truth.

6. Status/subscription:
   - Partner/Consultant/Leader;
   - current/next;
   - conditions/progress;
   - subscription;
   - payment history;
   - payment initiation;
   - notifications.

7. Cooperation:
   - пошаговая заявка;
   - Cargo/logistics/courier/Last Mile/PVZ;
   - geography/warehouses/branches/PVZ/tariffs/API/tracking/webhook/docs;
   - backend stores moderation and audit.

8. Notifications:
   - durable event endpoint;
   - idempotency;
   - localized templates;
   - Telegram delivery;
   - notification preferences.

## Backend API

Все реальные endpoint'ы могут называться иначе. Адаптер `app/integrations/backend.py` изолирует это отличие.

Перед production:
- заменить API paths на фактический контракт;
- подключить реальную авторизацию/linking;
- проверить scopes/roles;
- подключить backend event bus/outbox или подписанные webhook;
- настроить reverse proxy HTTPS;
- провести security review.
