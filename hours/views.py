# -*- coding: utf-8 -*-
from datetime import datetime, date
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.forms.formsets import formset_factory
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.template import loader, RequestContext
from django.utils.http import urlencode
from hours.forms import ReservationForm, ReservationEditionForm, ReturnSingleStuffForm
from hours.models import Stuff, StuffCategory, Reservation
from hours.utils import Calendar


@login_required
def my_account(request):
    context = __base_context(request)
    template = loader.get_template('my_account.html')
    recent_reservations = Reservation.objects.filter(
        user=request.user
    ).order_by('-date')[:10]
    context.update({
        'recent_reservations': recent_reservations
    })
    return HttpResponse(template.render(context))


@login_required()
def stuff(request):
    context = __base_context(request)
    context.update(dict(stuff=Stuff.objects.all(),
                        categories=StuffCategory.objects.all(),
                        current='stuff'))
    template = loader.get_template('stuff.html')
    return HttpResponse(template.render(context))


@login_required()
def item(request, item_id):
    context = __base_context(request)
    item_obj = Stuff.objects.get(id=item_id)
    if 'create' in request.POST:
        create_form = ReservationForm(request.POST)
        if create_form.save_instance(item=item_obj, user=request.user):
            return HttpResponseRedirect(reverse(item, args=[item_obj.id]))
        else:
            create_form.display = True
    else:
        instance = Reservation(start=_today(0, 0), end=_today(23,59))
        create_form = ReservationForm(instance=instance)
    calendar = Calendar(request.REQUEST.get('year', None),
                        request.REQUEST.get('month', None),
                        request.user)
    reservations = item_obj.reservations_in_month(calendar.date.year, calendar.date.month)
    calendar.apply_reservations(reservations)
    context.update(dict(
        item=item_obj,
        month=calendar,
        reservations=reservations,
        current='stuff',
        create_form=create_form
    ))
    template = loader.get_template('item.html')

    return HttpResponse(template.render(context))


@login_required()
def manage_reservation(request, reservation_id):
    context = __base_context(request)
    instance = Reservation.objects.prefetch_related('stuff').get(pk=reservation_id)
    if instance.is_completed():
        return HttpResponseRedirect(reverse(return_form, args=[instance.id]))
    item_obj = instance.stuff
    if 'edit' in request.POST:
        edit_form = ReservationEditionForm(request.POST, instance=instance)
        if edit_form.save_instance(item=item_obj, user=request.user):
            return HttpResponseRedirect('%s?%s' % (reverse(item, args=[item_obj.id]),
                                                   urlencode({'msg': u'Zapisano zmiany',
                                                              'msg_class': 'alert-success'})))
    else:
        edit_form = ReservationForm(instance=instance)
    calendar = Calendar(request.REQUEST.get('year', instance.start.year),
                        request.REQUEST.get('month', instance.start.month),
                        request.user)
    reservations = item_obj.reservations_in_month(calendar.date.year, calendar.date.month)
    calendar.apply_reservations(reservations)
    context.update(dict(
        item=item_obj,
        month=calendar,
        reservations=reservations,
        reservation=instance,
        current='stuff',
        edit_form=edit_form
    ))
    template = loader.get_template('manage_reservation.html')

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
    return RequestContext(request, {
        'user': request.user,
        'current': 'index',
        'pages': __main_pages(),
        'msg': request.REQUEST.get('msg', None),
        'msg_class': request.REQUEST.get('msg_class', None)
    })


def _today(hour, minute):
    today = date.today()
    return datetime(
        year=today.year,
        month=today.month,
        day=today.day,
        hour=hour,
        minute=minute
    )


@login_required()
def return_form(request, reservation_id):
    reservation = Reservation.objects.get(id=reservation_id)
    single_form = ReturnSingleStuffForm(request.POST or None)
    context = __base_context(request)
    context.update({
        'related_reservations': reservation.related_reservations(),
        'single_form': single_form,
        'form_set': formset_factory(ReturnSingleStuffForm, extra=2)
    })
    template = loader.get_template('return_form.html')
    return HttpResponse(template.render(context))
