from rest_framework import serializers
from ..models import Asset

class WeightPointSerializer(serializers.Serializer):
    date = serializers.DateField()
    weights = serializers.DictField(child=serializers.FloatField())

class ValuePointSerializer(serializers.Serializer):
    date = serializers.DateField()
    value = serializers.DecimalField(max_digits=30, decimal_places=6)

class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ("id", "name", "ticker")
