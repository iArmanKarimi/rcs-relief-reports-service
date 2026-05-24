from functools import wraps
from django.http import HttpResponseForbidden
from django.conf import settings


def require_api_key(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.headers.get("X-API-KEY") != settings.BALE_BOT_API_KEY:
            return HttpResponseForbidden("Unauthorized")
        return view_func(request, *args, **kwargs)
    return _wrapped_view
