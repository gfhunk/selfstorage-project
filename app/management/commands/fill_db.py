from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.models import Client, Terminal, Section, Box, Tariff, Contract, Payment
import random
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Заполняет БД тестовыми данными'

    def handle(self, *args, **kwargs):
        self.stdout.write('Начинаем заполнение базы...')

        t1 = Terminal.objects.create(name="Терминал Центр", address="ул. Ленина, 5")
        s1 = Section.objects.create(terminal=t1, name="Этаж 1")

        for i in range(1, 36):
            Box.objects.create(
                section=s1,
                number=f"A-{100 + i}",
                volume=round(random.uniform(1.0, 10.0), 2),
                status='free'
            )
        self.stdout.write('Создано 35 боксов.')

        tariff1 = Tariff.objects.create(name="Базовый", price_per_m2=500)

        for i in range(1, 13):
            u = User.objects.create_user(username=f'client{i}', password='password123')
            c = Client.objects.create(user=u, phone=f'+799900000{i:02d}')

            box = Box.objects.filter(status='free').first()
            if box:
                box.status = 'busy'
                box.save()

                con = Contract.objects.create(
                    client=c,
                    box=box,
                    start_date=date.today(),
                    is_active=True
                )

                Payment.objects.create(
                    contract=con,
                    amount=1000,
                    due_date=date.today() + timedelta(days=5)
                )

        self.stdout.write(self.style.SUCCESS('База успешно заполнена: 35 боксов, 12 клиентов и договоров!'))