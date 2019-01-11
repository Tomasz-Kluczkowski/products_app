from sqlalchemy import Column, Integer, String, Table, ForeignKey, Numeric
from sqlalchemy.orm import relationship

from database.database import Base


class NameBase:
    name = Column(String(50), unique=True)


product_tag = Table(
    'product_tag',
    Base.metadata,
    Column('product_id', Integer, ForeignKey('products.product_id')),
    Column('tag_id', Integer, ForeignKey('tags.tag_id'))
)


class Product(Base, NameBase):
    __tablename__ = 'products'
    product_id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.group_id'))
    group = relationship('Group', backref='products')
    tags = relationship('Tag', secondary=product_tag)
    product_type_id = Column(Integer, ForeignKey('product_types.product_type_id'))
    product_type = relationship('ProductType', backref='products')
    materials = relationship('ProductComponent')


class Group(Base, NameBase):
    __tablename__ = 'groups'
    group_id = Column(Integer, primary_key=True)


class Tag(Base, NameBase):
    __tablename__ = 'tags'
    tag_id = Column(Integer, primary_key=True)


class ProductType(Base, NameBase):
    __tablename__ = 'product_types'
    product_type_id = Column(Integer, primary_key=True)


class Material(Base, NameBase):
    __tablename__ = 'materials'
    material_id = Column(Integer, primary_key=True)
    units = Column(String(50))


class ProductComponent(Base):
    __tablename__ = 'product_components'
    product_component_id = Column(Integer, primary_key=True)
    material_id = Column(Integer, ForeignKey('materials.material_id'))
    material = relationship('Material', backref='product_components')
    quantity = Column(Numeric, precision=2)
    product_id = Column(Integer, ForeignKey('products.product_id'))

