from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, URLField, FloatField, IntegerField, SelectField, FileField
from wtforms.validators import DataRequired, URL, NumberRange, InputRequired
from flask_ckeditor import CKEditorField
from werkzeug.utils import secure_filename


class VehicleForm(FlaskForm):
    en_title = StringField('English Title', validators=[DataRequired()])
    br_title = StringField('Brazilian Title', validators=[DataRequired()])
    en_description = CKEditorField('English description', validators=[DataRequired()])
    br_description = CKEditorField('Brazilian description', validators=[DataRequired()])
    category = SelectField('Category', choices=[], validators=[DataRequired()])
    en_body = CKEditorField('English Body', validators=[DataRequired()])
    br_body = CKEditorField('Brazilian Body', validators=[DataRequired()])
    image = FileField('Primary Image', validators=[DataRequired()])
    image_video = FileField('Video Image')
    video = StringField('Youtube Video')
    br_price = FloatField('Vehicle Real Price', validators=[DataRequired()])
    en_price = FloatField('Vehicle Dolar Price', validators=[DataRequired()])
    discount_value = IntegerField('Valor desconto(0 a 99)',validators=[NumberRange(min=0, max=99, message='Valor invalido'), InputRequired()])
    tebex = URLField('Tebex Link', validators=[URL(), DataRequired()])
    submit = SubmitField('Submit')

    def validate_image(form, field):
        if field.data:
            field.data = secure_filename(field.data.filename)

class GalleryForm(FlaskForm):
    vehicle_choose = SelectField('Vehicle Br Name', choices=[], validators=[DataRequired()])
    images = FileField('Add Image', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_image(form, field):
        if field.data:
            field.data = secure_filename(field.data.filename)

class CategoryForm(FlaskForm):
    en_name = StringField('English Title', validators=[DataRequired()])
    br_name = StringField('Brazilian Title', validators=[DataRequired()])
    subcategory_id = SelectField('Subcategory', choices=[], validators=[DataRequired()])
    submit = SubmitField('Submit')

class SubcategoryForm(FlaskForm):
    en_name = StringField('English Title', validators=[DataRequired()])
    br_name = StringField('Brazilian Title', validators=[DataRequired()])
    submit = SubmitField('Submit')


