from django.core.mail import send_mail
from django.template.loader import render_to_string
import typing
from django.conf import settings
from django.utils.html import strip_tags


def send_mail_to_user(user, subject: str, message: str, greeting_prefix="Hi"):
    return send_email(receiver={"name": user.get_full_name(),
                                "email": user.email
                                }, subject=subject, message=message, greeting_prefix=greeting_prefix)


def send_email(receiver, subject, message, greeting_prefix):
    mail_template = "mail/message.html"
    sender = settings.DEFAULT_FROM_EMAIL
    context = {"subject": subject, "name": receiver.get("name") or '', "message": message,
               "greeting_prefix": greeting_prefix}
    mail_body = render_to_string(mail_template, context)
    return send_mail(subject, strip_tags(mail_body), sender, [receiver.get("email")], html_message=mail_body)
