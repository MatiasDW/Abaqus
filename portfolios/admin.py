from django.contrib import admin
from .models import Asset, Portfolio, Price, InitialWeight, Holding, Trade


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "ticker", "created_at", "updated_at")
    search_fields = ("name", "ticker")


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "inception_date", "initial_value_usd", "created_at")
    search_fields = ("name",)


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ("id", "asset", "date", "price")
    list_filter = ("asset", "date")
    date_hierarchy = "date"


@admin.register(InitialWeight)
class InitialWeightAdmin(admin.ModelAdmin):
    list_display = ("id", "portfolio", "asset", "weight")
    list_filter = ("portfolio", "asset")


@admin.register(Holding)
class HoldingAdmin(admin.ModelAdmin):
    list_display = ("id", "portfolio", "asset", "quantity", "effective_from")
    list_filter = ("portfolio", "asset")
    date_hierarchy = "effective_from"


@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = ("id", "portfolio", "asset", "trade_date", "amount_usd", "created_at")
    list_filter = ("portfolio", "asset")
    date_hierarchy = "trade_date"
