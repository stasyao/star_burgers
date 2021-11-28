from collections import Counter

from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.html import format_html_join
from django.views import View

from foodcartapp.models import Order, Product, Restaurant, RestaurantMenuItem
from places.models import Place
from places.utils import calc_distance


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    default_availability = {restaurant.id: False for restaurant in restaurants}
    products_with_restaurants = []
    for product in products:

        availability = {
            **default_availability,
            **{item.restaurant_id: item.availability for item in product.menu_items.all()},
        }
        orderer_availability = [availability[restaurant.id] for restaurant in restaurants]

        products_with_restaurants.append(
            (product, orderer_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurants': products_with_restaurants,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    """
    Независимо от количества заказов и манипуляций с ними, через контроллер
    идёт всегда 4 запроса к БД:
    - получить список всех ресторанов + доступных продуктов в них
    - получить список всех необработанных заказов
    - получить (через prefetch_related) список
      всех продуктов в необработанных заказах
    - получить список локаций, *отфильтрованный* по локациями ресторанов и
      адресам из всех необработанных заказов, т.е. всю таблицу не берем, т.к.
      она будет стремительно увеличиваться за счет каждого нового адреса клиента
    Дополнительные запросы к БД возможны ИСКЛЮЧИТЕЛЬНО в ситуации, когда
    появляется адрес (ресторана или в заказе), которого еще нет в БД.

    Тогда количество запросов = 4 + число новых для базы адресов.
    """
    restaurant_menu = RestaurantMenuItem.objects.get_available_menu()
    not_processed_orders = list(Order.objects.with_prices(processed=False))
    restaurant_addreses = set(
        entry.restaurant.address for entry in restaurant_menu
    )
    clients_addreses = {order.address for order in not_processed_orders}
    places = list(
        Place.objects.filter(address__in=restaurant_addreses | clients_addreses)
    )
    orders_and_restaurants = dict()
    for order in not_processed_orders:
        restaurants = []
        for menu in restaurant_menu:
            if menu.product in order.products.all():
                restaurants.append(menu.restaurant)
        else:
            count = Counter(restaurants)
            # оставляем только те рестораны, в которых доступны все продукты
            # из заказа
            # (проверяем по количеству наименований продуктов в заказе)
            restaurants = [
                (r.name, calc_distance(places, r.address, order.address))
                for r in count if count[r] == order.products.count()
            ]
            restaurants.sort(key=lambda x: x[1])
            orders_and_restaurants[order] = format_html_join(
                    '\n', "<li>{} - {} км</li>", restaurants
            )
    return render(
        request,
        template_name='restaurateur/order_items.html',
        context={'orders_and_restaurants': orders_and_restaurants}
    )
