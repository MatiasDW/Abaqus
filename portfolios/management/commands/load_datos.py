import pandas as pd
from decimal import Decimal
from datetime import datetime
from django.core.management.base import BaseCommand
from portfolios.models import Asset, Portfolio, Price, InitialWeight
from portfolios.services import bootstrap_initial_holdings


def pick_sheet(xls: pd.ExcelFile, *cands: str) -> str:
    """Devuelve el nombre real de la hoja matcheando por lower() y parcial."""
    names = [s.strip() for s in xls.sheet_names]
    lower = {s.lower(): s for s in names}
    # exactos por lower
    for c in cands:
        if c.lower() in lower:
            return lower[c.lower()]
    # parciales (e.g. "Sheet - weights")
    for s in names:
        sl = s.lower()
        if any(c.lower() in sl for c in cands):
            return s
    raise SystemExit(f"No se encontró ninguna hoja entre {cands}. Hojas: {names}")


def pick_col(df: pd.DataFrame, *cands: str) -> str:
    """Devuelve el nombre real de la columna matcheando por lower(); fallback: primera."""
    cols = [str(c).strip() for c in df.columns]
    lower = {c.lower(): c for c in cols}
    for c in cands:
        if c.lower() in lower:
            return lower[c.lower()]
    return cols[0]


class Command(BaseCommand):
    help = "Carga datos.xlsx (weights + Precios) y calcula c_{i,0}."

    def add_arguments(self, parser):
        parser.add_argument("xlsx_path", type=str)
        parser.add_argument("t0", type=str, help="YYYY-MM-DD, e.g. 2022-02-15")
        parser.add_argument("v0", type=str, help="Initial portfolio value in USD, e.g. 1000000000")
        parser.add_argument("portfolio_name", type=str)

    def handle(self, *args, **opts):
        xlsx_path = opts["xlsx_path"]
        t0 = datetime.strptime(opts["t0"], "%Y-%m-%d").date()
        v0 = Decimal(opts["v0"])
        portfolio_name = opts["portfolio_name"].strip()

        # Crea/actualiza portafolio
        portfolio, _ = Portfolio.objects.get_or_create(
            name=portfolio_name,
            defaults={"inception_date": t0, "initial_value_usd": v0},
        )
        if portfolio.initial_value_usd != v0:
            portfolio.initial_value_usd = v0
            portfolio.save(update_fields=["initial_value_usd"])

        xls = pd.ExcelFile(xlsx_path)

        # === Hojas (según tu archivo: 'weights' y 'Precios') ===
        weights_sheet = pick_sheet(xls, "weights", "Weights", "pesos", "Pesos")
        prices_sheet  = pick_sheet(xls, "Precios", "precios", "Prices", "prices")

        df_w = pd.read_excel(xls, sheet_name=weights_sheet)
        df_p = pd.read_excel(xls, sheet_name=prices_sheet)

        # === Columna fecha en Precios: 'Dates' (tu archivo) ===
        date_col = pick_col(df_p, "Dates", "Date", "Fecha", "fecha", "date")
        df_p[date_col] = pd.to_datetime(df_p[date_col]).dt.date

        # Todas las demás columnas son activos
        asset_cols = [c for c in df_p.columns if str(c).strip() != date_col]

        # Asegura assets
        assets = {}
        for col in asset_cols:
            name = str(col).strip()
            a, _ = Asset.objects.get_or_create(name=name)
            assets[name] = a

        # Carga precios
        prices_to_create = []
        for _, row in df_p.iterrows():
            dt = row[date_col]
            for col in asset_cols:
                name = str(col).strip()
                price = Decimal(str(row[col]))
                prices_to_create.append(Price(asset=assets[name], date=dt, price=price))
        Price.objects.bulk_create(prices_to_create, ignore_conflicts=True)

        # === Weights ===
        # En tu archivo: columnas 'activos', 'portafolio 1', 'portafolio 2'
        asset_name_col = pick_col(df_w, "activos", "Activo", "Asset", "Nombre", "name")
        col_p1 = pick_col(df_w, "portafolio 1", "Portfolio 1", "p1", "1")
        col_p2 = pick_col(df_w, "portafolio 2", "Portfolio 2", "p2", "2")

        # Elige columna de weights según nombre del portafolio (…1 o …2)
        target_col = None
        if portfolio_name.endswith("1"):
            target_col = col_p1
        elif portfolio_name.endswith("2"):
            target_col = col_p2
        if target_col is None:
            raise SystemExit(
                f"No se detectó la columna de weights para '{portfolio_name}'. "
                f"Columns en weights: {list(df_w.columns)}"
            )

        # (re)carga weights
        InitialWeight.objects.filter(portfolio=portfolio).delete()
        to_create_w = []
        for _, row in df_w.iterrows():
            asset_name = str(row[asset_name_col]).strip()
            if not asset_name:
                continue
            if asset_name not in assets:
                a, _ = Asset.objects.get_or_create(name=asset_name)
                assets[asset_name] = a
            w = Decimal(str(row[target_col]))
            to_create_w.append(InitialWeight(portfolio=portfolio, asset=assets[asset_name], weight=w))
        InitialWeight.objects.bulk_create(to_create_w)

        # Calcula C_{i,0} y guarda Holdings
        created = bootstrap_initial_holdings(portfolio, t0)

        self.stdout.write(self.style.SUCCESS(
            f"Cargados {len(assets)} assets, {len(prices_to_create)} precios y {len(created)} holdings para {portfolio_name}."
        ))
