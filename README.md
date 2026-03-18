# Car Parking

REST API для управления въездом и выездом автомобилей на парковки.

## Что делает

Система контролирует доступ транспортных средств на парковки по белому списку. При въезде/выезде клиент отправляет запрос с номерным знаком, система сверяет доступ и ведёт журнал.

**Логика:**
- Автомобиль должен быть в базе (белый список) и иметь доступ к конкретной парковке
- При въезде проверяется наличие свободных мест
- При выезде отмечается автомобиль, что покинул парковку

**API:**

### Парковки

```
GET /api/parking/
```
Список всех парковок.

### Автомобили клиентов

```
POST /api/parking/car-clients/
```
Создать автомобиль клиента.
```json
{
    “vehicle_plate”: “x123xx123”,
    “parkings”: [1, 2]
}
```

```
PUT /api/parking/car-clients/update/
```
Обновить список парковок автомобиля (или создать, если не существует).
```json
{
    “vehicle_plate”: “x123xx123”,
    “parkings”: [1, 2]
}
```

### Въезд / Выезд

```
POST /api/parking/{parking_id}/event/
```
Зафиксировать въезд или выезд.
```json
{
    “vehiclePlate”: “x123xx123”,
    “direction”: “in”,
    “brand”: “Audi”,
    “model”: “A4”
}
```

`direction` — `”in”` (въезд) или `”out”` (выезд).

Ответы:
- `201` — въезд зафиксирован
- `200` — выезд зафиксирован
- `403` — авто не в белом списке / нет доступа к парковке
- `404` — парковка не найдена / нет активной сессии для выезда
- `409` — нет свободных мест

### Журнал парковки

```
GET /api/parking/{parking_id}/control-cars/
```
История въездов/выездов на конкретной парковке (поля: `vehicle_plate`, `brand`, `model`, `entered_at`, `exited_at`).

## Стек

- Python 3.14, Django 5.2, Django REST Framework 3.15
- PostgreSQL 18
- uWSGI (прод), nginx-proxy
- Poetry 2.2.1

## Запуск

**Требования:** Docker, Docker Compose

Создать `.env` на основе примера:
```bash
cp .env.example .env
```

Запустить:
```bash
docker compose up
```

Применить миграции:
```bash
docker compose run --rm web python manage.py migrate
```

Создать суперпользователя:
```bash
docker compose run --rm web python manage.py createsuperuser
```

**Dev URLs** (требуется nginx-proxy):
- Приложение: `http://car-parking.localhost`
- PgAdmin: `http://pgadmin.car-parking.localhost` (admin@mail.com / adminpassword)

## Тесты

```bash
docker compose run --rm web python manage.py test
```

## Прод

```bash
docker compose -f docker-compose.yml up -d
docker compose -f docker-compose.yml run --rm web python manage.py migrate
docker compose -f docker-compose.yml run --rm web python manage.py collectstatic --noinput
```