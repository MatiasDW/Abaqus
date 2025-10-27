from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render
from django.views import View

from ..models import Portfolio, Asset
from ..selectors import compute_timeseries_weights_and_value

class PortfolioMetricsApi(APIView):
    """GET /api/portfolios/<id>/metrics?fecha_inicio=YYYY-MM-DD&fecha_fin=YYYY-MM-DD"""
    def get(self, request, portfolio_id: int):
        portfolio = get_object_or_404(Portfolio, id=portfolio_id)
        try:
            start = datetime.strptime(request.GET.get("fecha_inicio"), "%Y-%m-%d").date()
            end = datetime.strptime(request.GET.get("fecha_fin"), "%Y-%m-%d").date()
        except Exception:
            return Response({"detail": "Parámetros inválidos: use YYYY-MM-DD"}, status=400)
        if end < start:
            return Response({"detail": "fecha_fin debe ser >= fecha_inicio"}, status=400)

        w_map, v_map = compute_timeseries_weights_and_value(portfolio, start, end)
        assets = {a.id: a.name for a in Asset.objects.all()}

        weights_series = [
            {"date": d, "weights": {assets.get(a_id, str(a_id)): float(w) for a_id, w in inner.items()}}
            for d, inner in sorted(w_map.items())
        ]
        values_series = [{"date": d, "value": float(v)} for d, v in sorted(v_map.items())]
        return Response({"weights": weights_series, "values": values_series})

class PortfolioChartsView(View):
    template_name = "portfolios/charts.html"
    def get(self, request, portfolio_id: int):
        portfolio = get_object_or_404(Portfolio, id=portfolio_id)
        return render(request, self.template_name, {"portfolio": portfolio})
