from phonenumber_field.modelfields import PhoneNumberField

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Sum
from django.db.models.query import Prefetch


class Restaurant(models.Model):
    name = models.CharField('название', max_length=50)
    address = models.CharField('адрес', max_length=100, blank=True)
    contact_phone = models.CharField('контактный телефон',
                                     max_length=50,
                                     blank=True)

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestuarantMenuQueryset(models.QuerySet):
    def get_available_menu(self):
        return (self.select_related('restaurant', 'product')
                    .only('restaurant__name',
                          'restaurant__address',
                          'product__id')
                    .filter(availability=True))


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    objects = RestuarantMenuQueryset.as_manager()

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def with_prices(self, processed=None):
        status = [0, 1] if processed is None else [processed]
        products = Product.objects.only('id')
        return (
            self.prefetch_related(Prefetch('products', queryset=products))
                .defer('registered_at', 'delivered_at', 'called_at')
                .filter(status__in=status)
                .annotate(price=Sum(
                    F('productquantity__price') *
                    F('productquantity__quantity')
                    )
                )
            )


class Order(models.Model):

    class OrderStatus(models.IntegerChoices):
        NOT_PROCESSED = 0, 'не обработан'
        PROCESSED = 1, 'обработан'

    PAYMENT_METHODS = [
        ('at the order', 'оплата сразу'),
        ('при доставке', (('cash', 'наличностью'), ('non_cash', 'картой')))
    ]

    products = models.ManyToManyField(to=Product, through='ProductQuantity',
                                      verbose_name='продукт')
    firstname = models.CharField(max_length=30, verbose_name='имя')
    lastname = models.CharField(max_length=30, verbose_name='фамилия')
    phonenumber = PhoneNumberField(verbose_name='номер телефона')
    address = models.CharField(max_length=200, verbose_name='адрес')
    status = models.IntegerField(choices=OrderStatus.choices,
                                 verbose_name='статус заказа',
                                 default=OrderStatus.NOT_PROCESSED,
                                 db_index=True)
    comment = models.TextField(verbose_name='комментарий к заказу',
                               blank=True)
    payment_method = models.CharField(choices=PAYMENT_METHODS,
                                      max_length=20,
                                      verbose_name='способ оплаты',
                                      blank=True)
    registered_at = models.DateTimeField(verbose_name='когда сделан заказ',
                                         auto_now_add=True)
    called_at = models.DateTimeField(verbose_name='когда позвонили клиенту',
                                     blank=True,
                                     null=True)
    delivered_at = models.DateTimeField(verbose_name='когда доставили',
                                        blank=True,
                                        null=True)

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name_plural = 'Заказы'
        verbose_name = 'Заказ'

    def __str__(self):
        return f'{self.firstname} {self.lastname}, {self.address}'

    def get_full_name(self):
        return f'{self.firstname} {self.lastname}'


class ProductQuantity(models.Model):
    order = models.ForeignKey(to=Order, on_delete=models.CASCADE,
                              verbose_name='заказ')
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE,
                                verbose_name='продукт')
    quantity = models.PositiveSmallIntegerField(
        verbose_name='количество',
        default=1,
        validators=[MinValueValidator(1)]
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name_plural = 'Продукт в заказе'
        verbose_name = 'Продукты в заказе'
