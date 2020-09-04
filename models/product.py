from sqlalchemy.orm import scoped_session, sessionmaker
from database import db
from werkzeug.security import safe_str_cmp

session = scoped_session(sessionmaker(bind=db))


class ProductCategory(db.Model):

    __tablename__ = 'product_category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product = db.relationship('ProductModel')

    def __repr__(self):
        return f"<ProductCategory {self.name}>"


class ProductModel(db.Model):

    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    description = db.Column(db.Text(), nullable=False)
    price = db.Column(db.Float(precision=2), nullable=False)
    categories = db.relationship('ProductCategory', lazy=True)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def get_all_products(cls):
        return cls.query.all()

    def __repr__(self):
        return f"<Product {self.name} >"
