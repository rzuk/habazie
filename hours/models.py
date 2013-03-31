# -*- coding: utf-8 -*-
import calendar
import datetime

from django.contrib import admin
from django.contrib.auth.models import AbstractUser
from django.db import models as dm


class User(AbstractUser):
    class Meta(AbstractUser.Meta):
        verbose_name = u'użytkownik'
        verbose_name_plural = u'użytkownicy'

    saldo = dm.DecimalField(max_digits=5, decimal_places=2, default=0)
    nick = dm.CharField(max_length=20, default='')

    def change_saldo(self, value, note=None, reservation=None):
        pass


class UserAccountAdmin(admin.ModelAdmin):
    pass

admin.site.register(User, UserAccountAdmin)


class StuffCategory(dm.Model):
    class Meta:
        verbose_name = u'rodzaj sprzętu'
        verbose_name_plural = u'rodzaje sprzętu'

    name = dm.CharField(max_length=100)
    price = dm.OneToOneField('hours.Price')

    def __unicode__(self):
        return self.name

admin.site.register(StuffCategory)


class Stuff(dm.Model):
    class Meta:
        verbose_name = u'sprzęt'
        verbose_name_plural = u'sprzęt'

    name = dm.CharField(max_length=50, null=True)
    photo = dm.FileField(upload_to='stuff/',)
    category = dm.ForeignKey(StuffCategory)

    def __unicode__(self):
        return self.name if self.name else self.category.name

    def reservations_in_month(self, year, month):
        start = datetime.datetime(year, month, 1)
        end = datetime(year, month, calendar.monthrange(year, month)[1])
        qs = self.reservation_set.filter(start_be)
        pass


class StuffAdmin(admin.ModelAdmin):
    pass

admin.site.register(Stuff, StuffAdmin)


class ReservationStatus:
    unconfirmed = 'U', u"niepotwierdzony"
    accepted = 'A', u'zaakceptowany'
    cancelled = 'C', u'anulowany'
    done = 'D', u'zakończony'

    @staticmethod
    def choices():
        return (ReservationStatus.unconfirmed, ReservationStatus.accepted,
                ReservationStatus.cancelled, ReservationStatus.done)


class Reservation(dm.Model):
    class Meta:
        verbose_name = u'rezerwacja'
        verbose_name_plural = u'rezerwacje'

    stuff = dm.ForeignKey(Stuff)
    start = dm.DateTimeField()
    end = dm.DateTimeField()
    user = dm.ForeignKey(User)
    status = dm.CharField(max_length=20, choices=ReservationStatus.choices())
    cost = dm.DecimalField(max_digits=5, decimal_places=2, default=0)
    supervisor_notes = dm.TextField()

admin.site.register(Reservation)


class Price(dm.Model):
    class Meta:
        verbose_name = u'cena'
        verbose_name_plural = u'ceny'
    value = dm.DecimalField(max_digits=5, decimal_places=2, default=0)
admin.site.register(Price)


class SaldoChange(dm.Model):
    class Meta:
        verbose_name = u'zmiana godzinek'
        verbose_name_plural = u'zmiany godzinek'

    user = dm.ForeignKey(User)
    value = dm.DecimalField(max_digits=5, decimal_places=2, default=0)
    date = dm.DateTimeField(auto_now=True)
    author = dm.ForeignKey(User, related_name='changes_done')
    note = dm.TextField()
    reservation = dm.ForeignKey(Reservation, null=True)
admin.site.register(SaldoChange)