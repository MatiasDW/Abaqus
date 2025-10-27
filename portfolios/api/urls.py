from django.urls import path
from .views import PortfolioMetricsApi, PortfolioChartsView

urlpatterns = [
    path("portfolios/<int:portfolio_id>/metrics", PortfolioMetricsApi.as_view(), name="portfolio-metrics"),
    path("portfolios/<int:portfolio_id>/charts",  PortfolioChartsView.as_view(), name="portfolio-charts"),
]
