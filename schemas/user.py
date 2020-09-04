from marshmallow import pre_dump
from marshmallow_sqlalchemy import ModelSchema

from models.user import UserModel


class UserRegisterSchema(ModelSchema):
    class Meta:
        model = UserModel
        load_only = ('password', 'created_at')   # returning password is vulnerable
        dump_only = ('id', "confirmation")         # ID is automatically added to each user.

    @pre_dump
    def _pre_dump(self, user):
        user.confirmation = [user.most_recent_confirmation]
        return user


class UserLoginSchema(ModelSchema):
    class Meta:
        model = UserModel
        fields = ("username", "password")
        load_only = ("password", )
