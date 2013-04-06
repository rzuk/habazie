import calendar
import datetime

__author__ = 'rzuk'


def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    l = list(l)
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


def zero_to_null(l):
    return [None if x == 0 else x for x in l]


class Calendar:
    def __init__(self, year, month, user=None):
        if not year and not month:
            self.date = datetime.datetime.now()
        elif year and month:
            self.date = datetime.datetime(year=int(year), month=int(month), day=1)
        else:
            raise Exception('all or none of year, month may be specified')

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

    def get_classes(self):
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

        classes = []
        for reservation in self.reservations:
            if reservation.user == self.calendar.user:
                classes.append(my_reservation_dict[reservation.status])
            else:
                classes.append(reservation_dict[reservation.status])

        if classes:
            return ' '.join(classes)
        else:
            return 'free'