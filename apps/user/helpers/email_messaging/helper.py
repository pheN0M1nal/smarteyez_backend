from . import EmailClient


class EmailHelper:
    _client: EmailClient

    def __init__(self):
        self._client = EmailClient()

    def send_mail_to_user(self, user, subject: str, message: str, greeting_prefix="Hi"):
        self._client.send_mail(receiver={"name": user.full_name,
                                         "email": user.email
                                         }, subject=subject, message=message, greeting_prefix=greeting_prefix)

    def send_mail_to_address(self, email, subject: str, message: str, greeting_prefix="Hi"):
        self._client.send_mail(receiver={"name": '',
                                         "email": email
                                         }, subject=subject, message=message, greeting_prefix=greeting_prefix)
