# Модель данных (ERD) — Служба заявок

Диаграмма отражает реальную схему БД проекта (приложение `helpdesk`).

```mermaid
erDiagram
    USER ||--o{ TICKET : "создаёт как автор"
    USER ||--o{ TICKET : "назначается исполнителем"
    CATEGORY ||--o{ TICKET : "группирует по категории"
    STATUS ||--o{ TICKET : "задаёт статус"
    PRIORITY ||--o{ TICKET : "задаёт приоритет"
    TICKET ||--o{ COMMENT : "содержит переписку"
    USER ||--o{ COMMENT : "оставляет комментарии"
    TICKET }o--o{ TAG : "помечена метками (ticket_tags)"

    USER {
        int id PK
        string username UK
        string password "хеш"
        string first_name
        string last_name
        string email
        string role "client | agent | admin"
        bool is_staff
        datetime date_joined
    }
    CATEGORY {
        int id PK
        string name UK
        string description
    }
    STATUS {
        int id PK
        string name UK
        int order
        bool is_closed
    }
    PRIORITY {
        int id PK
        string name UK
        int weight
    }
    TAG {
        int id PK
        string name UK
    }
    TICKET {
        int id PK
        string title
        text description
        int author_id FK
        int assignee_id FK "nullable"
        int category_id FK
        int status_id FK
        int priority_id FK
        datetime created_at
        datetime updated_at
        datetime closed_at "nullable"
    }
    COMMENT {
        int id PK
        int ticket_id FK
        int author_id FK
        text body
        bool is_internal
        datetime created_at
    }
```

## Сущности и назначение

| Таблица | Назначение | Ключевые связи |
|---------|------------|----------------|
| `helpdesk_user` | Учётные записи с ролью (client / agent / admin). Пароль хранится в виде хеша. | 1:N к Ticket (как автор и как исполнитель), 1:N к Comment |
| `helpdesk_category` | Справочник категорий заявок | 1:N к Ticket |
| `helpdesk_status` | Справочник статусов; `is_closed` помечает закрывающие | 1:N к Ticket |
| `helpdesk_priority` | Справочник приоритетов; `weight` — для сортировки | 1:N к Ticket |
| `helpdesk_tag` | Метки заявок | M:N к Ticket |
| `helpdesk_ticket` | Заявка — центральная сущность | FK на User×2, Category, Status, Priority; M:N с Tag |
| `helpdesk_comment` | Переписка по заявке; `is_internal` — внутренние записи для агентов | FK на Ticket и User |
| `helpdesk_ticket_tags` | Связующая таблица «многие-ко-многим» Ticket↔Tag | — |

## Нормализация

- **1НФ** — все поля атомарны; множественные метки вынесены в `tag` + `ticket_tags`.
- **2НФ** — справочники (status, priority, category) отдельны; в `ticket` хранятся только FK.
- **3НФ** — нет транзитивных зависимостей: данные пользователя не дублируются в заявках/комментариях.

## Роли и права (администрирование)

| Действие | client | agent | admin |
|----------|:------:|:-----:|:-----:|
| Создать заявку / комментировать | ✅ | ✅ | ✅ |
| Видеть свои заявки | ✅ | ✅ | ✅ |
| Видеть все заявки | ❌ | ✅ | ✅ |
| Менять статус / приоритет / исполнителя | ❌ | ✅ | ✅ |
| Внутренние комментарии | ❌ | ✅ | ✅ |
| Управление пользователями и справочниками (админка) | ❌ | ❌ | ✅ |
