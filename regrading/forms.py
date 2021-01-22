from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, SelectMultipleField, SubmitField, DecimalField, FormField, FieldList, Form
from wtforms.fields.html5 import DateField, TimeField, DateTimeField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, InputRequired, Email, EqualTo, Length, NumberRange, Optional
from datetime import datetime
from pytz import timezone
from .models import Product, Grade, Customer, Task 

# set timezone to EST, change it as needed
def local_now():
    mytz = timezone('America/New_York')
    return datetime.now(tz=mytz)

def local_today():
    return local_now().date()

def local_time():
    return local_now().time()

class SignupForm(FlaskForm):
    firstname = StringField(
        'First name',
        validators=[InputRequired()]
    )
    lastname = StringField(
        'Last name',
        validators=[InputRequired()]
    )
    email = StringField(
        'Email',
        validators=[
            Length(min=6),
            Email(message='Enter a valid email.'),
            InputRequired()
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            InputRequired(),
            Length(min=6, message='Select a stronger password.')
        ]
    )
    confirm = PasswordField(
        'Confirm Your Password',
        validators=[
            InputRequired(),
            EqualTo('password', message='Passwords must match.')
        ]
    )
    phone = StringField(
        'Phone number'
    )
    active = BooleanField(
        'Active employee?',
        default='checked',
        false_values=(0, False, 'false', '',)
        #render_kw={'checked': True}
    )
    admin = BooleanField(
        'Administrator right?',
        false_values=(0, False, 'false', '',)
    )
    submit = SubmitField('Register')


class ChangepasswordForm(FlaskForm):
    oldpassword = PasswordField(
        'Your current password',
        validators=[
            InputRequired(),
            Length(min=6, message='Your current password')
        ]
    )
    password = PasswordField(
        'New Password',
        validators=[
            InputRequired(),
            Length(min=6, message='Select a stronger password.')
        ]
    )
    confirm = PasswordField(
        'Confirm Your Password',
        validators=[
            InputRequired(),
            EqualTo('password', message='Passwords must match.')
        ]
    )

class LoginForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[
            InputRequired(),
            Email(message='Enter a valid email.')
        ]
    )
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Log In')

class ProductForm(FlaskForm):
    name = StringField(
        'Produce name',
        validators=[InputRequired()]
    )

class GradeForm(FlaskForm):
    name = StringField(
        'Grade name',
        validators=[InputRequired()]
    )

class CustomerForm(FlaskForm):
    name = StringField(
        'Customer name',
        validators=[InputRequired()]
    )

class OldsizecaseForm(Form):
    size = StringField(
        'Size',
        validators=[InputRequired()])
    case = DecimalField(
        'Case#',
        validators=[InputRequired(), NumberRange(min=1, max=5000)])

class NewsizecaseForm(Form):
    grade = QuerySelectField(
        query_factory=lambda: Grade.query.order_by(Grade.name), get_label="name",
        allow_blank=True,
        validators=[DataRequired()])
    size = StringField(
        'Size',
        validators=[InputRequired()])
    case = DecimalField(
        'Case#',
        validators=[InputRequired(), NumberRange(min=1, max=5000)])

class LaborForm(Form):
    headcount = DecimalField(
        '# of workers',
        validators=[InputRequired(), NumberRange(min=1, max=100)])
    start = TimeField(
        'Start time',
        format='%H:%M',
        default=local_time,
        validators=[InputRequired()])
    end = TimeField(
        'End time',
        format='%H:%M',
        default=local_time,
        validators=[InputRequired()])
    breaks = SelectField(
        'Breaks',
        choices=[(0, 'None'), (15, '1 break'), (30, '2 breaks'), (30, 'Lunch')],
        coerce=int)

class TaskForm(FlaskForm):
    date = DateField(
        'Date',
        format='%Y-%m-%d',
        default=local_today)
    lot = StringField(
        'Lot',
        validators=[InputRequired()])
    item = StringField(
        'Item',
        validators=[InputRequired()])
    product = QuerySelectField(
        query_factory=lambda: Product.query.order_by(Product.name), get_label="name",
        allow_blank=True,
        validators=[DataRequired()])
    customer = QuerySelectField(
        'Pack for',
        query_factory=lambda: Customer.query.order_by(Customer.name), get_label="name",
        allow_blank=True,
        validators=[DataRequired()])
    oldsizecases = FieldList(FormField(OldsizecaseForm), min_entries=1, max_entries=10)
    newsizecases = FieldList(FormField(NewsizecaseForm), min_entries=1, max_entries=10)
    labors = FieldList(FormField(LaborForm), min_entries=1, max_entries=10)

class ReportForm(FlaskForm):
    fromdate = DateField(
        'Start date',
        format='%Y-%m-%d',
        default=local_today
    )
    todate = DateField(
        'End date',
        format='%Y-%m-%d',
        default=local_today
    )
    products = SelectMultipleField(
        'Products',
        choices=[(0, 'All')]+[(p.id, p.name) for p in Product.query.order_by(Product.name)], coerce=int)
    grades = SelectMultipleField(
        'Grades',
        choices=[(0, 'All')]+[(g.id, g.name) for g in Grade.query.order_by(Grade.name)], coerce=int)
    customers = SelectMultipleField(
        'Customers',
        choices=[(0, 'All')]+[(c.id, c.name) for c in Customer.query.order_by(Customer.name)], coerce=int)
    show = SelectField(
        'Report type',
        choices=[('summary', 'summary'), ('csv', 'csv'), ('daily', 'daily')]
    )