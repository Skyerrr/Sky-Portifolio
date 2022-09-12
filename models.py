from main import *
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship


db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True)
    password = db.Column(db.String(128))
    name = db.Column(db.String(128))



class Vehicles(db.Model):
    __tablename__ = 'vehicles'
    id = db.Column(db.Integer, primary_key=True)
    vehicles_db = relationship('Category', back_populates="category_db")
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    to_gallery_db = relationship('Gallery', back_populates="to_vehicle_db")
    category = db.Column(db.String, nullable=False)
    en_title = db.Column(db.String(128))
    br_title = db.Column(db.String(128))
    en_description = db.Column(db.String(256))
    br_description = db.Column(db.String(256))
    en_body = db.Column(db.Text)
    br_body = db.Column(db.Text)
    image = db.Column(db.String)
    video = db.Column(db.String)
    image_video = db.Column(db.String, nullable=True)
    br_price = db.Column(db.Float, nullable=False)
    en_price = db.Column(db.Float, nullable=False)
    discount_value = db.Column(db.Float, nullable=False)
    tebex = db.Column(db.String)

class Gallery(db.Model):
    __tablename__ = 'gallery'
    id = db.Column(db.Integer, primary_key=True)
    db_vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"))
    images = db.Column(db.String)
    to_vehicle_db = relationship('Vehicles', back_populates="to_gallery_db")



class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    subcategory_id = db.Column(db.Integer, db.ForeignKey("subcategories.id"))
    category_db = relationship("Vehicles", back_populates='vehicles_db')
    category_db2 = relationship("Subcategory", back_populates='category')
    en_name = db.Column(db.String(128))
    en_url = db.Column(db.String(128))
    br_name = db.Column(db.String(128))
    br_url = db.Column(db.String(128))

class Subcategory(db.Model):
    __tablename__ = 'subcategories'
    id = db.Column(db.Integer, primary_key=True)
    category = relationship("Category", back_populates=('category_db2'))
    en_name = db.Column(db.String(128))
    br_name = db.Column(db.String(128))


db.create_all()
