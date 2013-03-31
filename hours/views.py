# -*- coding: utf-8 -*-
import calendar
import datetime
from httplib import BAD_REQUEST
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import Context, loader
from hours.models import Stuff


@login_required
def my_account(request):
    context = __base_context(request)
    template = loader.get_template('my_account.html')
    return HttpResponse(template.render(context))


@login_required()
def stuff(request):
    context = __base_context(request)
    context.update(dict(stuff=Stuff.objects.all(),
                        current='stuff'))
    template = loader.get_template('stuff.html')
    return HttpResponse(template.render(context))


@login_required()
def item(request, id):
    context = __base_context(request)
    context.update(dict(item=Stuff.objects.get(id=id),
                        month=Calendar(request.REQUEST.get('year', None),
                                       request.REQUEST.get('month', None))))
    template = loader.get_template('item.html')
    return HttpResponse(template.render(context))


def my_reservations(request):
    pass


def manage_reservations(request):
    pass


def update_reservation(request):
    pass


def manage_hours(request):
    pass


def __main_pages():
    return (
        {
            'display': u'Moje konto',
            'url': 'index',
        },
        {
            'display': u'Sprzęt',
            'url': 'stuff',
        },
        {
            'display': u'Godzinki',
            'url': 'hours',

        },
    )


def __base_context(request):
    return Context({
        'user': request.user,
        'current': 'index',
        'pages': __main_pages()
    })


class Calendar:
    def __init__(self, year, month):
        if not year and not month:
            self.date = datetime.datetime.now()
        elif year and month:
            self.date = datetime.datetime(year=int(year), month=int(month), day=1)
        else:
            raise BAD_REQUEST

        self.next = add_month(self.date.year, self.date.month, +1)
        self.prev = add_month(self.date.year, self.date.month, -1)

        self.week = [u'Poniedziałek', u'Wtorek', u'Środa', u'Czwartek', u'Piątek', u'Sobota', u'Niedziela']
        self.weeks = chunks(
            (Day(date, self.date.year, self.date.month)
             for date in calendar.Calendar().itermonthdates(self.date.year, self.date.month)), 7)


class Day:
    def __init__(self, date, year, month):
        self.date = date
        self.year = year
        self.month = month

    def view_date(self):
        if self.date.month != self.month:
            return None
        else:
            return self.date


def zero_to_null(l):
    return [None if x == 0 else x for x in l]


def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    l = list(l)
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


def add_month(year, month, delta):
    month += delta
    while month <= 0:
        year -= 1
        month += 12
    while month > 12:
        year += 1
        month -= 12
    return datetime.datetime(year=year, month=month, day=1)