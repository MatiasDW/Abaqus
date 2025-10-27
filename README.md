# Django Portfolios — ETL · API · Charts

This project implements a minimal investment portfolio platform in **Django**:
- Models for **assets**, **portfolios**, **prices**, **initial weights**, **holdings** and **trades**.
- An **ETL** command to load the provided Excel (`datos.xlsx`), compute initial holdings \(C_{i,0}\) for each portfolio, and persist price history.
- A **REST API** to query portfolio value \(V_t\) and weights \(w_{i,t}\) over a date range.
- A simple **chart view** (bonus) that visualizes \(V_t\) and \(w_{i,t}\).

The code structure follows the principles of the [HackSoft Django Styleguide](https://github.com/HackSoftware/Django-Styleguide): a single **vertical slice app** (`portfolios/`) with `models.py`, `selectors.py` (read-only queries), `services.py` (business actions), and an `api/` module for serializers, views and routes.

---

## Stack

- Python 3.12, Django 5.x, Django REST Framework
- PostgreSQL (via Docker)
- Pandas & OpenPyXL for ETL
- Chart.js for the bonus visualization

---

## Project layout

```
repo/
├─ config/                      # Django project
│  ├─ settings.py
│  ├─ urls.py
│  ├─ asgi.py / wsgi.py
│  └─ __init__.py
└─ portfolios/                  # Single domain app (vertical slice)
   ├─ models.py                 # DB schema
   ├─ selectors.py              # read-only queries (ORM)
   ├─ services.py               # write/business actions (trades, bootstrap, etc.)
   ├─ api/
   │  ├─ serializers.py
   │  ├─ views.py               # DRF views + charts view
   │  └─ urls.py
   ├─ management/commands/
   │  └─ load_datos.py          # ETL from datos.xlsx
   ├─ templates/portfolios/
   │  └─ charts.html            # Bonus 1 view
   ├─ migrations/
   └─ middleware.py             # Easter egg header (optional)
```

---

## Quick start (Docker)

1) **Environment**
   ```bash
   cp .env.example .env
   # Adjust DJANGO_SECRET_KEY and any other variable if needed
   ```

2) **Build & run**
   ```bash
   docker compose up -d --build
   docker compose exec web python manage.py migrate
   ```

3) **Load data (ETL)**  
   Place `datos.xlsx` in the project root (same level as `manage.py`), then:
   ```bash
   # Portafolio 1 (V0 = 1,000,000,000 @ 2022-02-15)
   docker compose exec web python manage.py load_datos /app/datos.xlsx 2022-02-15 1000000000 "Portafolio 1"

   # Portafolio 2 (V0 = 1,000,000,000 @ 2022-02-15)
   docker compose exec web python manage.py load_datos /app/datos.xlsx 2022-02-15 1000000000 "Portafolio 2"
   ```

4) **Smoke tests**
   - Healthcheck: <http://localhost:8000/healthz>
   - API sample:  
     `GET /api/portfolios/1/metrics?fecha_inicio=2022-02-15&fecha_fin=2023-02-16`  
     Example: <http://localhost:8000/api/portfolios/1/metrics?fecha_inicio=2022-02-15&fecha_fin=2023-02-16>
   - Charts (bonus): <http://localhost:8000/api/portfolios/1/charts>

---

## API

### `GET /api/portfolios/<id>/metrics`
**Query params**
- `fecha_inicio` — `YYYY-MM-DD`
- `fecha_fin` — `YYYY-MM-DD`

**Response**
```json
{
  "values": [
    {"date": "2022-02-15", "value": 1000000000.0},
    ...
  ],
  "weights": [
    {"date": "2022-02-15", "weights": {"EEUU": 0.28, "Europa": 0.087, ...}},
    ...
  ]
}
```

The API assumes **quantities are fixed** \(c_{i,t} = c_{i,0}\). Values and weights evolve with price changes.

---

## ETL (`load_datos.py`)

- Reads **`weights`** (sheet: `weights`/`Weights`) and **`prices`** (sheet: `Precios`/`Prices`), handling minor variations in case/labels.
- Creates `Asset`, `Price`, `InitialWeight` and computes **initial holdings** \(C_{i,0} = w_{i,0} \* V_0 / P_{i,0}\).
- Uses `services.bootstrap_initial_holdings` to persist holdings \(c_{i,0}\).

Run:
```bash
docker compose exec web python manage.py load_datos /app/datos.xlsx 2022-02-15 1000000000 "Portafolio 1"
```

---

## Bonus 1 — Charts

- `GET /api/portfolios/<id>/charts` renders a simple page using **Chart.js**.
- The demo version loads a fixed range known to contain data (can be easily adjusted).

---

## Bonus 2 — Trades (optional)

Trades are supported via the `services.py` layer. Example (sell **USD 200M EEUU** and buy **USD 200M Europa** on **2022‑05‑15** for Portafolio 1):

```bash
docker compose exec -it web python manage.py shell
```

```python
from decimal import Decimal
from datetime import date
from portfolios.models import Portfolio, Asset
from portfolios.services import post_trade_usd_notional

p  = Portfolio.objects.get(name="Portafolio 1")
us = Asset.objects.get(name="EEUU")
eu = Asset.objects.get(name="Europa")

post_trade_usd_notional(p, us, date(2022,5,15), Decimal("-200000000"))  # sell 200M
post_trade_usd_notional(p, eu, date(2022,5,15),  Decimal("200000000"))  # buy 200M
```

Re‑query the API over a range that includes `2022‑05‑15` to see updated \(c_{i,t}\), \(x_{i,t}\), \(w_{i,t}\) and \(V_t\) from that date onward.

> Note: By design, trades adjust holdings from the trade date forward while preserving past history.

---

## Notes

- The **style** follows the HackSoft Django Styleguide (single domain app, `selectors` for reads, `services` for writes, and a thin `api/` layer).
- An optional middleware (`portfolios.middleware.EasterEggHeaderMiddleware`) sets the header `X-Mat-Egg` when `EASTER_EGG_MSG` is present in `.env`.
- Default timezone and DB settings are configured via environment variables in `.env`.

---
