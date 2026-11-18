from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile',
                                verbose_name="Пользователь")
    phone = models.CharField(max_length=20, verbose_name="Телефон")

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self):
        return f"{self.user.username} ({self.phone})"


class Terminal(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название терминала")
    address = models.CharField(max_length=255, verbose_name="Адрес")

    class Meta:
        verbose_name = "Терминал"
        verbose_name_plural = "Терминалы"
        ordering = ['name']

    def __str__(self):
        return self.name


class Section(models.Model):
    terminal = models.ForeignKey(Terminal, on_delete=models.CASCADE, related_name='sections', verbose_name="Терминал")
    name = models.CharField(max_length=50, verbose_name="Название секции")

    class Meta:
        verbose_name = "Секция"
        verbose_name_plural = "Секции"

    def __str__(self):
        return f"{self.terminal.name} - {self.name}"


class Box(models.Model):
    STATUS_CHOICES = [
        ('free', 'Свободен'),
        ('busy', 'Занят'),
        ('repair', 'Ремонт'),
    ]
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='boxes', verbose_name="Секция")
    number = models.CharField(max_length=10, unique=True, verbose_name="Номер бокса")
    volume = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0.1)],
                                 verbose_name="Объём (м3)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='free', verbose_name="Статус")

    class Meta:
        verbose_name = "Бокс"
        verbose_name_plural = "Боксы"
        ordering = ['number']

    def __str__(self):
        return f"Бокс {self.number} ({self.get_status_display()})"


class Tariff(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название тарифа")
    price_per_m2 = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена за м2")
    boxes = models.ManyToManyField(Box, through='BoxTariff', related_name='tariffs', verbose_name="Боксы")

    class Meta:
        verbose_name = "Тариф"
        verbose_name_plural = "Тарифы"

    def __str__(self):
        return self.name


class BoxTariff(models.Model):
    box = models.ForeignKey(Box, on_delete=models.CASCADE, verbose_name="Бокс")
    tariff = models.ForeignKey(Tariff, on_delete=models.CASCADE, verbose_name="Тариф")
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Скидка (%)")

    class Meta:
        verbose_name = "Тариф бокса"
        verbose_name_plural = "Тарифы боксов"
        unique_together = ('box', 'tariff')

    def __str__(self):
        return f"{self.box} - {self.tariff}"


class Contract(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='contracts', verbose_name="Клиент")
    box = models.ForeignKey(Box, on_delete=models.PROTECT, related_name='contracts', verbose_name="Бокс")
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(null=True, blank=True, verbose_name="Дата окончания")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Итоговая стоимость")

    class Meta:
        verbose_name = "Договор"
        verbose_name_plural = "Договоры"
        constraints = [
            models.CheckConstraint(condition=models.Q(end_date__gt=models.F('start_date')), name='check_dates')
        ]

    def __str__(self):
        return f"Договор №{self.id} - {self.client.user.username}"


class Payment(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='payments', verbose_name="Договор")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    penalty = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Пеня")
    due_date = models.DateField(verbose_name="Срок оплаты")
    paid_date = models.DateField(null=True, blank=True, verbose_name="Дата оплаты")

    class Meta:
        verbose_name = "Платёж"
        verbose_name_plural = "Платежи"

    def __str__(self):
        return f"Платёж {self.amount} по договору {self.contract.id}"

@receiver(post_save, sender=User)
def create_client_profile(sender, instance, created, **kwargs):
    if created:
        Client.objects.create(user=instance, phone="+7(000)000-00-00")

@receiver(post_save, sender=User)
def save_client_profile(sender, instance, **kwargs):
    if hasattr(instance, 'client_profile'):
        instance.client_profile.save()