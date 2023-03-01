import pytz
from django.utils import timezone


def convert_seconds_to_hr_min(seconds: int) -> str:
    hr = seconds // (60 * 60)
    mins = (seconds - (hr * 3600)) // 60
    secs = seconds - ((hr * 3600) + (mins * 60))
    time_str = ""
    if hr:
        time_str += f"{hr} Hr{'s' if hr > 1 else ''} "
    if mins:
        time_str += f"{mins} Min{'s' if mins > 1 else ''} "
    if secs:
        time_str += f"{secs} Sec{'s' if secs > 1 else ''} "
    return time_str.strip()


def convert_camel_case_to_python_method_convention(str_: str) -> str:
    action_name = ""
    for id_, letter in enumerate(str_):
        if letter.isupper() and id_:
            action_name += "_"
        action_name += letter.lower()
    return action_name


def date_by_adding_business_days(from_date, add_days):
    business_days_to_add = add_days
    current_date = from_date
    while business_days_to_add > 0:
        current_date += timezone.timedelta(days=1)
        weekday = current_date.weekday()
        if weekday >= 5:  # sunday = 6
            continue
        business_days_to_add -= 1
    return current_date


def convert_to_localtime(utctime) -> timezone.datetime:
    utc = utctime.replace(tzinfo=pytz.UTC)
    localtz = utc.astimezone(timezone.get_current_timezone())
    return localtz


def get_day_suffix(day: int) -> str:
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    return suffix
