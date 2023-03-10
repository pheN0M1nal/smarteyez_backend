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
        """serializer for both user and admin"""
        class Meta:
            model = get_user_model()
            fields = ['user_id', 'email', 'username'
                , 'first_name', 'last_name', 'account_type','phone_number']

        class SubUser(serializers.ModelSerializer):
            class Meta:
                model = get_user_model()
                fields = ['user_id', 'email', 'username'
                    , 'first_name', 'last_name', 'account_type','parent_user','phone_number']
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
                    "user_permissions",
                ]
        #         Remove this serializer
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
                    "parent_user"
                ]
        class SubUser(serializers.ModelSerializer):
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
                    "License",
                ]
