from sqlalchemy import Column, Integer, String, Table, ForeignKey, FLOAT
from sqlalchemy.ext.declarative import declared_attr
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
    __tablename__ = 'groups'
    group_id = Column(Integer, primary_key=True)


class Tag(Base, NameBase):
    """
    Tag model for products.
    """
    __tablename__ = 'tags'
    tag_id = Column(Integer, primary_key=True)


class ProductType(Base, NameBase):
    """
    Product type model. Use as a general classification for whole set of products (i.e. edibles,
     machines etc.) Use Group as more specific classification.
    """
    __tablename__ = 'product_types'
    product_type_id = Column(Integer, primary_key=True)


class Material(Base, NameBase):
    """
    Model of a basic material of a product. (i. e. sugar, grams)
    """
    __tablename__ = 'materials'
    material_id = Column(Integer, primary_key=True)
    units = Column(String(50))


class Allergen(Base, NameBase):
    """
    Model for an allergen in food product.
    """
    __tablename__ = 'allergens'
    allergen_id = Column(Integer, primary_key=True)


class Customer(Base, NameBase):
    """
    Model for customer.
    """
    __tablename__ = 'customers'
    customer_id = Column(Integer, primary_key=True)


class ProductComponent(Base):
    """
    Model for an actual constituent of a product (i.e. 20g of sugar etc.)
    """
    __tablename__ = 'product_components'
    product_component_id = Column(Integer, primary_key=True)
    material_id = Column(Integer, ForeignKey('materials.material_id'))
    material = relationship('Material', backref='product_components')
    quantity = Column(FLOAT)
    product_id = Column(Integer, ForeignKey('products.product_id'))


product_tag = Table(
    'product_tag',
    Base.metadata,
    Column('product_id', Integer, ForeignKey('products.product_id')),
    Column('tag_id', Integer, ForeignKey('tags.tag_id'))
)


class Product(Base, NameBase):
    """
    Base product model to be extended by specific product types.
    """
    __tablename__ = 'products'
    product_id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.group_id'))
    group = relationship('Group', backref='products')
    tags = relationship('Tag', secondary=product_tag)
    product_type_id = Column(Integer, ForeignKey('product_types.product_type_id'))
    product_type = relationship('ProductType', backref='products')
    product_components = relationship('ProductComponent')


product_allergens = Table(
    'product_allergens',
    Base.metadata,
    Column('product_id', Integer, ForeignKey('food_products.product_id')),
    Column('allergen_id', Integer, ForeignKey('allergens.allergen_id'))
)


class ProductMixin:
    """
    Adds product_id to specific product types.
    """
    @declared_attr
    def product_id(cls):
        return Column('product_id', ForeignKey('products.product_id'))

    @declared_attr
    def product(cls):
        return relationship("Product")


class FoodProduct(ProductMixin, Base):
    """
    Food product model class.
    """
    __tablename__ = 'food_products'
    food_product_id = Column(Integer, primary_key=True)
    allergens = relationship('Allergen', secondary=product_allergens)
    customer_id = Column(Integer, ForeignKey('customers.customer_id'))
    customer = relationship('Customer', backref='food_products')


class TextileProduct(ProductMixin, Base):
    """
    Textile product model class.
    """
    __tablename__ = 'textile_products'
    textile_product_id = Column(Integer, primary_key=True)
    colour = Column(String(50))

