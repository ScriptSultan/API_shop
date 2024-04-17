from django.contrib.auth.models import User
from django.db import models

TYPE_CHOICES = (
        ('phone', 'Телефон'),
        ('email', 'Электронная почта'),
        ('address', 'Адрес'),
    )


class Shop(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название', unique=True)
    url = models.URLField(unique=True, blank=True, verbose_name='Ссылка')
    user = models.OneToOneField(User, verbose_name='Пользователь',
                                blank=True, null=True,
                                on_delete=models.CASCADE)
    status = models.BooleanField(verbose_name='Статус магазина', default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = "Список магазинов"


class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    shops = models.ManyToManyField(Shop, related_name='categories', verbose_name='Категория')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категории'
        verbose_name_plural = "Список категорий"


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name='Название')

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = "Список продуктов"

    def __str__(self):
        return self.name


class ProductInfo(models.Model):
    product = models.ForeignKey(Product, related_name='products_info', on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, related_name='shops_info', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name='Название', blank=True)
    quantity = models.PositiveIntegerField(verbose_name='Количество', blank=True)
    price = models.PositiveIntegerField(verbose_name='Цена', blank=True)
    price_rrc = models.PositiveIntegerField(verbose_name='Розничная цена', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Информация о продукте'


class Parameter(models.Model):
    name = models.CharField(max_length=100, verbose_name='Параметр')

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = "Список параметров"

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    product_info = models.ForeignKey(ProductInfo, related_name='product_details', on_delete=models.CASCADE)
    parameter = models.ForeignKey(Parameter, related_name='parameter_details', on_delete=models.CASCADE)
    value = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'Параметры продукта'

    def __str__(self):
        return f'{self.product_info} {self.parameter}'


class Contact(models.Model):
    type_contact = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='Тип контакта')
    user = models.OneToOneField (User, related_name='contact_user', on_delete=models.CASCADE)
    city = models.CharField(max_length=50, verbose_name='Город', blank=True)
    street = models.CharField(max_length=100, verbose_name='Улица', blank=True)
    house = models.CharField(max_length=15, verbose_name='Дом', blank=True)
    structure = models.CharField(max_length=15, verbose_name='Корпус', blank=True)
    building = models.CharField(max_length=15, verbose_name='Строение', blank=True)
    apartment = models.CharField(max_length=15, verbose_name='Квартира', blank=True)
    phone = models.CharField(max_length=20, verbose_name='Телефон', blank=True)

    def __str__(self):
        return self.type_contact

    class Meta:
        verbose_name = 'Контакты'
        verbose_name_plural = "Список контактов"


class Order(models.Model):
    user = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    dt = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(verbose_name="Статус", default=False)
    contact = models.ForeignKey(Contact, verbose_name='Контакт', blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.status

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = "Список заказов"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='orderitem_order', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='orderitem_product', on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, related_name='orderitem_shop', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return self.quantity

    class Meta:
        verbose_name = 'Информация о заказе'


# class Token(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
#     token = models.CharField(max_length=100, unique=True)

