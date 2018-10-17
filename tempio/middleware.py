from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string

import datetime


def AnonymousUserMiddleware(get_response):
    def middleware(request):
        User = get_user_model()
        send_cookie = False
        if request.user.is_anonymous:
            username = request.COOKIES.get(settings.TEMPIO_COOKIE_NAME, get_random_string(40))
            try:
                request.user = User.objects.get(username=username)
            except User.DoesNotExist:
                request.user = User.objects.create_user(username)
                send_cookie = True
        response = get_response(request)
        if send_cookie:
            expires = datetime.date.today() + datetime.timedelta(days=settings.TEMPIO_COOKIE_EXPIRATION)
            response.set_cookie(settings.TEMPIO_COOKIE_NAME, username, expires=expires, httponly=True)
        return response
    return middleware
