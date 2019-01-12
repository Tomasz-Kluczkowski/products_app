from sqlalchemy import Column, Integer, String, Table, ForeignKey, FLOAT
from sqlalchemy.orm import relationship

from database.database import Base


class NameBase:
    """
    Base class for all models requiring a unique name field.
    """
    name = Column(String(50), unique=True)


class Group(Base, NameBase):
    """
    Group model for products (i.e: family, range etc.) - more specific classification than Type.
    """
    __tablename__ = 'group'
    id = Column(Integer, primary_key=True)


class Tag(Base, NameBase):
    """
    Tag model for products.
    """
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True)


class Material(Base, NameBase):
    """
    Model of material of a product. (i. e. sugar, grams, 20)
    """
    __tablename__ = 'material'
    id = Column(Integer, primary_key=True)
    quantity = Column(FLOAT)
    units = Column(String(50))
    product_id = Column(Integer, ForeignKey('product.id'))


class Allergen(Base, NameBase):
    """
    Model for an allergen in food product.
    """
    __tablename__ = 'allergen'
    id = Column(Integer, primary_key=True)


class Customer(Base, NameBase):
    """
    Model for customer.
    """
    __tablename__ = 'customer'
    id = Column(Integer, primary_key=True)


product_tag = Table(
    'product_tag',
    Base.metadata,
    Column('product_id', Integer, ForeignKey('product.id')),
    Column('tag_id', Integer, ForeignKey('tag.id'))
)


class Product(Base, NameBase):
    """
    Base product model to be extended by specific product types.
    """
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('group.id'))
    group = relationship('Group', backref='products')
    tags = relationship('Tag', secondary=product_tag)
    materials = relationship('Material')
    type = Column(String(50))
    __mapper_args__ = {
        'polymorphic_identity': 'product',
        'polymorphic_on': type
    }


product_allergens = Table(
    'product_allergen',
    Base.metadata,
    Column('food_product_id', Integer, ForeignKey('food_product.id')),
    Column('allergen_id', Integer, ForeignKey('allergen.id'))
)


class FoodProduct(Product):
    """
    Food product model class.
    """
    __tablename__ = 'food_product'
    id = Column(Integer, ForeignKey('product.id'), primary_key=True)
    allergens = relationship('Allergen', secondary=product_allergens)
    customer_id = Column(Integer, ForeignKey('customer.id'))
    customer = relationship('Customer', backref='food_products')
    __mapper_args__ = {
        'polymorphic_identity': 'food_product'
    }


class TextileProduct(Product):
    """
    Textile product model class.
    """
    __tablename__ = 'textile_product'
    id = Column(Integer, ForeignKey('product.id'), primary_key=True)
    colour = Column(String(50))
    __mapper_args__ = {
        'polymorphic_identity': 'textile_product'
    }
