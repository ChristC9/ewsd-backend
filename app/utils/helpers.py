from passlib.context import CryptContext
import resend
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_pw: str, hashed_pw: str) -> bool:
    return pwd_context.verify(plain_pw, hashed_pw)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def generate_otp_code(length=6) -> str:
    import random
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])


def send_otp_email(to_email: str, otp_code: str):
    resend.api_key = settings.RESEND_API_KEY

    params: resend.Emails.SendParams = {
        "from": "EWSD <onboarding@resend.dev>",
        "to": [f"{to_email}"],
        "subject": "Sending OTP Code",
        "html": f"Here is OTP code <strong>{otp_code}</strong>",
    }

    email = resend.Emails.send(params)