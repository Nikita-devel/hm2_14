from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.conf.config import settings
from src.services.auth import auth_service

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME="Example FastAPI email",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


async def send_confirm_email(email: EmailStr, username: str, host: str):
    """
        Send a confirmation email for email verification.

        :param email: The recipient's email address.
        :type email: EmailStr
        :param username: The recipient's username.
        :type username: str
        :param host: The host URL for generating email confirmation links.
        :type host: str
    """
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="registration/confirm.html")
    except ConnectionErrors as err:
        print(err)


async def send_reset_email(email: EmailStr, username: str, host: str):
    """
        Send a password reset email.

        :param email: The recipient's email address.
        :type email: EmailStr
        :param username: The recipient's username.
        :type username: str
        :param host: The host URL for generating password reset links.
        :type host: str
    """
    try:
        reset_token = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Password Reset",
            recipients=[email],
            template_body={"host": host, "username": username, "token": reset_token},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="reset_password/password_reset_email.html")
    except ConnectionErrors as err:
        print(err)
