from django.db import transaction
from rest_framework import serializers

from .models import Order, ProductQuantity


class ProductQuantitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductQuantity
        fields = ['product', 'quantity', ]


class OrderSerializer(serializers.ModelSerializer):
    products = ProductQuantitySerializer(many=True, allow_empty=False,
                                         write_only=True)

    class Meta:
        model = Order
        fields = '__all__'

    def create(self, validated_data):
        products = validated_data.pop('products')
        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            products_for_order = [
                ProductQuantity(**product | {
                    'order': order, 'price': product['product'].price
                }) for product in products
            ]
            ProductQuantity.objects.bulk_create(products_for_order)
        return order
