from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # 랜딩
    path("", views.site_index, name="site_index"),
    path("landing/", views.landing, name="landing"),

    # 관리자 로그인
    path("admin-login/", auth_views.LoginView.as_view(template_name="adm/login.html"), name="admin_login"),
    path("admin-logout/", views.admin_logout_view, name="admin_logout"),

    # ✅ 새 어드민 (/adm)
    path("adm/", views.adm_dashboard, name="adm_dashboard"),
    path("adm/payments/", views.adm_payment_list, name="adm_payment_list"),
    path("adm/settings/", views.adm_settings, name="adm_settings"),
    path("adm/leads/", views.adm_lead_list, name="adm_lead_list"),
    path("adm/leads/<int:lead_id>/", views.adm_lead_detail, name="adm_lead_detail"),

    # 배너
    path("adm/banners/", views.adm_banner_list, name="adm_banner_list"),
    path("adm/banners/<int:banner_id>/", views.adm_banner_edit, name="adm_banner_edit"),

    # 상품권
    path("adm/prices/", views.adm_price_list, name="adm_price_list"),
    path("adm/prices/new/", views.adm_price_create, name="adm_price_create"),
    path("adm/prices/<int:price_id>/edit/", views.adm_price_update, name="adm_price_update"),
    path("adm/prices/<int:price_id>/delete/", views.adm_price_delete, name="adm_price_delete"),
    path("adm/prices/fetch/", views.adm_price_fetch, name="adm_price_fetch"),
    path("adm/prices/<int:price_id>/toggle/", views.adm_price_toggle, name="adm_price_toggle"),
    path("prices/", views.prices_page, name="prices_page"),
    path("adm/ads/", views.adm_ads, name="adm_ads"),

    path("adm/companies/", views.adm_company_list, name="adm_company_list"),
    path("adm/companies/new/", views.adm_company_create, name="adm_company_create"),
    path("adm/companies/<int:company_id>/edit/", views.adm_company_update, name="adm_company_update"),
    path("adm/companies/<int:company_id>/delete/", views.adm_company_delete, name="adm_company_delete"),

    path("prices/", views.prices_page, name="prices_page"),
    path("companies/", views.companies_page, name="companies_page"),
    path("shopping/", views.shopping_page, name="shopping_page"),
    path("community/", views.community_page, name="community_page"),
    path("shopping/<int:shopping_id>/", views.shopping_detail, name="shopping_detail"),
    path("shopping/<int:pk>/favorite/", views.toggle_banner_favorite, name="toggle_banner_favorite"),

    path("adm/banners/", views.adm_banner_list, name="adm_banner_list"),
    path("adm/banners/new/", views.adm_banner_create, name="adm_banner_create"),
    path("adm/banners/<int:banner_id>/edit/", views.adm_banner_update, name="adm_banner_update"),
    path("adm/banners/<int:banner_id>/delete/", views.adm_banner_delete, name="adm_banner_delete"),

    path("login/", views.user_login, name="user_login"),
    path("signup/", views.signup, name="signup"),
    path("logout/", views.user_logout, name="user_logout"),

    path("mypage/", views.mypage, name="mypage"),
    path("companies/<int:company_id>/", views.company_detail, name="company_detail"),
    path("mypage/inquiries/", views.my_inquiries, name="my_inquiries"),

    path("adm/boards/", views.adm_board_list, name="adm_board_list"),
    path("adm/boards/new/", views.adm_board_create, name="adm_board_create"),
    path("adm/boards/<int:post_id>/edit/", views.adm_board_update, name="adm_board_update"),
    path("adm/boards/<int:post_id>/delete/", views.adm_board_delete, name="adm_board_delete"),

    path("board/buy/", views.buy_board_page, name="buy_board_page"),
    path("board/sell/", views.sell_board_page, name="sell_board_page"),
    path("board/<str:board_type>/<int:pk>/", views.board_detail, name="board_detail"),
    path("board/<str:board_type>/<int:pk>/edit/", views.board_edit, name="board_edit"),
    path("board/<str:board_type>/<int:pk>/delete/", views.board_delete, name="board_delete"),
    path("board/<str:board_type>/write/", views.board_write, name="board_write"),

    path('password_change_done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='site/password_change_done.html'
        ), name='password_change_done'),
    path('password_change/', views.CustomPasswordChangeView.as_view(), name='password_change'),

    path("favorite/toggle/<int:pk>/", views.toggle_favorite, name="toggle_favorite"),
    path("board/<str:board_type>/<int:pk>/comment/", views.board_comment_create, name="board_comment_create"),
    path("board/<str:board_type>/<int:pk>/comment/<int:comment_id>/delete/", views.board_comment_delete, name="board_comment_delete"),

    path("adm/prices/fetch/", views.adm_price_fetch, name="adm_price_fetch"),
    path("customer/", views.customer_page, name="customer_page"),
]