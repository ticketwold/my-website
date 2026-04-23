from django import forms

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import MainBannerCard
from .models import Lead
from .models import GiftcardPrice
from .models import RegisteredCompany
from .models import BoardPost
from .models import BoardComment

class LeadCreateForm(forms.ModelForm):
    privacy_agree = forms.BooleanField(required=True, label="개인정보 수집·이용 동의")

    class Meta:
        model = Lead
        fields = ["name", "phone", "memo"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "이름"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "연락처"}),
            "memo": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "문의 내용(선택)"}),
        }

class GiftcardPriceForm(forms.ModelForm):
    class Meta:
        model = GiftcardPrice
        fields = [
            "kind",
            "name",
            "face_value",
            "buy_price",
            "buy_rate",
            "sell_price",
            "sell_rate",
            "is_active",
            "sort",
        ]
        widgets = {
            "kind": forms.Select(attrs={"class": "form-select"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "face_value": forms.NumberInput(attrs={"class": "form-control"}),
            "buy_price": forms.NumberInput(attrs={"class": "form-control"}),
            "buy_rate": forms.NumberInput(attrs={"class": "form-control"}),
            "sell_price": forms.NumberInput(attrs={"class": "form-control"}),
            "sell_rate": forms.NumberInput(attrs={"class": "form-control"}),
            "sort": forms.NumberInput(attrs={"class": "form-control"}),
        }

class RegisteredCompanyForm(forms.ModelForm):
    class Meta:
        model = RegisteredCompany
        fields = [
            "name", "desc", "image", "phone", "link_url",
            "ecommerce_number", "biz_number", "agency_name", "office_address",
            "detail_content", "warning_text",
            "is_active", "sort"
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "inputx", "placeholder": "업체명"}),
            "desc": forms.Textarea(attrs={"class": "inputx", "rows": 3, "placeholder": "짧은 소개"}),
            "phone": forms.TextInput(attrs={"class": "inputx", "placeholder": "전화번호"}),
            "link_url": forms.URLInput(attrs={"class": "inputx", "placeholder": "외부 홈페이지(선택)"}),
            "ecommerce_number": forms.TextInput(attrs={"class": "inputx", "placeholder": "통신판매업"}),
            "biz_number": forms.TextInput(attrs={"class": "inputx", "placeholder": "사업자등록번호"}),
            "agency_name": forms.TextInput(attrs={"class": "inputx", "placeholder": "등록기관"}),
            "office_address": forms.TextInput(attrs={"class": "inputx", "placeholder": "영업소 주소"}),
            "detail_content": forms.Textarea(attrs={"class": "inputx", "rows": 10, "placeholder": "상세 설명"}),
            "warning_text": forms.Textarea(attrs={"class": "inputx", "rows": 5, "placeholder": "주의사항"}),
            "sort": forms.NumberInput(attrs={"class": "inputx"}),
        }


class MainBannerCardForm(forms.ModelForm):
    class Meta:
        model = MainBannerCard
        fields = [
            "title",
            "desc",
            "extra_desc",  # ⭐ 추가
            "link_url",
            "phone",
            "business_number",
            "ecommerce_number",
            "agency",
            "office_address",
            "is_active",
            "sort",
        ]
        labels = {
            "title": "업체명",
            "desc": "설명",
            "extra_desc": "부가설명",  # ⭐
            "link_url": "바로가기 링크",
            "phone": "연락처",
            "business_number": "사업자등록번호",
            "ecommerce_number": "통신판매업 신고번호",
            "agency": "등록기관",
            "office_address": "영업소",
            "is_active": "노출 여부",
            "sort": "정렬 순서",
        }
        widgets = {
            "title": forms.TextInput(attrs={"class": "inputx"}),
            "desc": forms.Textarea(attrs={"class": "inputx", "rows": 3}),
            "extra_desc": forms.Textarea(attrs={"class": "inputx", "rows": 4}),  # ⭐
            "link_url": forms.URLInput(attrs={"class": "inputx"}),
            "phone": forms.TextInput(attrs={"class": "inputx"}),
            "business_number": forms.TextInput(attrs={"class": "inputx"}),
            "ecommerce_number": forms.TextInput(attrs={"class": "inputx"}),
            "agency": forms.TextInput(attrs={"class": "inputx"}),
            "office_address": forms.TextInput(attrs={"class": "inputx"}),
            "is_active": forms.CheckboxInput(attrs={"class": "checkx"}),
            "sort": forms.NumberInput(attrs={"class": "inputx"}),
        }


class UserSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True, label="이름")

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "아이디"
        })
        self.fields["email"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "이메일"
        })
        self.fields["first_name"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "이름"
        })
        self.fields["password1"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "비밀번호"
        })
        self.fields["password2"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "비밀번호 확인"
        })

class BoardPostForm(forms.ModelForm):
    class Meta:
        model = BoardPost
        fields = [
            "category",
            "title",
            "giftcard_type",
            "face_value",
            "price",
            "available_date",
            "content",
            "image",
        ]
        widgets = {
            "category": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "제목 입력"
            }),
            "giftcard_type": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "예: 롯데 상품권"
            }),
            "face_value": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "예: 50000"
            }),
            "price": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "예: 47000"
            }),
            "available_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),
            "content": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 8,
                "placeholder": "내용 입력"
            }),
            "image": forms.ClearableFileInput(attrs={
                "class": "form-control"
            }),
        }

class BoardCommentForm(forms.ModelForm):
    class Meta:
        model = BoardComment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "댓글을 입력하세요"
            }),
        }

class SignupVerifyRequestForm(forms.Form):
    name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "이름"
        })
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "휴대폰 번호"
        })
    )