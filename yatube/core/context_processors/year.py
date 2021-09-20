from django.utils import timezone as tz


def year(request):
    now = tz.now()
    return {'year': int(now.strftime("%Y"))}
