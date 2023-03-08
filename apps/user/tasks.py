# from django.core.exceptions import ObjectDoesNotExist
# from .helpers.email_messaging import helper as email_messaging_helper
#
#
# def send_email_to_user(self, user_id: int, subject, message, greeting_prefix):
#     try:
#         from .models import User
#         user_instance: User = User.objects.get(id=user_id)
#         email_helper = email_messaging_helper.EmailHelper()
#         return email_helper.send_mail_to_user(user_instance, subject, message, greeting_prefix)
#     except ObjectDoesNotExist as exc:
#         raise exc
#     except Exception as exc:
#         raise exc
