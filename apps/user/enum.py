from enum import Enum


class BaseEnum(Enum):
    @classmethod
    def choices(cls):
        return [(i.value, i.name) for i in cls]

    @classmethod
    def values(cls):
        return list(i.value for i in cls)

    @classmethod
    def mapping(cls):
        return dict((i.name, i.value) for i in cls)

    @classmethod
    def count(cls):
        return len(cls)


class UserAccountType(BaseEnum):
    USER = "user"
    SUBUSER = "subuser"
    ADMINISTRATOR = "administrator"
