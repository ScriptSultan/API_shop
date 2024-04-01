from django.contrib.auth.models import User
from django.db import models

TYPE_CHOICES = (
        ('phone', 'Телефон'),
        ('email', 'Электронная почта'),
        ('address', 'Адрес'),
    )


class Shop(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    url = models.URLField(unique=True, blank=True, verbose_name='Ссылка')

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

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = "Список продуктов"


class ProductInfo(models.Model):
    product = models.ForeignKey(Product, related_name='products_info', on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, related_name='shops_info', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name='Название')
    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Информация о продукте'


class Parameter(models.Model):
    name = models.CharField(max_length=100, verbose_name='Параметр')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = "Список параметров"


class ProductParameter(models.Model):
    product_info = models.ForeignKey(ProductInfo, related_name='product_details', on_delete=models.CASCADE)
    parameter = models.ForeignKey(Parameter, related_name='parameter_details', on_delete=models.CASCADE)
    value = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.product_info} {self.parameter}'

    class Meta:
        verbose_name = 'Параметры продукта'


class Order(models.Model):
    user = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    dt = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.status

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = "Список заказов"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='orderitem_order')
    product = models.ForeignKey(Product, related_name='orderitem_product')
    shop = models.ForeignKey(Shop, related_name='orderitem_shop', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return self.quantity

    class Meta:
        verbose_name = 'Информация о заказе'


class Contact(models.Model):
    type_contact = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='Тип контакта')
    user = models.ForeignKey(User, related_name='contact_user', on_delete=models.CASCADE)
    value = models.PositiveIntegerField()

    def __str__(self):
        return self.type_contact

    class Meta:
        verbose_name = 'Контакты'
        verbose_name_plural = "Список контактов"