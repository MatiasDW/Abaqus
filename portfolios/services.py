# portfolios/services.py
from datetime import date
from decimal import Decimal, ROUND_DOWN
from django.db import transaction
from .models import Portfolio, Asset, Price, InitialWeight, Holding, Trade

@transaction.atomic
def bootstrap_initial_holdings(portfolio: Portfolio, t0: date):
    """
    C_{i,0} = w_{i,0} * V0 / P_{i,0}
    Crea Holding(effective_from=t0) por asset con weight inicial.
    """
    prices_t0 = {p.asset_id: p.price for p in Price.objects.filter(date=t0)}
    weights = InitialWeight.objects.filter(portfolio=portfolio)
    created = []
    for w in weights:
        p = Decimal(prices_t0[w.asset_id])
        qty = (Decimal(w.weight) * Decimal(portfolio.initial_value_usd) / p)
        qty = qty.quantize(Decimal("1.000000000000"), rounding=ROUND_DOWN)
        h = Holding.objects.create(
            portfolio=portfolio, asset=w.asset, quantity=qty, effective_from=t0
        )
        created.append(h)
    print(f"[INFO] Holdings iniciales: {len(created)} en {portfolio.name}")
    return created

@transaction.atomic
def post_trade_usd_notional(portfolio: Portfolio, asset: Asset, trade_date: date, amount_usd: Decimal):
    """
    Ajusta cantidades desde 'trade_date':
    Δqty = amount_usd / P(asset, trade_date). Positivo=BUY, Negativo=SELL.
    """
    price_row = Price.objects.filter(asset=asset, date=trade_date).first()
    if not price_row:
        raise ValueError(f"Falta precio para {asset} el {trade_date}")
    delta_qty = Decimal(amount_usd) / Decimal(price_row.price)

    latest = (Holding.objects
              .filter(portfolio=portfolio, asset=asset, effective_from__lte=trade_date)
              .order_by("-effective_from")
              .first())
    if not latest:
        raise ValueError("No existe holding previo que ajustar.")

    new_qty = latest.quantity + delta_qty
    if new_qty < 0:
        raise ValueError("La cantidad resultante quedaría negativa.")

    Holding.objects.create(
        portfolio=portfolio, asset=asset, quantity=new_qty, effective_from=trade_date
    )
    Trade.objects.create(
        portfolio=portfolio, asset=asset, trade_date=trade_date, amount_usd=amount_usd
    )
    print(f"[INFO] Trade {asset} {amount_usd} USD @ {trade_date} → qty {new_qty}")
