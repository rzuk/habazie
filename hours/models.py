# -*- coding: utf-8 -*-
import datetime

from django.contrib import admin
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models as dm
from hours.utils import Calendar


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
    price = dm.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    def __unicode__(self):
        return self.name


admin.site.register(StuffCategory)


class Stuff(dm.Model):
    class Meta:
        verbose_name = u'sprzęt'
        verbose_name_plural = u'sprzęt'

    name = dm.CharField(max_length=50, null=True)
    photo = dm.FileField(upload_to='stuff/', )
    category = dm.ForeignKey(StuffCategory)

    def __unicode__(self):
        return self.name if self.name else self.category.name

    def reservations_in_month(self, year, month):
        start = datetime.datetime(year, month, 1)
        end = Calendar.add_month(year, month, 1)
        return self.reservation_set.exclude(end__lt=start).exclude(start__gt=end)


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

    @staticmethod
    def as_dict():
        return dict(ReservationStatus.choices())

    @staticmethod
    def check_status(value):
        if value not in ReservationStatus.as_dict():
            raise ValidationError(u'Niewłaściwy status rezerwacji.')


class Reservation(dm.Model):
    class Meta:
        verbose_name = u'rezerwacja'
        verbose_name_plural = u'rezerwacje'

    stuff = dm.ForeignKey(Stuff, verbose_name='sprzęt')
    start = dm.DateTimeField(verbose_name='start')
    end = dm.DateTimeField(verbose_name='koniec')
    user = dm.ForeignKey(User, verbose_name=u'rezerwujący')
    status = dm.CharField(max_length=20, choices=ReservationStatus.choices(), default=ReservationStatus.unconfirmed[0],
                          validators=[ReservationStatus.check_status])
    cost = dm.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='koszt')
    supervisor_notes = dm.TextField(blank=True, verbose_name=u'uwagi sprzętowca')
    user_notes = dm.TextField(blank=True, verbose_name=u'uwagi')
    date = dm.DateTimeField(verbose_name='data rezerwacji')

    def clean(self):
        if not self.start or not self.end:
            raise ValidationError(u'Błąd!')
        if self.start > self.end:
            raise ValidationError(u'Rezerwacja nie może kończyć się później niż zaczynać http://localhost:8000/admin/hours/reservation/1/')
        if self.end - self.start > datetime.timedelta(days=28):
            raise ValidationError(u'Sprzęt można rezerwować na maksymalnie 28 dni')

        try:
            self.__check_doesnt_overlap_accepted()
            self.__check_doesnt_overlap_mine()

            if self.pk:
                instance = Reservation.objects.get(self.pk)
                self.__check_only_first_accpted(instance)
                self.__check_cant_change_done(instance)
        except NotImplementedError:
            pass

    def create_reservation(self, stuff, user, start, end):
        reservation = Reservation(stuff=stuff, user=user, start=start, end=end)
        reservation.cost = stuff.category.price
        reservation.data = datetime.time.now()
        return reservation

    def confirm_reservation(self, notes=None):
        if notes:
            self.supervisor_notes = notes
        self.status = ReservationStatus.accepted[0]

    def __check_doesnt_overlap_accepted(self):
        """
        Cannot create reservation if overlaps accepted/done one.
        """
        raise NotImplementedError()

    def __check_doesnt_overlap_mine(self):
        """
        Cannot create reservation that overlaps another reservation for
        sam user.
        """
        raise NotImplementedError()

    def __check_only_first_accepted(self, instance):
        """
        If there are two or more overlapping pending reservations,
        only first may be accepted.
        Stuff manager should cancel previous reservations, and then accept selected one
        """
        raise NotImplementedError()

    def __check_cant_change_done(self, instance):
        """
        If reservation is marked as done, it's immutable.
        """
        raise NotImplementedError()


class ReservationAdmin(admin.ModelAdmin):
    list_display = 'stuff', 'user', 'status', 'supervisor_notes', 'start', 'end', 'date'
    search_fields = 'stuff__name', 'user__pk', 'user__email'
    list_filter = 'status', 'start', 'end'


admin.site.register(Reservation, ReservationAdmin)


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

    def create_change(self, user, author, note=None, value=None, reservation=None):
        if reservation and value:
            raise ValidationError(u'Zmiana dotycząca rezerwacji ma automatyczną liczbę godzinek.')
        if reservation:
            value = reservation.cost
        change = SaldoChange(user=user, value=value, author=author, note=note, reservation=reservation)
        user.saldo += value
        return change


admin.site.register(SaldoChange)
