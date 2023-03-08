from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import QueryDict
from .serializers import UserSerializer
from rest_framework import response, status, viewsets, decorators
from apps.utils.enum import UserAccountType
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated,IsAdminUser,AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
# from .models import EmailVerificationToken
# Create your views here.
UserModel = get_user_model()


class AuthViewSet(viewsets.ModelViewSet):
    """viewset for creating users"""
    queryset = get_user_model().objects
    authentication_classes = [JWTAuthentication]
    permission_classes = []
    serializer_class = UserSerializer
    permission_classes_by_action={}

    def get_permissions(self):
        if self.action in ["create_user","create_super_user"]:
            return [IsAdminUser()]
        if self.action in ["create_sub_user"]:
            return [IsAuthenticated()]
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
        try:
            # validate_password(password=password)
            if isinstance(request.data, QueryDict):
                request.data._mutable = True
            request.data['account_type'] = UserAccountType.USER.value
            serializer = self.serializer_class.Create(data=request.data)
            if (serializer.is_valid()):
                password = request.data.get("password")
                if password != request.data.get("confirm_password") or password == None:
                    return response.Response(
                        status=status.HTTP_400_BAD_REQUEST,
                        data={
                            "errors": ["passwords do not match"],
                        },
                    )
                instance: UserModel = serializer.save()
                instance.parent_user = request.user
                instance.set_password(password)
                instance.save()
            else:
                return response.Response(status=status.HTTP_400_BAD_REQUEST, data={"error": serializer.errors})

            instance: UserModel = serializer.save()
            instance.set_password(password)
            instance.save()
            user_data=self.serializer_class.Retrieve.User(instance=instance,
                                                          context=self.get_serializer_context()).data
            auth_token = self.get_auth_token_data(instance)
            response_data={**user_data,"token":auth_token}
            return response.Response(status=status.HTTP_201_CREATED,
                                     data={
                                         "message": "The user is created successfully",
                                         "data":response_data
                                     }, )
        except Exception as e:
            return response.Response(status=status.HTTP_400_BAD_REQUEST,
                                     data={
                                         "message": str(e),
                                     }, )

    @decorators.action(
        detail=False,
        methods=["post"]
    )
    def create_super_user(self, request, *args, **kwargs):
        try:
            if isinstance(request.data, QueryDict):
                request.data._mutable = True
            request.data['account_type'] = UserAccountType.ADMINISTRATOR.value
            serializer = self.serializer_class.Create(data=request.data)

            # serializer.is_valid(raise_exception=True)
            if (serializer.is_valid()):
                password = request.data.get("password")
                if password != request.data.get("confirm_password") or password == None:
                    return response.Response(
                        status=status.HTTP_400_BAD_REQUEST,
                        data={
                            "errors": ["passwords do not match"],
                        },
                    )
                instance: UserModel = serializer.save()
                instance.parent_user = request.user
                instance.set_password(password)
                instance.is_superuser=True
                instance.is_staff=True
                instance.save()
            else:
                return response.Response(status=status.HTTP_400_BAD_REQUEST,data={"error":serializer.errors})
            user_data = self.serializer_class.Retrieve.User(instance=instance,
                                                            context=self.get_serializer_context()).data
            auth_token = self.get_auth_token_data(instance)
            response_data = {**user_data, "token": auth_token}
            transaction.on_commit(lambda : self.initialize_verify_email(instance))
            return response.Response(status=status.HTTP_201_CREATED,
                                     data={
                                         "message": "The user is created successfully",
                                         "data": response_data
                                     }, )
        except Exception as e:
            return response.Response(status=status.HTTP_400_BAD_REQUEST,
                                 data={
                                     "message": str(e),
                                 }, )

    @decorators.action(
        detail=False,
        methods=["post"]
    )
    @transaction.atomic
    # set permission for user only
    def create_sub_user(self, request, *args, **kwargs):
        try:
            if isinstance(request.data, QueryDict):
                request.data._mutable = True
            request.data['account_type'] = UserAccountType.SUBUSER.value
            serializer = self.serializer_class.Create.SubUser(data=request.data)

            # serializer.is_valid(raise_exception=True)
            if (serializer.is_valid()):
                password = request.data.get("password")
                if password != request.data.get("confirm_password") or password == None:
                    return response.Response(
                        status=status.HTTP_400_BAD_REQUEST,
                        data={
                            "errors": ["passwords do not match"],
                        },
                    )
                instance: UserModel = serializer.save()
                instance.parent_user=request.user
                instance.set_password(password)
                instance.save()
            else:
                return response.Response(status=status.HTTP_400_BAD_REQUEST,data={"error":serializer.errors})
            user_data = self.serializer_class.Retrieve.User(instance=instance,
                                                            context=self.get_serializer_context()).data
            auth_token = self.get_auth_token_data(user=instance)
            response_data = {**user_data, "token": auth_token}
            return response.Response(status=status.HTTP_201_CREATED,
                                     data={
                                         "message": "The user is created successfully",
                                         "data": response_data
                                     }, )
        except Exception as e:
            return response.Response(status=status.HTTP_400_BAD_REQUEST,
                                 data={
                                     "message": str(e),
                                 }, )

    def initialize_verify_email(self,instance : UserModel):
        instance.has_pending_email_verification(False)
        instance.save()
        # token_instance: models.EmailVerificationToken.objects.create(owner=instance)
        # message=MessageTemplates(token_instance.token)
    #     Resolve the model error here tomorrow

    # @decorators.action(detail=False,
    #     methods=['GET'])
    def send_email(self,request,*args,**kwargs):
        from django.core.mail import send_mail
        from apps.utils.message_templates import MessageTemplates
        send_mail(
            'Subject here',
            MessageTemplates.email_verification_email('abc'),
            'haseebahmed2624@gmail.com',
            ['haseeb.ahmed@deutics.com'],
            fail_silently=False,
        )
        return response.Response(status=status.HTTP_400_BAD_REQUEST, data={"message": "successful"})