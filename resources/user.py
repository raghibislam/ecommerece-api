import traceback

from flask import request
from flask_restful import Resource
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    jwt_required,
    get_raw_jwt,
)

from libs.mailgun import MailGunException
from models.confirmation import ConfirmationModel
from schemas.user import UserRegisterSchema, UserLoginSchema
from models.user import UserModel, session
from blacklist import BLACKLIST

_USER_ALREADY_EXISTS = "A user with that username already exists."
_CREATED_SUCCESSFULLY = "User created successfully."
_USER_NOT_FOUND = "User not found."
_USER_DELETED = "User deleted."
_INVALID_CREDENTIALS = "Invalid credentials!"
_USER_LOGGED_OUT = "{} successfully logged out."
EMAIL_ALREADY_EXISTS = "A user with that email already exists."
SUCCESS_REGISTER_MESSAGE = "Account created successfully. An email" \
                           " with an activation link has been sent to you email address.Please check.."
FAILED_TO_CREATE = "Internal Server error. Failed to create user."
NOT_CONFIRMED_ERROR = "You have not confirmed your registration, please check your email {}"

user_register_schema = UserRegisterSchema()
user_login_schema = UserLoginSchema()


class UserRegister(Resource):
    @classmethod
    def post(cls):
        user_json = request.get_json()
        user = user_register_schema.load(user_json, session=session)    # python object

        if UserModel.find_by_username(user.username):
            return {"message": _USER_ALREADY_EXISTS}, 400

        try:
            user.save_to_db()
            confirmation = ConfirmationModel(user.id)
            confirmation.save_to_db()
            user.send_confirmation_email()
            return {"message": SUCCESS_REGISTER_MESSAGE}, 201
        except MailGunException as error:
            user.delete_from_db()
            return {"message": str(error)}, 500
        except:
            traceback.print_exc()
            user.delete_from_db()
            return {"message": FAILED_TO_CREATE}, 500


class UserLogin(Resource):
    @classmethod
    def post(cls):
        user_json = request.get_json()
        user_data = user_login_schema.load(user_json, session=session)
        user = UserModel.find_by_username(user_data.username)
        user.set_password()
        if user and user.check_password(user_data.password):
            confirmation = user.most_recent_confirmation
            if confirmation and confirmation.confirmed:
                access_token = create_access_token(identity=user.id, fresh=True)
                refresh_token = create_refresh_token(identity=user.id)
                return {
                    "access_token": access_token,
                    "refresh_token": refresh_token
                }, 200
            return {"message": NOT_CONFIRMED_ERROR.format(user.username)}, 400
        return {"message": _INVALID_CREDENTIALS}, 401


class UserLogout(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        jti = get_raw_jwt()['jti']
        user_id = get_jwt_identity()
        BLACKLIST.add(jti)
        return {"message": _USER_LOGGED_OUT.format(UserModel.find_by_id(user_id).get_full_name())}, 200


class TokenRefresh(Resource):
    @classmethod
    @jwt_refresh_token_required
    def post(cls):
        current_user_id = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user_id, fresh=False)
        return {"access_token": new_access_token}, 200

