from models.product import ProductModel, ProductCategory
from marshmallow_sqlalchemy import ModelSchema


class ProductSchema(ModelSchema):
    class Meta:
        model = ProductModel
        dump_only = ('id',)
        include_fk = True


class ProductCategorySchema(ModelSchema):
    class Meta:
        model = ProductCategory
        load_only = ('product',)
        dump_only = ('id',)
        include_fk = True
