from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.html import strip_tags
import typing
from django.conf import settings


class EmailClient:
    mail_template = "mail/message.html"
    sender: str = settings.DEFAULT_FROM_EMAIL

    def send_mail(self, receiver: typing.Dict, subject: str, message: str, greeting_prefix):
        context = {"subject": subject, "name": receiver.get("name") or '', "message": message,
                   "greeting_prefix": greeting_prefix}
        mail_body = render_to_string(self.mail_template, context)
        return send_mail(subject, strip_tags(mail_body), self.sender, [receiver.get("email")], html_message=mail_body)
