from marshmallow_sqlalchemy import ModelSchema

from models.confirmation import ConfirmationModel


class ConfirmationSchema(ModelSchema):
    class Meta:
        model = ConfirmationModel
        load_only = ("user",)
        dump_only = ("id", "expire_at", "confirmed")
        include_fk = True
