from django.conf import settings
from solapi import SolapiMessageService
from solapi.model import RequestMessage


def send_verification_sms(to_phone: str, code: str) -> dict:
    try:
        message_service = SolapiMessageService(
            api_key=settings.SOLAPI_API_KEY,
            api_secret=settings.SOLAPI_API_SECRET,
        )

        message = RequestMessage(
            from_=settings.SOLAPI_SENDER,
            to=to_phone,
            text=f"[상품권거래소] 회원가입 인증번호는 [{code}] 입니다.",
            country="82",
        )

        response = message_service.send(message)

        return {
            "ok": True,
            "response": response,
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
        }