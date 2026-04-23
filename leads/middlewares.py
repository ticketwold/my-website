from .models import VisitorCount
from django.utils import timezone

class VisitorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.session.get("visited"):
            today = timezone.now().date()

            obj, created = VisitorCount.objects.get_or_create(date=today)
            obj.count += 1
            obj.save()

            request.session["visited"] = True

        response = self.get_response(request)
        return response    