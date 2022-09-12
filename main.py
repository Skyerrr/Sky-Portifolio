from flask import Flask, render_template, request, redirect, url_for, flash, abort, send_file
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from functools import wraps
from wtforms import StringField, SubmitField, URLField
from wtforms.validators import DataRequired, URL, AnyOf
from flask_ckeditor import CKEditorField, CKEditor
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
import os
from werkzeug.utils import secure_filename
import forms
from forms import *

UPLOAD_PATH = 'static/img/'


app = Flask(__name__)
app.config['UPLOAD_PATH'] = UPLOAD_PATH


app.config['SECRET_KEY'] = '8BBkEFbA6O7donzWlSihBXox8C0sKR6B'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)
ckeditor = CKEditor(app)
login_manager = LoginManager()
login_manager.init_app(app)
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
    to_vehicle_db = relationship('Vehicles', back_populates="to_gallery_db")
    images = db.Column(db.String)



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




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)

    return decorated_function



@app.route('/')
def home():
    return render_template("index.html")

@app.route('/skymacro')
def skymacro():
    return render_template("skymacro.html")

@app.route('/skymacro/download')
def skymacro_download():
    return send_file(
        'outputs/SkyMacroSetup.exe',
        mimetype='application/vnd.microsoft.portable-executable',
        download_name='SkyMacroSetup.exe',
        as_attachment=True
    )

#### PT BR Route ####

@app.route('/pt-br')
def pthome():
    sub_categories = Subcategory.query.all()
    return render_template("/br/index.html", sub_categories=sub_categories)

@app.route('/pt-br/sobre')
def about():
    sub_categories = Subcategory.query.all()
    return render_template("/br/about.html", sub_categories=sub_categories)

@app.route('/pt-br/faq')
def faq():
    sub_categories = Subcategory.query.all()
    return render_template("/br/faq.html", sub_categories=sub_categories)

@app.route('/<br_name>')
def category_selected(br_name):
    br_name = Category.query.filter(Category.br_name==br_name).first()
    subcategorys = Subcategory.query.get(br_name.subcategory_id)
    all_vehicles = Vehicles.query.filter(Vehicles.category.contains(br_name.id))
    sub_categories = Subcategory.query.all()
    return render_template('/br/categoria.html', sub_categories=sub_categories, category=br_name, all_vehicles=all_vehicles, subcategory=subcategorys)

@app.route('/pt-br/veiculo/<int:vehicle_id>')
def show_vehicle(vehicle_id):
    requested_vehicle = Vehicles.query.get(vehicle_id)
    category = Category.query.filter(Category.id == requested_vehicle.category).first()
    sub_categories = Subcategory.query.all()
    return render_template('/br/vehicle.html', sub_categories=sub_categories, vehicle=requested_vehicle, category=category)

@app.route('/add-vehicle', methods=["GET", "POST"])
@admin_only
def add_vehicle():
    sub_categories = Subcategory.query.all()
    model = Vehicles()
    form = VehicleForm(discount_value=0)
    form.category.choices = [(category.id, category.br_name) for category in Category.query.all()]
    if form.validate_on_submit():
        if form.image.data:
            uploaded_file = request.files['image']
            filename = secure_filename(uploaded_file.filename)
            uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        if form.image_video.data:
            form.image_video.data = secure_filename(form.image_video.data.filename)
            uploaded_file2 = request.files['image_video']
            filename2 = secure_filename(uploaded_file2.filename)
            uploaded_file2.save(os.path.join(app.config['UPLOAD_PATH'], filename2))
        elif not form.image_video.data:
            form.image_video.data = None


        form.populate_obj(model)
        db.session.add(model)
        db.session.commit()
        flash('Vehicle Successfully Added', 'succes')
        return render_template("/br/add-vehicle.html", form=form, sub_categories=sub_categories)
    return render_template("/br/add-vehicle.html", form=form, sub_categories=sub_categories)

@app.route('/add-category', methods=["GET", "POST"])
@admin_only
def add_category():
    sub_categories = Subcategory.query.all()
    form = CategoryForm()
    form.subcategory_id.choices = [(subcategory_id.id, subcategory_id.br_name) for subcategory_id in Subcategory.query.all()]
    if form.validate_on_submit():
        new_category = Category(en_name=request.form["en_name"], br_name=request.form["br_name"], subcategory_id=request.form["subcategory_id"])
        db.session.add(new_category)
        db.session.commit()
        flash('Category Successfully Added', 'succes')
        return render_template("/br/add-category.html", form=form, sub_categories=sub_categories)
    return render_template("/br/add-category.html", form=form, sub_categories=sub_categories)

@app.route('/add-subcategory', methods=["GET", "POST"])
@admin_only
def add_subcategory():
    sub_categories = Subcategory.query.all()
    form = SubcategoryForm()
    if form.validate_on_submit():
        new_category = Subcategory(en_name=request.form["en_name"], br_name=request.form["br_name"])
        db.session.add(new_category)
        db.session.commit()
        flash('Subcategory Successfully Added', 'succes')
        return render_template("/br/add-subcategory.html", form=form, sub_categories=sub_categories)
    return render_template("/br/add-subcategory.html", form=form, sub_categories=sub_categories)

@app.route('/delete-category')
def delete_category():
    sub_categories = Subcategory.query.all()
    return render_template('/br/delete-category.html', sub_categories=sub_categories)

@app.route("/edit/<int:vehicle_id>", methods=["GET", "POST"])
@admin_only
def edit_vehicle(vehicle_id):
    vehicle_edit = Vehicles.query.get(vehicle_id)
    form = VehicleForm(obj=vehicle_edit)

    form.category.choices = [(category.id, category.br_name) for category in Category.query.all()]
    if form.validate_on_submit():
        if form.image.data:
            uploaded_file = request.files['image']
            filename = secure_filename(uploaded_file.filename)
            uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        if form.image_video.data:
            form.image_video.data = secure_filename(form.image_video.data.filename)
            uploaded_file2 = request.files['image_video']
            filename2 = secure_filename(uploaded_file2.filename)
            uploaded_file2.save(os.path.join(app.config['UPLOAD_PATH'], filename2))
        elif not form.image_video.data:
            form.image_video.data = None
        vehicle_edit.category = form.category.data
        vehicle_edit.en_title = form.en_title.data
        vehicle_edit.br_title = form.br_title.data
        vehicle_edit.en_description = form.en_description.data
        vehicle_edit.br_description = form.br_description.data
        vehicle_edit.en_body = form.en_body.data
        vehicle_edit.br_body = form.br_body.data
        vehicle_edit.image = form.image.data
        vehicle_edit.video = form.video.data
        vehicle_edit.image_video = form.image_video.data
        vehicle_edit.br_price = form.br_price.data
        vehicle_edit.en_price = form.en_price.data
        vehicle_edit.discount_value = form.discount_value.data
        vehicle_edit.tebex = form.tebex.data
        db.session.commit()
        return redirect(url_for("show_vehicle", vehicle_id=vehicle_edit.id))
    return render_template("/br/edit.html", form=form, vehicle=vehicle_edit)

@app.route("/editgallery/<int:vehicle_id>", methods=["GET", "POST"])
@admin_only
def edit_gallery(vehicle_id):
    sub_categories = Subcategory.query.all()
    vehicle_edit = Vehicles.query.get(vehicle_id)
    form = GalleryForm()
    form.vehicle_choose.choices = [(vehicle_edit.id, vehicle_edit.br_title)]
    if form.validate_on_submit():
        if form.images.data:
            form.images.data = secure_filename(form.images.data.filename)
            uploaded_file2 = request.files['images']
            filename2 = secure_filename(uploaded_file2.filename)
            uploaded_file2.save(os.path.join(app.config['UPLOAD_PATH'], filename2))
        elif not form.images.data:
            form.images.data = None
        new_gallery = Gallery(db_vehicle_id=vehicle_edit.id, images=form.images.data)
        db.session.add(new_gallery)
        db.session.commit()
        flash('Image Successfully Added', 'succes')

    return render_template("/br/editgallery.html", form=form, sub_categories=sub_categories, vehicle=vehicle_edit)


@app.route("/deletecat/<int:cat_id>")
@admin_only
def delete_cat(cat_id):
    cat_to_delete = Category.query.get(cat_id)
    db.session.delete(cat_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/deletesubcat/<int:subcat_id>")
@admin_only
def delete_subcat(subcat_id):
    subcat_to_delete = Subcategory.query.get(subcat_id)
    db.session.delete(subcat_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/deletevehicle/<int:vehicle_id>")
@admin_only
def delete_vehicle(vehicle_id):
    vehicle_to_delete = Vehicles.query.get(vehicle_id)
    db.session.delete(vehicle_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/deletegalery/<int:galery_id>/<int:vehicle_id>")
@admin_only
def delete_galery(galery_id, vehicle_id):
    the_vehicle_id = Vehicles.query.get(vehicle_id)
    vehicle_id = the_vehicle_id.id
    galery_to_delete = Gallery.query.get(galery_id)
    db.session.delete(galery_to_delete)
    db.session.commit()
    return redirect(url_for('edit_gallery', vehicle_id=vehicle_id))


@app.route('/billyregister', methods=["GET", "POST"])
def register():

    if request.method == "POST":

        if User.query.filter_by(email=request.form.get('email')).first():
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=12
        )
        new_user = User(
            email=request.form.get('email'),
            name=request.form.get('name'),
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("home"))

    return render_template("/br/register.html", logged_in=current_user.is_authenticated)

@app.route('/billylogin', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        # Email doesn't exist or password incorrect.
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('home'))

    return render_template("/br/login.html", logged_in=current_user.is_authenticated)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

############## English Route #################

@app.route('/en-us')
def en_home():
    sub_categories = Subcategory.query.all()
    return render_template("/en/index.html", sub_categories=sub_categories)

@app.route('/en-us/about')
def en_about():
    sub_categories = Subcategory.query.all()
    return render_template("/en/about.html", sub_categories=sub_categories)

@app.route('/en-us/faq')
def en_faq():
    sub_categories = Subcategory.query.all()
    return render_template("/en/faq.html", sub_categories=sub_categories)

@app.route('/en-us/category/<en_name>')
def en_category_selected(en_name):
    en_name = Category.query.filter(Category.en_name==en_name).first()
    subcategorys = Subcategory.query.get(en_name.subcategory_id)
    all_vehicles = Vehicles.query.filter(Vehicles.category.contains(en_name.id))
    sub_categories = Subcategory.query.all()
    return render_template('/en/categoria.html', sub_categories=sub_categories, category=en_name, all_vehicles=all_vehicles, subcategory=subcategorys)

@app.route('/en-us/vehicle/<int:vehicle_id>')
def en_show_vehicle(vehicle_id):
    requested_vehicle = Vehicles.query.get(vehicle_id)
    category = Category.query.filter(Category.id == requested_vehicle.category).first()
    sub_categories = Subcategory.query.all()
    return render_template('/en/vehicle.html', sub_categories=sub_categories, vehicle=requested_vehicle, category=category)





if __name__ == "__main__":
    app.run(debug=True)



