from django.contrib.auth.models import AbstractUser, Group
from django.db import models


class Users(AbstractUser):
    chat_id = models.IntegerField(null=True,blank=True)
    surename = models.CharField(max_length=15, null=True, blank=True, verbose_name='Отчество')
    phone_number = models.CharField(max_length=12, null=True, blank=True, verbose_name='Номер телефона')
    admin_verification = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.surename}'

    class Meta():
        verbose_name = 'Пользователь'
        verbose_name_plural = "Пользователи"


class Students(models.Model):
    first_name = models.CharField(max_length=15, verbose_name='Имя')
    last_name = models.CharField(max_length=15, verbose_name='Фамилия')
    sure_name = models.CharField(max_length=15, null=True,blank=True, verbose_name='Отчество')
    klass = models.ForeignKey(
        Group,
        models.CASCADE,
        verbose_name=("Класс"),
    )
    card = models.CharField(max_length=10, null=True,blank=True)
    presence = models.BooleanField(verbose_name='Присутствие')

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.sure_name}'

    class Meta():
        verbose_name = 'Ученик'
        verbose_name_plural = "Ученики"


class Evacuation(models.Model):
    STATUS = {
        ('0', 'нет данных'),
        ('1', 'эвакуированы'),
        ('2', 'забарикодированы'),
    }

    teacher = models.ForeignKey(
        Users,
        models.CASCADE,
        verbose_name=("Учитель"),
    )
    klass = models.ForeignKey(
        Group,
        models.CASCADE,
        verbose_name=("Класс"),
    )
    before = models.IntegerField(default=0, verbose_name='Должно быть')
    amount = models.IntegerField(default=0, verbose_name='Эвакуировано')
    missing = models.IntegerField(default=0, verbose_name='Расхождение')
    klass_room = models.CharField(max_length=30, verbose_name='Кабинет')
    status = models.CharField(
        max_length=2,
        choices=STATUS,
        default=0,
    )

    note = models.CharField(max_length=300, verbose_name='Доп. информация')
    date = models.DateTimeField(null=True, blank=True)

    class Meta():
        verbose_name = 'Эвакуация'
        verbose_name_plural = "Эвакуации"


class Missing(models.Model):
    REASON = [
        ('б', "болеет"),
        ('у', "уважительная"),
        ('н', "неуважительная"),
    ]
    student = models.ForeignKey(
        Students,
        models.CASCADE,
        verbose_name=("Ученик"),
    )
    date = models.DateTimeField(verbose_name='Дата')
    reason = models.CharField(
        max_length=2,
        choices=REASON,
        default='н',
        verbose_name='Причина'
    )
    accuracy = models.BooleanField(null=True)

    class Meta():
        verbose_name = 'Пропуск'
        verbose_name_plural = "Пропуски"
