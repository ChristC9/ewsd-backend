from passlib.context import CryptContext
import resend

from app.config import settings
from app.services.mail import send_email

from app.schema.pagination import PaginationResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_pw: str, hashed_pw: str) -> bool:
    return pwd_context.verify(plain_pw, hashed_pw)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def generate_otp_code(length=6) -> str:
    import random
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])


def send_otp_email(to_email: str, otp_code: str):
    send_email([to_email], "Sending OTP Code", f"Here is OTP code <strong>{otp_code}</strong>")


def send_idea_submitted_email(to_emails, idea_title: str, user_name: str):
    send_email(to_emails, "Idea Submitted", f"<strong>{user_name}</strong> sumbitted an idea with title: <strong>{idea_title}</strong>")

def send_comment_submitted_email(to_emails, comment_text: str, user_name: str):
    send_email(to_emails, "Comment Submitted", f"<strong>{user_name}</strong> sumbitted a comment: <strong>{comment_text}</strong>")

def compute_pagination(total: int, page: int, limit: int) -> PaginationResponse:
    total_pages = (total + limit - 1) // limit
    
    next_page = page + 1 if page < total_pages else None
    prev_page = page - 1 if page > 1 else None
    
    return PaginationResponse(
        total_records=total,
        current_page=page,
        total_pages=total_pages,
        next_page=next_page,
        prev_page=prev_page
    )

def get_full_file_url(file_path: str, base_url: str = "https://ewsd-endpoint.onrender.com") -> str:
    """Convert a relative file path to a full URL including domain"""
    if not file_path:
        return None
    
    # Check if file_path already includes the domain
    if file_path.startswith(('http://', 'https://')):
        return file_path
        
    # Ensure file_path doesn't start with a slash if we're going to add it
    file_path = file_path.lstrip('/')
    
    # Combine to form complete URL
    return f"{base_url}/{file_path}"
    