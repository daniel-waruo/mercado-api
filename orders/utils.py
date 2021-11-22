from dateutil.relativedelta import relativedelta
from django.utils import timezone


def months(start: timezone.datetime, end: timezone.datetime):
    result = []
    while start <= end:
        result.append(start)
        start += relativedelta(months=1)
    return result
