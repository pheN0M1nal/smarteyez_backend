from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer:
    class Base(serializers.ModelSerializer):
        class Meta:
            model = get_user_model()
            fields = [
                "user_id",
                "email",
                "account_type",
                "date_joined",
            ]
            filterset_fields = ['email', 'date_joined', 'account_type']
            ordering_fields = ['email', 'date_joined']

    class List(Base):
        ...

    class Create(Base):
        class Meta:
            model = get_user_model()
            fields = ['user_id', 'email', 'username'
                , 'first_name', 'last_name', 'account_type']

    class Retrieve(Base):
        class User(serializers.ModelSerializer):
            class Meta:
                model=get_user_model()
                exclude=[
                    "user_id",
                    "password",
                    "is_superuser",
                    "is_staff",
                    "is_active",
                    "groups",
                    "user_permissions"
                ]
        class Admin(serializers.ModelSerializer):
            class Meta:
                model=get_user_model()
                exclude=[
                    "user_id",
                    "password",
                    "is_superuser",
                    "is_staff",
                    "is_active",
                    "groups",
                    "user_permissions",
                ]