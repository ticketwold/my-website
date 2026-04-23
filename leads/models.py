from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

class Lead(models.Model):
    class Status(models.TextChoices):
        NEW = "NEW", "신규"
        CONTACTED = "CONTACTED", "연락완료"
        IN_PROGRESS = "IN_PROGRESS", "진행중"
        DONE = "DONE", "완료"
        HOLD = "HOLD", "보류"
        SPAM = "SPAM", "스팸"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leads"
)

    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    memo = models.TextField(blank=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)

    utm_source = models.CharField(max_length=100, blank=True)
    utm_medium = models.CharField(max_length=100, blank=True)
    utm_campaign = models.CharField(max_length=100, blank=True)
    referer = models.URLField(blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.phone})"


class LeadNote(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="notes")
    content = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Note for Lead#{self.lead_id}"
    
class Payment(models.Model):
    class Status(models.TextChoices):
        WAIT = "WAIT", "대기"
        DONE = "DONE", "완료"
        CANCELED = "CANCELED", "취소"

    order_no = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    amount = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.WAIT)
    memo = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.order_no} {self.name} {self.amount}"


class MainBannerCard(models.Model):
    title = models.CharField("업체명", max_length=100)
    desc = models.TextField("설명", blank=True)

    # ⭐ 추가
    extra_desc = models.TextField("부가설명", blank=True)

    link_url = models.URLField("바로가기 링크", blank=True)

    phone = models.CharField("연락처", max_length=30, blank=True)
    business_number = models.CharField("사업자등록번호", max_length=100, blank=True)
    ecommerce_number = models.CharField("통신판매업 신고번호", max_length=100, blank=True)
    agency = models.CharField("등록기관", max_length=100, blank=True)
    office_address = models.CharField("영업소", max_length=200, blank=True)

    is_active = models.BooleanField("노출 여부", default=True)
    sort = models.IntegerField("정렬 순서", default=1)

    def __str__(self):
        return self.title

class MainAd(models.Model):
    title = models.CharField(max_length=50)
    desc = models.CharField(max_length=100, blank=True)

    image = models.ImageField(upload_to="ads/", blank=True, null=True)
    link_url = models.URLField(blank=True)

    is_active = models.BooleanField(default=True)
    sort = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f"[{self.sort}] {self.title}"
    

class GiftPrice(models.Model):

    CATEGORY = (
        ("paper", "지류"),
        ("mobile", "모바일"),
    )

    category = models.CharField(max_length=10, choices=CATEGORY)
    name = models.CharField(max_length=100)

    buy_rate = models.DecimalField(max_digits=5, decimal_places=2)
    sell_rate = models.DecimalField(max_digits=5, decimal_places=2)

    sort = models.IntegerField(default=1)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
class GiftcardPrice(models.Model):
    class Kind(models.TextChoices):
        PAPER = "PAPER", "지류(종이)"
        MOBILE = "MOBILE", "모바일"

    name = models.CharField(max_length=50, verbose_name="상품권명")
    kind = models.CharField(max_length=10, choices=Kind.choices, verbose_name="구분")

    face_value = models.PositiveIntegerField(default=0, verbose_name="액면가")

    buy_price = models.PositiveIntegerField(default=0, verbose_name="매입가")
    buy_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="매입 퍼센트")

    sell_price = models.PositiveIntegerField(default=0, verbose_name="판매가")
    sell_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="판매 퍼센트")

    is_active = models.BooleanField(default=True, verbose_name="노출 여부")
    sort = models.PositiveSmallIntegerField(default=1, verbose_name="정렬순서")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_kind_display()})"
    

class RegisteredCompany(models.Model):
    name = models.CharField(max_length=50)
    desc = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to="companies/", blank=True, null=True)

    phone = models.CharField(max_length=30, blank=True)
    link_url = models.URLField(blank=True)

    reg_number = models.CharField("등록번호", max_length=100, blank=True)
    biz_number = models.CharField("사업자등록번호", max_length=100, blank=True)
    ecommerce_number = models.CharField("통신판매업 신고번호", max_length=100, blank=True)
    agency_name = models.CharField("등록기관", max_length=100, blank=True)
    office_address = models.CharField("영업소", max_length=200, blank=True)

    detail_content = models.TextField("상세설명", blank=True)
    warning_text = models.TextField("주의사항", blank=True)

    is_active = models.BooleanField(default=True)
    sort = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return self.name
    
class BoardPost(models.Model):
    class BoardType(models.TextChoices):
        BUY = "BUY", "구매게시판"
        SELL = "SELL", "판매게시판"

    class Category(models.TextChoices):
        DEPARTMENT = "department", "백화점"
        GIFT = "gift", "상품권"
        ETC = "etc", "기타"

    board_type = models.CharField(max_length=20, choices=BoardType.choices)

    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.ETC
    )

    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)

    giftcard_type = models.CharField("상품권 종류", max_length=100, blank=True)
    face_value = models.IntegerField("상품권 금액", default=0)
    price = models.IntegerField("희망가격", default=0)
    available_date = models.DateField("거래 가능일", null=True, blank=True)

    image = models.ImageField(upload_to="board/", blank=True, null=True)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="board_posts"
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.board_type}] {self.title}"

class BoardComment(models.Model):
    post = models.ForeignKey(
        "BoardPost",
        on_delete=models.CASCADE,
        related_name="comments"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="board_comments"
    )
    content = models.TextField("댓글 내용")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.author} - {self.post_id}"
    

class Inquiry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

class FavoriteCompany(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company = models.ForeignKey('RegisteredCompany', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'company')

    def __str__(self):
        return f"{self.user} - {self.company}"


class RecentView(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company = models.ForeignKey('RegisteredCompany', on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.company}"

class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    shopping = models.ForeignKey("MainBannerCard", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "shopping")

class VisitorCount(models.Model):
    date = models.DateField(unique=True)
    count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.date} - {self.count}"
    
class FavoriteBanner(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    banner = models.ForeignKey("MainBannerCard", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "banner")