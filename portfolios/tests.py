from datetime import date
from decimal import Decimal
from django.test import TestCase
from .models import Asset, Portfolio, Price, InitialWeight, Holding


class ModelsSmokeTest(TestCase):
    def setUp(self):
        # Activos mínimos
        self.a_us = Asset.objects.create(name="EEUU", ticker="US")
        self.a_eu = Asset.objects.create(name="Europa", ticker="EU")

        # Portafolio con V0
        self.t0 = date(2022, 2, 15)
        self.p = Portfolio.objects.create(
            name="Portafolio 1",
            inception_date=self.t0,
            initial_value_usd=Decimal("1000000000.00"),
        )

        # Precios al t0
        Price.objects.create(asset=self.a_us, date=self.t0, price=Decimal("10"))
        Price.objects.create(asset=self.a_eu, date=self.t0, price=Decimal("20"))

        # Weights iniciales (suman 1)
        InitialWeight.objects.create(portfolio=self.p, asset=self.a_us, weight=Decimal("0.6"))
        InitialWeight.objects.create(portfolio=self.p, asset=self.a_eu, weight=Decimal("0.4"))

    def test_models_exist(self):
        self.assertEqual(Asset.objects.count(), 2)
        self.assertEqual(Portfolio.objects.count(), 1)
        self.assertEqual(Price.objects.count(), 2)
        self.assertEqual(InitialWeight.objects.count(), 2)

    def test_str_methods(self):
        self.assertEqual(str(self.a_us), "EEUU")
        self.assertEqual(str(self.p), "Portafolio 1")

    def test_holding_schema(self):
        # No holdings aún (los crea el ETL/servicio)
