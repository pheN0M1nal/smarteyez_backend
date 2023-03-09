from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import QueryDict
from .serializers import UserSerializer
from rest_framework import response, status, viewsets, decorators
from apps.utils.enum import UserAccountType
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from user import models
from apps.utils.message_templates import MessageTemplates
from django.shortcuts import Http404, get_object_or_404
from django.core.mail import send_mail
from apps.utils.permissions import IsUserOrAdmin
# from .models import EmailVerificationToken
# Create your views here.

UserModel = get_user_model()


class AuthViewSet(viewsets.ModelViewSet):
    """viewset for creating users"""
    queryset = get_user_model().objects
    authentication_classes = [JWTAuthentication]
    permission_classes = []
    serializer_class = UserSerializer
    permission_classes_by_action = {}

    def get_permissions(self):
        if self.action in ["create_user", "create_super_user"]:
            return [IsAdminUser()]
        elif self.action in ["create_sub_user" ]:
            return [IsUserOrAdmin()]
        elif self.action in ["initiate_verify_email"]:
            return [IsAuthenticated]
        else:
            return [AllowAny()]

    def get_auth_token_data(self, user):
        data = {}
        refresh = RefreshToken.for_user(user)
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        return data

    @decorators.action(
        detail=False,
        methods=["post"]
    )
    def create_user(self, request, *args, **kwargs):
        # validate_password(password=password)
        if isinstance(request.data, QueryDict):
            request.data._mutable = True
        request.data['account_type'] = UserAccountType.USER.value
        serializer = self.serializer_class.Create(data=request.data)
        if (serializer.is_valid()):
            password = request.data.get("password")
            instance: UserModel = serializer.save()
            instance.parent_user = request.user
            instance.set_password(password)
            instance.save()
        else:
            return response.Response(status=status.HTTP_400_BAD_REQUEST, data={"error": serializer.errors})

        instance: UserModel = serializer.save()
        instance.set_password(password)
        instance.save()
        user_data = self.serializer_class.Retrieve.User(instance=instance,
                                                        context=self.get_serializer_context()).data
        auth_token = self.get_auth_token_data(instance)
        response_data = {**user_data, "token": auth_token}
        return response.Response(status=status.HTTP_201_CREATED,
                                 data={
                                     "message": "The user is created successfully",
                                     "data": response_data
                                 }, )

    @decorators.action(
        detail=False,
        methods=["post"]
    )
    def create_super_user(self, request, *args, **kwargs):
        if isinstance(request.data, QueryDict):
            request.data._mutable = True
        request.data['account_type'] = UserAccountType.ADMINISTRATOR.value
        serializer = self.serializer_class.Create(data=request.data)

        # serializer.is_valid(raise_exception=True)
        if (serializer.is_valid()):
            password = request.data.get("password")
            instance: UserModel = serializer.save()
            instance.parent_user = request.user
            instance.set_password(password)
            instance.is_superuser = True
            instance.is_staff = True
            instance.save()
        else:
            return response.Response(status=status.HTTP_400_BAD_REQUEST, data={"error": serializer.errors})
        user_data = self.serializer_class.Retrieve.User(instance=instance,
                                                        context=self.get_serializer_context()).data
        auth_token = self.get_auth_token_data(instance)
        response_data = {**user_data, "token": auth_token}
        transaction.on_commit(lambda: self.initialize_verify_email(instance))
        return response.Response(status=status.HTTP_201_CREATED,
                                 data={
                                     "message": "The user is created successfully",
                                     "data": response_data
                                 }, )

    @decorators.action(
        detail=False,
        methods=["post"]
    )
    @transaction.atomic
    # set permission for user only
    def create_sub_user(self, request, *args, **kwargs):
        if isinstance(request.data, QueryDict):
            request.data._mutable = True
        request.data['account_type'] = UserAccountType.SUBUSER.value
        serializer = self.serializer_class.Create.SubUser(data=request.data)

        # serializer.is_valid(raise_exception=True)
        if (serializer.is_valid()):
            password = request.data.get("password")
            instance: UserModel = serializer.save()
            instance.parent_user = request.user
            instance.set_password(password)
            instance.save()
        else:
            return response.Response(status=status.HTTP_400_BAD_REQUEST, data={"error": serializer.errors})
        user_data = self.serializer_class.Retrieve.User(instance=instance,
                                                        context=self.get_serializer_context()).data
        auth_token = self.get_auth_token_data(user=instance)
        response_data = {**user_data, "token": auth_token}
        return response.Response(status=status.HTTP_201_CREATED,
                                 data={
                                     "message": "The user is created successfully",
                                     "data": response_data
                                 }, )

    def initialize_verify_email(self, instance: UserModel):
        try:
            instance.has_pending_email_verification_request = False
            instance.save()
            token_instance = models.EmailVerificationToken.objects.create(owner=instance)
            message = MessageTemplates.email_verification_email(token_instance.token)
            print(message)
            transaction.on_commit(lambda: instance.send_email(subject='Verify Email Address', message=message))
        except Exception as e:
            print(str(e))

    @decorators.action(detail=False, methods=["post"])
    def initiate_verify_email(self, request, *args, **kwargs):
        instance = request.user
        if instance.is_email_verified:
            return response.Response(status=status.HTTP_400_BAD_REQUEST, data={"errors": ["verified email"],
                                                                               "message": "The email address is already verified for the account"})
        self.initialize_verify_email(instance)
        instance.has_pending_email_verification_request = True
        instance.save()
        return response.Response(status=status.HTTP_200_OK,
                                 data={"message": f"A verification email has been sent to {instance.email}"})

    @decorators.action(detail=False, methods=["post"])
    def finalize_verify_email(self, request, *args, **kwargs):
        Token = request.data.get("token")
        try:
            token_instance = get_object_or_404(models.EmailVerificationToken, token=Token)
        except Http404:
            return response.Response(status=status.HTTP_400_BAD_REQUEST, data={"errors": ["expired token"],
                                                                "message": "You specified a invalid verification token"})
    # Start from here tomorrow