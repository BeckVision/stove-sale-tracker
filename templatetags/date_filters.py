# your_app/templatetags/date_filters.py
from django import template
from datetime import datetime

register = template.Library()

@register.filter
def uzbek_date(value, format_string):
    if not isinstance(value, datetime):
        return value
    uzbek_months = {
        1: 'yanvar', 2: 'fevral', 3: 'mart', 4: 'aprel', 5: 'may', 6: 'iyun',
        7: 'iyul', 8: 'avgust', 9: 'sentyabr', 10: 'oktabr', 11: 'noyabr', 12: 'dekabr'
    }
    uzbek_days = {
        0: 'Dushanba', 1: 'Seshanba', 2: 'Chorshanba', 3: 'Payshanba',
        4: 'Juma', 5: 'Shanba', 6: 'Yakshanba'
    }
    if 'M' in format_string:
        format_string = format_string.replace('M', uzbek_months[value.month])
    if 'l' in format_string:
        format_string = format_string.replace('l', uzbek_days[value.weekday()])
    return value.strftime(format_string)