import secrets

from django.utils import timezone
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.utils.enum import UserAccountType
from apps.utils.base_model_config import BaseModelMixin
from django.conf import settings
from apps.utils import tasks as background_tasks

from apps.utils.helpers.email_messaging.helper import send_email


class UserManager(BaseUserManager):
    use_in_migration = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("account_type", UserAccountType.USER.value)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        try:
            extra_fields.setdefault("is_superuser", True)
            extra_fields.setdefault("is_staff", True)
            extra_fields.setdefault("account_type", UserAccountType.ADMINISTRATOR.value)
            if extra_fields.get("is_superuser") is not True:
                raise ValueError("Superuser must have is_superuser=True.")
        except Exception as e:
            pass
        else:
            return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()
    user_id = models.BigAutoField(primary_key=True)
    parent_user = models.ForeignKey('self', verbose_name='Parent User', on_delete=models.CASCADE, blank=True,
                                    null=True, related_name='children'
                                    , help_text="Only populate for subuser",
                                    limit_choices_to={"account_type__in": [UserAccountType.USER.value,
                                                                           UserAccountType.ADMINISTRATOR.value]})
    username = models.CharField(
        _("username"),
        max_length=150,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    email = models.EmailField(_("email address"), null=False, blank=False, unique=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    License = models.CharField(_("License"), blank=True, null=True, max_length=30)
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    account_type = models.CharField(_("Account Type"), null=False, blank=False, max_length=32,
                                    choices=UserAccountType.choices())
    phone_number = models.CharField(_("Phone Number"), null=False, blank=True, max_length=50, unique=False)
    is_phone_number_verified = models.BooleanField(_("Phone Number Verified?"), default=False, blank=False, null=False)
    is_email_verified = models.BooleanField(_("Email Verified?"), default=False, blank=True, null=False)
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def send_email(self, subject, message, ignore_verification=True, greeting_prefix="Hi"):
        assert self.email, f"{self.get_full_name()} doesn't have a valid email address"
        if not ignore_verification and not self.is_email_verified:
            return background_tasks.send_email_to_user(self.user_id, subject, message, greeting_prefix)

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def verify_phone_number(self):
        self.is_phone_number_verified = True
        self.save()

    def __str__(self):
        return f'{self.email}-{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        abstract = False
        app_label = 'user'


class EmailVerificationToken(BaseModelMixin):
    def create_token(self):
        return secrets.token_hex(16)

    owner = models.ForeignKey("user.User",
                              on_delete=models.CASCADE,
                              null=False,
                              related_name="email_verification_token",
                              verbose_name=_("Created By"))
    token = models.CharField(_("Token"),
                             null=False,
                             blank=True,
                             default=secrets.token_hex(16),
                             editable=False,
                             max_length=100, )

    def __str__(self):
        return f'EmailVerificationToken - {self.owner}'

    def is_expired(self):
        return timezone.now() > (
                    self.date_added + timezone.timedelta(seconds=settings.EMAIL_VERIFICATION_TOKEN_EXPIRATION_SECS))

    class Meta:
        verbose_name = _("Email Verification Token")
        verbose_name_plural = _("Email Verification Tokens")
        app_label = 'user'
