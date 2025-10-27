# portfolios/selectors.py
from datetime import date
from decimal import Decimal
from .models import Price, Holding, Portfolio

def get_portfolio_prices_between(portfolio: Portfolio, start: date, end: date):
    """{date: {asset_id: price}} para los assets presentes en holdings."""
    asset_ids = list(portfolio.holdings.values_list("asset_id", flat=True).distinct())
    qs = (Price.objects
          .filter(asset_id__in=asset_ids, date__gte=start, date__lte=end)
          .order_by("date", "asset_id"))
    out = {}
    for p in qs.iterator():
        out.setdefault(p.date, {})[p.asset_id] = p.price
    return out

def get_holdings_at(portfolio: Portfolio, at_date: date):
    """Último lote (efective_from más reciente ≤ at_date) por asset."""
    latest = {}
    q = (portfolio.holdings
         .filter(effective_from__lte=at_date)
         .order_by("asset_id", "-effective_from"))
    for h in q:
        if h.asset_id not in latest:
            latest[h.asset_id] = h.quantity
    return latest

def compute_timeseries_weights_and_value(portfolio: Portfolio, start: date, end: date):
    """Devuelve ({fecha:{asset_id:w}}, {fecha:V_t})."""
    price_map = get_portfolio_prices_between(portfolio, start, end)
    result_w, result_V = {}, {}
    for d, prices in price_map.items():
        c_map = get_holdings_at(portfolio, d)
        x_sum = Decimal("0")
        x_map = {}
        for a_id, p in prices.items():
            qty = c_map.get(a_id)
            if qty is None:
                continue
            x = Decimal(p) * Decimal(qty)
            x_map[a_id] = x
            x_sum += x
        if x_sum == 0:
            continue
        result_V[d] = x_sum
        result_w[d] = {a_id: (x / x_sum) for a_id, x in x_map.items()}
    return result_w, result_V
