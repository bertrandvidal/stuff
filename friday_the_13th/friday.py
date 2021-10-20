#!/usr/bin/env python3

import sys

from datetime import date, timedelta, datetime

def _is_friday(current_date):
    return current_date.weekday() == 4

def _is_13th(current_date):
    return current_date.day == 13

def friday_the_13th(current_date=None):
    current_date = current_date or date.today()
    max_iteration = 100
    while max_iteration > 0:
        print('testing %s' % current_date.strftime("%A %d %B %Y"))
        if _is_friday(current_date) and _is_13th(current_date):
            return current_date.isoformat()
        if not _is_friday(current_date):
            # adjust date to be a Friday
            delta = timedelta(days=4 - current_date.weekday())
            # for Sat and Sun delta.days is < 0 so applying delta would set us
            # to the previous Friday, instead move to the next Friday
            if delta.days < 0:
                delta += timedelta(days=7)
            current_date += delta
        else:
            # we are already a Friday but not a 13th, move on to the next Fiday
            current_date += timedelta(days=7)

        max_iteration -= 1
    return current_date.isoformat()


if __name__ == "__main__":
    start_date = date.today()
    if len(sys.argv) > 1:
        start_date = datetime.strptime(sys.argv[1], '%Y-%m-%d')
    print(friday_the_13th(start_date))
