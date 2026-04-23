import re
import urllib3
from decimal import Decimal, InvalidOperation

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand, CommandError

from leads.models import GiftcardPrice

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

WOOTICKET_PRICE_URL = "https://www.wooticket.com/price_status.php"


def parse_int(value: str) -> int:
    if not value:
        return 0

    # 괄호 앞까지만 사용
    # 예: "483,250 (3.35%)" -> "483,250 "
    value = value.split("(")[0]

    digits = re.sub(r"[^\d]", "", value)

    try:
        num = int(digits) if digits else 0

        # 비정상적으로 큰 값 방어
        if num >= 10**9:
            return 0

        return num
    except (ValueError, TypeError):
        return 0


def parse_percent(value: str) -> Decimal:
    match = re.search(r"\(([\d.]+)%\)", value or "")
    if not match:
        return Decimal("0")

    try:
        return Decimal(match.group(1))
    except (InvalidOperation, ValueError):
        return Decimal("0")


def extract_price_and_rate(raw: str) -> tuple[int, Decimal]:
    return parse_int(raw), parse_percent(raw)


def detect_kind(name: str) -> str:
    mobile_keywords = [
        "모바일", "기프티콘", "온라인", "컬쳐랜드", "해피머니", "구글",
        "틴캐시", "북앤라이프", "에그머니", "주유", "외식", "상품권교환권",
    ]
    if any(keyword in name for keyword in mobile_keywords):
        return GiftcardPrice.Kind.MOBILE
    return GiftcardPrice.Kind.PAPER


def detect_face_value(name: str) -> int:
    # 예: "(50만원권)"
    m = re.search(r"\((\d+)\s*만원권\)", name)
    if m:
        return int(m.group(1)) * 10000

    # 예: "(5천원권)"
    m = re.search(r"\((\d+)\s*천원권\)", name)
    if m:
        return int(m.group(1)) * 1000

    # 예: "(10000원권)"
    m = re.search(r"\((\d+)\s*원권\)", name)
    if m:
        return int(m.group(1))

    # 예: "50만원"
    m = re.search(r"(\d+)\s*만원", name)
    if m:
        return int(m.group(1)) * 10000

    # 예: "5천원"
    m = re.search(r"(\d+)\s*천원", name)
    if m:
        return int(m.group(1)) * 1000

    return 0


class Command(BaseCommand):
    help = "wooticket 시세를 가져와 GiftcardPrice에 반영합니다."

    def handle(self, *args, **options):
        try:
            response = requests.get(
                WOOTICKET_PRICE_URL,
                timeout=15,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/123.0.0.0 Safari/537.36"
                    )
                },
                verify=False,
            )
            response.raise_for_status()

            # 한글 깨짐 방지
            response.encoding = "cp949"

        except requests.RequestException as exc:
            raise CommandError(f"wooticket 요청 실패: {exc}") from exc

        soup = BeautifulSoup(response.text, "html.parser")

        rows = soup.select("table tr")
        if not rows:
            raise CommandError("시세 테이블을 찾지 못했습니다. HTML 구조를 확인하세요.")

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for row in rows:
            cols = [col.get_text(" ", strip=True) for col in row.find_all("td")]

            # 컬럼 수 부족하면 스킵
            if len(cols) < 3:
                continue

            raw_name, raw_buy, raw_sell = cols[0], cols[1], cols[2]

            # 헤더/빈 데이터 제외
            if not raw_name:
                continue

            if "상품권" in raw_name and "매입" in raw_buy:
                continue

            name = (
                raw_name
                .replace("▷ go", "")
                .replace("\xa0", " ")
                .strip()
            )

            buy_price, buy_rate = extract_price_and_rate(raw_buy)
            sell_price, sell_rate = extract_price_and_rate(raw_sell)

            # 가격이 둘 다 0이면 이상 데이터로 보고 스킵
            if buy_price == 0 and sell_price == 0:
                skipped_count += 1
                continue

            face_value = detect_face_value(name)

            # 액면가를 못 찾으면 더 큰 값을 임시 액면가로 사용
            if face_value == 0:
                face_value = max(buy_price, sell_price)

            kind = detect_kind(name)

            _, created = GiftcardPrice.objects.update_or_create(
                name=name,
                defaults={
                    "kind": kind,
                    "face_value": face_value,
                    "buy_price": buy_price,
                    "buy_rate": buy_rate,
                    "sell_price": sell_price,
                    "sell_rate": sell_rate,
                    "is_active": True,
                },
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"완료: 생성 {created_count}건 / 수정 {updated_count}건 / 스킵 {skipped_count}건"
            )
        )