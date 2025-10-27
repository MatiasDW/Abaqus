from django.db import models
from django.core.validators import MinValueValidator


class TimeStampedModel(models.Model):
    """Timestamps básicos para auditoría."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Asset(TimeStampedModel):
    name = models.CharField(max_length=128, unique=True)
    ticker = models.CharField(max_length=32, blank=True, default="")

    def __str__(self) -> str:
        return self.name


class Portfolio(TimeStampedModel):
    name = models.CharField(max_length=128, unique=True)
    inception_date = models.DateField()
    initial_value_usd = models.DecimalField(
        max_digits=20, decimal_places=2, validators=[MinValueValidator(0)]
    )

    def __str__(self) -> str:
        return self.name


class Price(TimeStampedModel):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="prices")
    date = models.DateField()
    price = models.DecimalField(max_digits=20, decimal_places=8, validators=[MinValueValidator(0)])

    class Meta:
        unique_together = ("asset", "date")
        indexes = [
            models.Index(fields=["asset", "date"]),
            models.Index(fields=["date"]),
        ]


class InitialWeight(TimeStampedModel):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="initial_weights")
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    weight = models.DecimalField(max_digits=10, decimal_places=8)  # 0..1

    class Meta:
        unique_together = ("portfolio", "asset")
        indexes = [models.Index(fields=["portfolio", "asset"])]


class Holding(TimeStampedModel):
    """Cantidad c_{i,t} por tramos (cambia cuando hay trades)."""
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="holdings")
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=30, decimal_places=12, validators=[MinValueValidator(0)])
    effective_from = models.DateField()

    class Meta:
        indexes = [models.Index(fields=["portfolio", "asset"])]


class Trade(TimeStampedModel):
    """Trade en USD (positivo = compra, negativo = venta)."""
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="trades")
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    trade_date = models.DateField()
    amount_usd = models.DecimalField(max_digits=20, decimal_places=2)

    class Meta:
        indexes = [models.Index(fields=["portfolio", "trade_date"])]
