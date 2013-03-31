# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import Context, loader
from hours.models import Stuff, Calendar


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
def item(request, item_id):
    context = __base_context(request)
    calendar = Calendar(request.REQUEST.get('year', None),
                        request.REQUEST.get('month', None),
                        request.user
    )
    item = Stuff.objects.get(id=item_id)
    reservations = item.reservations_in_month(calendar.date.year, calendar.date.month)
    calendar.apply_reservations(reservations)
    context.update(dict(
        item=item,
        month=calendar,
        reservations=reservations,
        current='stuff',
    ))
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
