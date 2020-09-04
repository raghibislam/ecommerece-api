from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from werkzeug.security import safe_str_cmp

from schemas.product import ProductSchema
from models.product import ProductModel, session

_PRODUCT_ALREADY_EXISTS = "{} already exists."
_CREATED_SUCCESSFULLY = "Product is added successfully."
_PRODUCT_NOT_FOUND = "{} does not exists. Invalid Request"
_PRODUCT_DELETED = "{} is successfully deleted."
product_schema = ProductSchema()


class Product(Resource):

    @classmethod
    def get(cls, name):
        product = ProductModel.find_by_name(name)
        if product:
            return {"product": product_schema.dump(product)}, 200
        return {"message": _PRODUCT_NOT_FOUND.format(name)}, 400

    @classmethod
    def put(cls, name):
        product_json = request.get_json()
        product_in_db = ProductModel.find_by_name(name)
        if product_in_db:
            product_in_db.price = product_json['price']
            product_in_db.name = product_json["name"]
            product_in_db.description = product_json['description']
            product_in_db.categories = []
            product_in_db.save_to_db()
            return product_schema.dump(product_in_db), 200
        return {"message": _PRODUCT_NOT_FOUND.format(name)}

    @classmethod
    @jwt_required
    def delete(cls, name):
        product = ProductModel.find_by_name(name)
        if product:
            product.delete_from_db()
            return {"message": _PRODUCT_DELETED.format(name)}, 200
        return {"message": _PRODUCT_NOT_FOUND}, 404


class ProductList(Resource):
    @classmethod
    def get(cls):
        products = ProductModel.get_all_products()
        return {'products': [product_schema.dump(product) for product in products]}

    @classmethod
    @jwt_required
    def post(cls):
        """
        Post an item
        :return item that is added to database.:
        """
        product_json = request.get_json()
        product = product_schema.load(product_json, session=session)

        if ProductModel.find_by_name(product.name):
            return {"message": _PRODUCT_ALREADY_EXISTS.format(product.name)}, 400

        product.save_to_db()

        return {"message": _CREATED_SUCCESSFULLY, "product": product_schema.dump(product)}, 201
