# -*- coding: utf-8 -*-
from datetime import datetime
from django.forms.widgets import SplitDateTimeWidget, HiddenInput, TextInput
from hours.models import Reservation

__author__ = 'rzuk'

from django import forms


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = 'start', 'end', 'user_notes',
        widgets = {
            'start': SplitDateTimeWidget(attrs={'class': 'datepicker'}),
            'end': SplitDateTimeWidget(attrs={'class': 'datepicker'}),
            'stuff': HiddenInput(),
        }

    def save_instance(self, item, user):
        if not self.is_valid():
            return False
        else:
            reservation = self.save(commit=False)
            reservation.user = user
            reservation.stuff = item
            reservation.date = datetime.now()
            reservation.save()
            return True


class ReservationEditionForm(forms.ModelForm):
    class Meta(ReservationForm.Meta):
        model = Reservation
        fields = 'start', 'end', 'user_notes', 'supervisor_notes'

    def __init__(self, *args, **kwargs):
        super(ReservationEditionForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['supervisor_notes'].widget.attrs['readonly'] = True

    def clean_supervisor_notes(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            return instance.supervisor_notes
        else:
            return ''

    def save_instance(self, item, user):
        if not self.is_valid():
            return False
        else:
            reservation = self.save(commit=False)
            reservation.date = datetime.now()
            reservation.save()
            return True


class ReturnSingleStuffForm(forms.Form):

    checked = forms.BooleanField()
    days = forms.IntegerField()
