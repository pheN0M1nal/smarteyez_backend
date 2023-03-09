from django.core.exceptions import ObjectDoesNotExist
from user import models as user_models
from .helpers.email_messaging.helper import send_mail_to_user


def send_email_to_user(user_id: int, subject, message, greeting_prefix):
    try:
        user_instance: user_models.User = user_models.User.objects.get(user_id=user_id)
        return send_mail_to_user(user_instance, subject, message, greeting_prefix)
    except ObjectDoesNotExist as error:
        print(error)
