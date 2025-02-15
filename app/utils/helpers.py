from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_pw: str, hashed_pw: str) -> bool:
    return pwd_context.verify(plain_pw, hashed_pw)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def generate_otp_code(length=6) -> str:
    import random
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])
