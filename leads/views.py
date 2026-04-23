from datetime import date
import random

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.db import models
from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.contrib.auth import login as auth_login
from django.shortcuts import redirect, render
from django.core.management import call_command


from .forms import UserSignupForm
from .forms import MainBannerCardForm
from .forms import LeadCreateForm
from .forms import GiftcardPriceForm
from .forms import RegisteredCompanyForm
from .forms import BoardPostForm
from .forms import BoardCommentForm
from .models import FavoriteBanner
from .models import RecentView
from .models import Lead, LeadNote, Payment
from .models import MainBannerCard, GiftcardPrice
from .models import MainAd, RegisteredCompany
from .models import RegisteredCompany
from .models import BoardPost
from .models import Inquiry
from .models import FavoriteCompany, RecentView
from .models import BoardComment
from django.contrib.auth import logout
from django.shortcuts import redirect


# =========================
# Site
# =========================
def site_index(request):
    companies = list(
        RegisteredCompany.objects.filter(is_active=True)
    )
    random.shuffle(companies)
    companies = companies[:12]

    banners = list(
        MainBannerCard.objects.filter(is_active=True)
    )
    random.shuffle(banners)
    banners = banners[:10]

    paper_prices = GiftcardPrice.objects.filter(
        is_active=True,
        kind=GiftcardPrice.Kind.PAPER
    ).order_by("sort", "name")

    mobile_prices = GiftcardPrice.objects.filter(
        is_active=True,
        kind=GiftcardPrice.Kind.MOBILE
    ).order_by("sort", "name")

    paper_price_chunks = [paper_prices[i:i+5] for i in range(0, len(paper_prices), 5)]
    mobile_price_chunks = [mobile_prices[i:i+5] for i in range(0, len(mobile_prices), 5)]

    buy_posts = BoardPost.objects.filter(
        board_type=BoardPost.BoardType.BUY,
        is_active=True
    ).order_by("-created_at")[:5]

    sell_posts = BoardPost.objects.filter(
        board_type=BoardPost.BoardType.SELL,
        is_active=True
    ).order_by("-created_at")[:5]

    price_count = len(paper_prices) + len(mobile_prices)


    return render(request, "site/index.html", {
        "banners": banners,
        "paper_prices": paper_prices,
        "mobile_prices": mobile_prices,
        "companies": companies,
        "active_nav": "home",
        "buy_posts": buy_posts,
        "sell_posts": sell_posts,
        "price_count": price_count,
        "paper_price_chunks": paper_price_chunks,
        "mobile_price_chunks": mobile_price_chunks,
    })


def get_client_ip(request: HttpRequest) -> str | None:
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def landing(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = LeadCreateForm(request.POST)
        if form.is_valid():
            lead: Lead = form.save(commit=False)
            lead.utm_source = request.GET.get("utm_source", "")
            lead.utm_medium = request.GET.get("utm_medium", "")
            lead.utm_campaign = request.GET.get("utm_campaign", "")
            lead.referer = request.META.get("HTTP_REFERER", "")[:2000]
            lead.ip = get_client_ip(request)
            lead.save()
            messages.success(request, "상담 신청이 접수되었습니다. 빠르게 연락드리겠습니다.")
            return redirect("landing_done")
    else:
        form = LeadCreateForm()

    return render(request, "landing.html", {"form": form})


def landing_done(request: HttpRequest) -> HttpResponse:
    return render(request, "landing_done.html")


# =========================
# Admin Login (커스텀)
# =========================
def admin_login(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("adm_dashboard")

    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        password = (request.POST.get("password") or "").strip()
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("adm_dashboard")
        messages.error(request, "아이디/비밀번호가 올바르지 않습니다.")

    return render(request, "adm/login.html")


# =========================
# Admin (/adm) - Dashboard
# =========================
@login_required
def adm_dashboard(request: HttpRequest) -> HttpResponse:
    today = date.today()

    today_leads = Lead.objects.filter(created_at__date=today).count()
    total_leads = Lead.objects.count()

    wait_pay = Payment.objects.filter(status=Payment.Status.WAIT).count()
    done_pay = Payment.objects.filter(status=Payment.Status.DONE).count()

    latest_leads = Lead.objects.order_by("-created_at")[:10]

    return render(request, "adm/dashboard.html", {
        "today_leads": today_leads,
        "total_leads": total_leads,
        "wait_pay": wait_pay,
        "done_pay": done_pay,
        "latest_leads": latest_leads,
        "active_menu": "dashboard",
    })

@login_required
def adm_ads(request):
    ads = MainAd.objects.all().order_by("sort")
    return render(request, "adm/ads.html", {
        "ads": ads,
        "active_menu": "ads",
    })


# =========================
# Admin (/adm) - Leads
# =========================
@login_required
def adm_lead_list(request: HttpRequest) -> HttpResponse:
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()

    qs = Lead.objects.all().order_by("-created_at")
    if q:
        qs = qs.filter(models.Q(name__icontains=q) | models.Q(phone__icontains=q))
    if status:
        qs = qs.filter(status=status)

    return render(request, "adm/lead_list.html", {
        "leads": qs,
        "q": q,
        "status": status,
        "status_choices": Lead.Status.choices,
        "active_menu": "leads",
    })


@login_required
def adm_lead_detail(request: HttpRequest, lead_id: int) -> HttpResponse:
    lead = get_object_or_404(Lead, id=lead_id)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "update_status":
            new_status = request.POST.get("status")
            if new_status in dict(Lead.Status.choices):
                lead.status = new_status
                lead.save(update_fields=["status"])
                messages.success(request, "상태가 변경되었습니다.")
            return redirect("adm_lead_detail", lead_id=lead.id)

        if action == "add_note":
            content = (request.POST.get("content") or "").strip()
            if content:
                LeadNote.objects.create(lead=lead, content=content, created_by=request.user)
                messages.success(request, "메모가 추가되었습니다.")
            return redirect("adm_lead_detail", lead_id=lead.id)

    return render(request, "adm/lead_detail.html", {
        "lead": lead,
        "status_choices": Lead.Status.choices,
        "active_menu": "leads",
    })


# =========================
# Admin (/adm) - Payments
# =========================
@login_required
def adm_payment_list(request: HttpRequest) -> HttpResponse:
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()

    qs = Payment.objects.all().order_by("-created_at")

    if q:
        qs = qs.filter(
            models.Q(order_no__icontains=q) |
            models.Q(name__icontains=q) |
            models.Q(phone__icontains=q)
        )

    if status:
        qs = qs.filter(status=status)

    return render(request, "adm/payment_list.html", {
        "payments": qs,
        "q": q,
        "status": status,
        "status_choices": Payment.Status.choices,
        "active_menu": "payments",
    })


# =========================
# Admin (/adm) - Settings
# =========================
@login_required
def adm_settings(request: HttpRequest) -> HttpResponse:
    tab = request.GET.get("tab", "basic")
    return render(request, "adm/settings.html", {
        "active_tab": tab,
        "active_menu": "settings",
    })

@login_required
def adm_banner_list(request: HttpRequest) -> HttpResponse:
    banners = MainBannerCard.objects.all().order_by("sort")
    return render(request, "adm/banner_list.html", {
        "banners": banners,
        "active_menu": "banners",
        "page_title": "프리미엄 업체 관리",
    })

@login_required
def adm_banner_edit(request: HttpRequest, banner_id: int) -> HttpResponse:
    banner = get_object_or_404(MainBannerCard, id=banner_id)

    if request.method == "POST":
        banner.sort = int(request.POST.get("sort") or banner.sort)
        banner.title = (request.POST.get("title") or "").strip()
        banner.desc = (request.POST.get("desc") or "").strip()
        banner.link_url = (request.POST.get("link_url") or "").strip()
        banner.bg_color = (request.POST.get("bg_color") or "#315efb").strip()
        banner.is_active = (request.POST.get("is_active") == "on")

        if "image" in request.FILES:
            banner.image = request.FILES["image"]

        banner.save()
        messages.success(request, "저장되었습니다.")
        return redirect("adm_banner_list")

    return render(request, "adm/banner_edit.html", {
        "banner": banner,
        "active_menu": "banners",
    })

@login_required
def adm_banner_create(request):
    if request.method == "POST":
        form = MainBannerCardForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "배너가 등록되었습니다.")
            return redirect("adm_banner_list")
    else:
        form = MainBannerCardForm()

    return render(request, "adm/banner_form.html", {
        "form": form,
        "mode": "create",
        "active_menu": "banners",
    })


@login_required
def adm_banner_update(request, banner_id: int):
    obj = get_object_or_404(MainBannerCard, id=banner_id)

    if request.method == "POST":
        form = MainBannerCardForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "배너가 수정되었습니다.")
            return redirect("adm_banner_list")
    else:
        form = MainBannerCardForm(instance=obj)

    return render(request, "adm/banner_form.html", {
        "form": form,
        "mode": "update",
        "obj": obj,
        "active_menu": "banners",
    })


@login_required
def adm_banner_delete(request, banner_id: int):
    obj = get_object_or_404(MainBannerCard, id=banner_id)

    if request.method == "POST":
        obj.delete()
        messages.success(request, "배너가 삭제되었습니다.")
        return redirect("adm_banner_list")

    return render(request, "adm/banner_confirm_delete.html", {
        "obj": obj,
        "active_menu": "banners",
    })

# ===== /adm/prices =====
@login_required
def adm_price_list(request):
    q = request.GET.get("q", "").strip()
    kind = request.GET.get("kind", "").strip()
    active = request.GET.get("active", "").strip()
    latest_price = GiftcardPrice.objects.order_by("-updated_at").first()

    qs = GiftcardPrice.objects.all()

    if q:
        qs = qs.filter(name__icontains=q)

    if kind in dict(GiftcardPrice.Kind.choices):
        qs = qs.filter(kind=kind)

    if active == "1":
        qs = qs.filter(is_active=True)
    elif active == "0":
        qs = qs.filter(is_active=False)

    qs = qs.order_by("kind", "sort", "id")

    return render(request, "adm/price_list.html", {
        "prices": qs,
        "q": q,
        "kind": kind,
        "active": active,
        "kind_choices": GiftcardPrice.Kind.choices,
        "active_menu": "prices",
        "latest_price": latest_price,
    })


@login_required
def adm_price_create(request):
    if request.method == "POST":
        form = GiftcardPriceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "시세가 등록되었습니다.")
            return redirect("adm_price_list")
    else:
        form = GiftcardPriceForm()

    return render(request, "adm/price_form.html", {
        "form": form,
        "mode": "create",
        "active_menu": "prices",
    })


@login_required
def adm_price_update(request, price_id: int):
    obj = get_object_or_404(GiftcardPrice, id=price_id)

    if request.method == "POST":
        form = GiftcardPriceForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "시세가 수정되었습니다.")
            return redirect("adm_price_list")
    else:
        form = GiftcardPriceForm(instance=obj)

    return render(request, "adm/price_form.html", {
        "form": form,
        "mode": "update",
        "obj": obj,
        "active_menu": "prices",
    })


@login_required
def adm_price_delete(request, price_id: int):
    obj = get_object_or_404(GiftcardPrice, id=price_id)

    if request.method == "POST":
        obj.delete()
        messages.success(request, "시세가 삭제되었습니다.")
        return redirect("adm_price_list")

    return render(request, "adm/price_confirm_delete.html", {
        "obj": obj,
        "active_menu": "prices",
    })


@login_required
def adm_company_list(request):
    q = request.GET.get("q", "").strip()
    active = request.GET.get("active", "").strip()

    qs = RegisteredCompany.objects.all()

    if q:
        qs = qs.filter(name__icontains=q)

    if active == "1":
        qs = qs.filter(is_active=True)
    elif active == "0":
        qs = qs.filter(is_active=False)

    qs = qs.order_by("sort", "id")

    return render(request, "adm/company_list.html", {
        "companies": qs,
        "q": q,
        "active": active,
        "active_menu": "companies",
    })


@login_required
def adm_company_create(request):
    if request.method == "POST":
        form = RegisteredCompanyForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "등록업체가 등록되었습니다.")
            return redirect("adm_company_list")
    else:
        form = RegisteredCompanyForm()

    return render(request, "adm/company_form.html", {
        "form": form,
        "mode": "create",
        "active_menu": "companies",
    })


@login_required
def adm_company_update(request, company_id: int):
    obj = get_object_or_404(RegisteredCompany, id=company_id)

    if request.method == "POST":
        form = RegisteredCompanyForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "등록업체가 수정되었습니다.")
            return redirect("adm_company_list")
    else:
        form = RegisteredCompanyForm(instance=obj)

    return render(request, "adm/company_form.html", {
        "form": form,
        "mode": "update",
        "obj": obj,
        "active_menu": "companies",
    })


@login_required
def adm_company_delete(request, company_id: int):
    obj = get_object_or_404(RegisteredCompany, id=company_id)

    if request.method == "POST":
        obj.delete()
        messages.success(request, "등록업체가 삭제되었습니다.")
        return redirect("adm_company_list")

    return render(request, "adm/company_confirm_delete.html", {
        "obj": obj,
        "active_menu": "companies",
    })


def prices_page(request):
    paper_prices = GiftcardPrice.objects.filter(
        is_active=True,
        kind=GiftcardPrice.Kind.PAPER
    ).order_by("sort", "name")

    mobile_prices = GiftcardPrice.objects.filter(
        is_active=True,
        kind=GiftcardPrice.Kind.MOBILE
    ).order_by("sort", "name")

    return render(request, "site/prices.html", {
        "paper_prices": paper_prices,
        "mobile_prices": mobile_prices,
        "active_nav": "prices",
    })

def shopping_page(request):
    shopping = MainBannerCard.objects.filter(is_active=True).order_by("sort", "-id")

    return render(request, "site/shopping.html", {
        "shopping": shopping,
        "active_nav": "shopping",
    })


def companies_page(request):
    companies = RegisteredCompany.objects.filter(
        is_active=True
    ).order_by("sort", "-id")

    return render(request, "site/companies.html", {
        "companies": companies,
        "active_nav": "companies",
    })

def community_page(request):
    return render(request, "site/community.html", {
        "active_nav": "community",
    })

def user_login(request):
    if request.user.is_authenticated:
        return redirect("site_index")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, "로그인되었습니다.")
            return redirect("site_index")
    else:
        form = AuthenticationForm()

    form.fields["username"].widget.attrs.update({
        "class": "inputx",
        "placeholder": "아이디"
    })
    form.fields["password"].widget.attrs.update({
        "class": "inputx",
        "placeholder": "비밀번호"
    })

    return render(request, "site/login.html", {
        "form": form,
    })


def signup(request):
    if request.user.is_authenticated:
        return redirect("site_index")

    if request.method == "POST":
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data["first_name"]
            user.email = form.cleaned_data["email"]
            user.save()

            auth_login(request, user)
            messages.success(request, "회원가입이 완료되었습니다.")
            return redirect("site_index")
        else:
            messages.error(request, "입력값을 다시 확인해주세요.")
    else:
        form = UserSignupForm()

    return render(request, "site/signup.html", {"form": form}) 


def user_logout(request):
    auth_logout(request)
    messages.success(request, "로그아웃되었습니다.")
    return redirect("site_index")

@login_required
def mypage(request):
    favorites = FavoriteCompany.objects.filter(
        user=request.user
    ).select_related("company")

    recent = RecentView.objects.filter(
        user=request.user
    ).select_related("company").order_by("-viewed_at")[:5]

    return render(request, "site/mypage.html", {
        "favorites": favorites,
        "recent": recent,
    })

def company_detail(request, company_id):
    company = get_object_or_404(RegisteredCompany, id=company_id, is_active=True)

    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = FavoriteCompany.objects.filter(
            user=request.user,
            company=company
        ).exists()

        RecentView.objects.filter(user=request.user, company=company).delete()
        RecentView.objects.create(user=request.user, company=company)

    return render(request, "site/company_detail.html", {
        "company": company,
        "is_favorite": is_favorite,
        "active_nav": "companies",
    })

@login_required
def adm_board_list(request):
    board_type = request.GET.get("board_type", "").strip()
    q = request.GET.get("q", "").strip()

    qs = BoardPost.objects.all().order_by("-created_at")

    if board_type:
        qs = qs.filter(board_type=board_type)
    if q:
        qs = qs.filter(title__icontains=q)

    return render(request, "adm/board_list.html", {
        "posts": qs,
        "board_type": board_type,
        "q": q,
        "board_choices": BoardPost.BoardType.choices,
        "active_menu": "boards",
    })


@login_required
def adm_board_create(request):
    if request.method == "POST":
        form = BoardPostForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.author = request.user
            obj.save()
            messages.success(request, "게시글이 등록되었습니다.")
            return redirect("adm_board_list")
    else:
        form = BoardPostForm()

    return render(request, "adm/board_form.html", {
        "form": form,
        "mode": "create",
        "active_menu": "boards",
    })


@login_required
def adm_board_update(request, post_id: int):
    obj = get_object_or_404(BoardPost, id=post_id)

    if request.method == "POST":
        form = BoardPostForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "게시글이 수정되었습니다.")
            return redirect("adm_board_list")
    else:
        form = BoardPostForm(instance=obj)

    return render(request, "adm/board_form.html", {
        "form": form,
        "mode": "update",
        "obj": obj,
        "active_menu": "boards",
    })


@login_required
def adm_board_delete(request, post_id: int):
    obj = get_object_or_404(BoardPost, id=post_id)

    if request.method == "POST":
        obj.delete()
        messages.success(request, "게시글이 삭제되었습니다.")
        return redirect("adm_board_list")

    return render(request, "adm/board_confirm_delete.html", {
        "obj": obj,
        "active_menu": "boards",
    })

def buy_board_page(request):
    category = request.GET.get("category", "").strip()

    posts = BoardPost.objects.filter(
        board_type=BoardPost.BoardType.BUY,
        is_active=True
    )

    if category:
        posts = posts.filter(category=category)

    posts = posts.order_by("-created_at")

    return render(request, "site/board_list.html", {
        "posts": posts,
        "page_title": "상품권 구매게시판",
        "active_nav": "community",
        "board_type": "buy",
        "category": category,
        "category_choices": BoardPost.Category.choices,
    })

@login_required
def board_write(request, board_type):
    board_type = board_type.lower()

    if board_type not in ["buy", "sell"]:
        return redirect("community_page")

    if request.method == "POST":
        form = BoardPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user

            if board_type == "buy":
                post.board_type = BoardPost.BoardType.BUY
            elif board_type == "sell":
                post.board_type = BoardPost.BoardType.SELL

            post.save()
            return redirect("board_detail", board_type=board_type, pk=post.pk)
    else:
        form = BoardPostForm()

    return render(request, "site/board_write.html", {
        "form": form,
        "board_type": board_type,
    })


@login_required
def board_edit(request, board_type, pk):
    board_type = board_type.lower()

    if board_type not in ["buy", "sell"]:
        return redirect("community_page")

    post = get_object_or_404(BoardPost, pk=pk, author=request.user)

    if request.method == "POST":
        form = BoardPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            updated_post = form.save(commit=False)

            if board_type == "buy":
                updated_post.board_type = BoardPost.BoardType.BUY
            elif board_type == "sell":
                updated_post.board_type = BoardPost.BoardType.SELL

            updated_post.author = request.user
            updated_post.save()
            return redirect("board_detail", board_type=board_type, pk=updated_post.pk)
    else:
        form = BoardPostForm(instance=post)

    return render(request, "site/board_edit.html", {
        "form": form,
        "post": post,
        "board_type": board_type,
    })

def sell_board_page(request):
    category = request.GET.get("category", "").strip()

    posts = BoardPost.objects.filter(
        board_type=BoardPost.BoardType.SELL,
        is_active=True
    )

    if category:
        posts = posts.filter(category=category)

    posts = posts.order_by("-created_at")

    return render(request, "site/board_list.html", {
        "posts": posts,
        "page_title": "상품권 판매게시판",
        "active_nav": "community",
        "board_type": "sell",
        "category": category,
        "category_choices": BoardPost.Category.choices,
    })


@login_required
def my_inquiries(request):
    inquiries = Inquiry.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'site/my_inquiries.html', {
        'inquiries': inquiries
    })


@login_required
def toggle_favorite(request, pk):
    company = get_object_or_404(RegisteredCompany, pk=pk)

    favorite = FavoriteCompany.objects.filter(
        user=request.user,
        company=company
    ).first()

    if favorite:
        favorite.delete()
        messages.success(request, "즐겨찾기에서 제거되었습니다.")
    else:
        FavoriteCompany.objects.create(
            user=request.user,
            company=company
        )
        messages.success(request, "즐겨찾기에 추가되었습니다.")

    return redirect("company_detail", company_id=company.id)

@login_required
def my_page(request):
    favorites = FavoriteCompany.objects.filter(user=request.user)
    recent = RecentView.objects.filter(user=request.user).order_by('-viewed_at')[:10]

    return render(request, 'site/mypage.html', {
        'favorites': favorites,
        'recent': recent
    })


class CustomPasswordChangeView(auth_views.PasswordChangeView):
    template_name = "site/password_change.html"
    success_url = reverse_lazy("password_change_done")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        form.fields["old_password"].widget.attrs.update({
            "class": "form-control form-control-lg",
            "placeholder": "현재 비밀번호를 입력하세요"
        })
        form.fields["new_password1"].widget.attrs.update({
            "class": "form-control form-control-lg",
            "placeholder": "새 비밀번호를 입력하세요"
        })
        form.fields["new_password2"].widget.attrs.update({
            "class": "form-control form-control-lg",
            "placeholder": "새 비밀번호를 다시 입력하세요"
        })

        return form
    
def board_detail(request, board_type, pk):
    board_map = {
        "buy": BoardPost.BoardType.BUY,
        "sell": BoardPost.BoardType.SELL,
    }

    if board_type not in board_map:
        return redirect("community_page")

    post = get_object_or_404(
        BoardPost,
        pk=pk,
        board_type=board_map[board_type],
        is_active=True,
    )

    comment_form = BoardCommentForm()

    return render(request, "site/board_detail.html", {
        "post": post,
        "board_type": board_type,
        "active_nav": "community",
        "comment_form": comment_form,
    })

@login_required
def board_edit(request, board_type, pk):
    post = get_object_or_404(BoardPost, pk=pk, author=request.user)

    if request.method == "POST":
        form = BoardPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            updated_post = form.save(commit=False)

            if board_type == "buy":
                updated_post.board_type = BoardPost.BoardType.BUY
            elif board_type == "sell":
                updated_post.board_type = BoardPost.BoardType.SELL

            updated_post.author = request.user
            updated_post.save()

            return redirect("board_detail", board_type=board_type, pk=updated_post.pk)
    else:
        form = BoardPostForm(instance=post)

    return render(request, "site/board_edit.html", {
        "form": form,
        "post": post,
        "board_type": board_type,
    })


@login_required
def board_delete(request, board_type, pk):
    board_map = {
        "buy": BoardPost.BoardType.BUY,
        "sell": BoardPost.BoardType.SELL,
    }

    if board_type not in board_map:
        return redirect("community_page")

    post = get_object_or_404(
        BoardPost,
        pk=pk,
        board_type=board_map[board_type],
        is_active=True,
    )

    if post.author != request.user:
        messages.error(request, "본인 글만 삭제할 수 있습니다.")
        return redirect("board_detail", board_type=board_type, pk=post.pk)

    if request.method == "POST":
        post.delete()
        messages.success(request, "게시글이 삭제되었습니다.")

        if board_type == "buy":
            return redirect("buy_board_page")
        elif board_type == "sell":
            return redirect("sell_board_page")

    return render(request, "site/board_delete.html", {
        "post": post,
        "board_type": board_type,
        "active_nav": "community",
    })

@login_required
def board_comment_create(request, board_type, pk):
    board_map = {
        "buy": BoardPost.BoardType.BUY,
        "sell": BoardPost.BoardType.SELL,
    }

    if board_type not in board_map:
        return redirect("community_page")

    post = get_object_or_404(
        BoardPost,
        pk=pk,
        board_type=board_map[board_type],
        is_active=True,
    )

    if request.method == "POST":
        form = BoardCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, "댓글이 등록되었습니다.")

    return redirect("board_detail", board_type=board_type, pk=post.pk)

@login_required
def board_comment_delete(request, board_type, pk, comment_id):
    board_map = {
        "buy": BoardPost.BoardType.BUY,
        "sell": BoardPost.BoardType.SELL,
    }

    if board_type not in board_map:
        return redirect("community_page")

    post = get_object_or_404(
        BoardPost,
        pk=pk,
        board_type=board_map[board_type],
        is_active=True,
    )

    comment = get_object_or_404(BoardComment, id=comment_id, post=post)

    if comment.author != request.user:
        messages.error(request, "본인 댓글만 삭제할 수 있습니다.")
        return redirect("board_detail", board_type=board_type, pk=post.pk)

    if request.method == "POST":
        comment.delete()
        messages.success(request, "댓글이 삭제되었습니다.")

    return redirect("board_detail", board_type=board_type, pk=post.pk)


@login_required
def adm_price_fetch(request):
    if request.method == "POST":
        try:
            call_command("fetch_wooticket_prices")
            messages.success(request, "wooticket 시세를 불러왔습니다.")
        except Exception as e:
            messages.error(request, f"시세 불러오기 실패: {e}")

    return redirect("adm_price_list")

@login_required
def adm_price_toggle(request, price_id):
    if request.method == "POST":
        price = get_object_or_404(GiftcardPrice, id=price_id)
        price.is_active = not price.is_active
        price.save(update_fields=["is_active", "updated_at"])

        state = "노출" if price.is_active else "숨김"
        messages.success(request, f"{price.name} 상태가 '{state}'로 변경되었습니다.")

    return redirect("adm_price_list")

def shopping_detail(request, shopping_id):
    shopping = get_object_or_404(MainBannerCard, id=shopping_id, is_active=True)

    return render(request, "site/shopping_detail.html", {
        "shopping": shopping,
        "active_nav": "shopping",
    })

def admin_logout_view(request):
    logout(request)
    return redirect("admin_login")

def customer_page(request):
    return render(request, "site/customer.html", {
        "active_nav": "customer",
    })

def board_create(request, board_type):
    if request.method == "POST":
        form = BoardPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.category = board_type
            post.save()
            return redirect("board_detail", board_type=board_type, pk=post.id)
    else:
        form = BoardPostForm()

    return render(request, "board_form.html", {"form": form})

@login_required
def toggle_banner_favorite(request, pk):
    banner = get_object_or_404(MainBannerCard, pk=pk)

    obj, created = FavoriteBanner.objects.get_or_create(
        user = request.user,
        banner = banner
    )

    if not created:
        obj.delete()

    return redirect("shopping_detail", pk=pk)