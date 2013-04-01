# -*- coding: utf-8 -*-
import calendar
import datetime
from httplib import BAD_REQUEST

from django.contrib import admin
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
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
    supervisor_notes = dm.TextField(blank=True, verbose_name='uwagi')
    date = dm.DateTimeField(verbose_name='data rezerwacji')

    def clean(self):
        if self.start > self.end:
            raise ValidationError(u'Rezerwacja nie może kończyć się później niż zaczynać http://localhost:8000/admin/hours/reservation/1/')
        if self.end - self.start > datetime.timedelta(days=28):
            raise ValidationError(u'Sprzęt można rezerwować na maksymalnie 28 dni')

    def create_reservation(self, stuff, user, start, end):
        reservation = Reservation(stuff=stuff, user=user, start=start, end=end)
        reservation.cost = stuff.category.price.value
        reservation.data = datetime.time.now()
        return reservation

    def confirm_reservation(self, notes=None):
        if notes:
            self.supervisor_notes = notes
        self.status = ReservationStatus.accepted[0]


class ReservationAdmin(admin.ModelAdmin):
    list_display = 'stuff', 'user', 'status', 'supervisor_notes', 'start', 'end', 'date'
    search_fields = 'stuff__name', 'user__pk', 'user__email'
    list_filter = 'status', 'start', 'end'


admin.site.register(Reservation, ReservationAdmin)


class Price(dm.Model):
    class Meta:
        verbose_name = u'cena'
        verbose_name_plural = u'ceny'

    value = dm.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0)])

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


class Calendar:
    def __init__(self, year, month, user=None):
        if not year and not month:
            self.date = datetime.datetime.now()
        elif year and month:
            self.date = datetime.datetime(year=int(year), month=int(month), day=1)
        else:
            raise BAD_REQUEST

        self.user = user

        self.next = Calendar.add_month(self.date.year, self.date.month, +1)
        self.prev = Calendar.add_month(self.date.year, self.date.month, -1)

        self.week = [u'Poniedziałek', u'Wtorek', u'Środa', u'Czwartek', u'Piątek', u'Sobota', u'Niedziela']
        self.days = []
        self.weeks = []
        self.__days_dict = {}
        self.__generate_days()

    def __generate_days(self):
        for date in calendar.Calendar().itermonthdates(self.date.year, self.date.month):
            day = Day(date, self)
            self.days.append(day)
            if day.view_date():
                self.__days_dict[day.view_date().day] = day
        self.weeks = chunks(self.days, 7)

    def apply_reservations(self, reservations):
        for day in self.days:
            for reservation in reservations:
                if reservation.start.date() <= day.date <= reservation.end.date():
                    day.reservations.append(reservation)


    @staticmethod
    def add_month(year, month, delta):
        month += delta
        while month <= 0:
            year -= 1
            month += 12
        while month > 12:
            year += 1
            month -= 12
        return datetime.datetime(year=year, month=month, day=1)


class Day:
    def __init__(self, date, calendar):
        self.date = date
        self.calendar = calendar
        self.year = calendar.date.year
        self.month = calendar.date.month
        self.reservations = []

    def view_date(self):
        if self.date.month != self.month:
            return None
        else:
            return self.date

    def get_class(self):
        if not self.view_date():
            return None

        my_reservation_dict = {
            'U': 'my_pending',
            'A': 'my_accepted',
            'C': 'free',
            'D': 'free',
        }
        reservation_dict = {
            'U': 'pending',
            'A': 'accepted',
            'C': 'free',
            'D': 'free',
        }

        for reservation in self.reservations:
            if reservation.user == self.calendar.user:
                return my_reservation_dict[reservation.status]
            else:
                return reservation_dict[reservation.status]

        return 'free'


def zero_to_null(l):
    return [None if x == 0 else x for x in l]


def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    l = list(l)
    for i in xrange(0, len(l), n):
        yield l[i:i + n]