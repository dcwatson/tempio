from django.conf import settings


def context_processor(request):
    return {
        "site_name": settings.TEMPIO_SITE_NAME,
    }
