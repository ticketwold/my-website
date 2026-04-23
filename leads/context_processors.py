from .models import FavoriteCompany, RecentView, VisitorCount
from django.utils import timezone
from django.db.models import Sum


def side_company_box(request):
    if not request.user.is_authenticated:
        return {
            "side_favorites": [],
            "side_recent_companies": [],
        }

    favorites = (
        FavoriteCompany.objects
        .filter(user=request.user)
        .select_related("company")
        .order_by("-created_at")[:5]
    )

    recent = (
        RecentView.objects
        .filter(user=request.user)
        .select_related("company")
        .order_by("-viewed_at")[:5]
    )

    return {
        "side_favorites": favorites,
        "side_recent_companies": recent,
    }

def visitor_count(request):
    today = timezone.now().date()

    today_obj = VisitorCount.objects.filter(date=today).first()
    today_count = today_obj.count if today_obj else 0

    total_count = VisitorCount.objects.aggregate(total=Sum("count"))["total"] or 0

    return{
        'today_visitors':today_count,
        'total_visitors':total_count,
    }