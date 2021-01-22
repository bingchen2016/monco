from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    """User account model."""
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}
    id = db.Column(
        db.Integer,
        primary_key=True)
    firstname = db.Column(
        db.String(50),
        nullable=False,
        unique=False)
    lastname = db.Column(
        db.String(50),
        nullable=False,
        unique=False)
    email = db.Column(
        db.String(50),
        nullable=False,
        unique=True)
    phone = db.Column(
        db.String(20),
        nullable=True,
        unique=False)
    active = db.Column(
        db.Boolean,
        nullable=False,
        default=True)
    admin = db.Column(
        db.Boolean,
        nullable=False,
        default=False)
    password = db.Column(
        db.String(100),
        primary_key=False,
        unique=False,
        nullable=False)
    created_on = db.Column(
        db.DateTime,
        index=False,
        unique=False,
        nullable=True)

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password, method='sha256')

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User {} {}>'.format(self.firstname, self.lastname)


class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(
        db.Integer,
        primary_key=True)
    name = db.Column(
        db.String(70),
        unique=True,
        nullable=False)
    tasks = db.relationship('Task', backref='product', lazy='dynamic')

class Grade(db.Model):
    __tablename__ = 'grade'
    id = db.Column(
        db.Integer,
        primary_key=True)
    name = db.Column(
        db.String(20),
        unique=True,
        nullable=False)
    newsizecases = db.relationship('Newsizecase', backref='grade')

class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(
        db.Integer,
        primary_key=True)
    name = db.Column(
        db.String(50),
        unique=True,
        nullable=False)
    tasks = db.relationship('Task', backref='customer')

class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(
        db.Integer,
        primary_key=True)
    date = db.Column(
        db.Date,
        unique=False,
        nullable=False)
    lot = db.Column(
        db.String(30),
        unique=False,
        nullable=False)
    item = db.Column(
        db.String(30),
        unique=False,
        nullable=False)
    product_id = db.Column(
        db.Integer,
        db.ForeignKey('product.id'),
        nullable=False)
    customer_id = db.Column(
        db.Integer,
        db.ForeignKey('customer.id'),
        nullable=False)
    oldsizecases = db.relationship('Oldsizecase', backref='task', lazy='dynamic')
    newsizecases = db.relationship('Newsizecase', backref='task', lazy='dynamic')
    labors = db.relationship('Labor', backref='task', lazy='dynamic')

class Oldsizecase(db.Model):
    __tablename__ = 'oldsizecase'
    id = db.Column(
        db.Integer,
        primary_key=True)
    size = db.Column(
        db.String(50),
        nullable=False)
    case = db.Column(
        db.Float,
        nullable=False)
    task_id = db.Column(
        db.Integer,
        db.ForeignKey('task.id'),
        nullable=False)

class Newsizecase(db.Model):
    __tablename__ = 'newsizecase'
    id = db.Column(
        db.Integer,
        primary_key=True)
    size = db.Column(
        db.String(50),
        nullable=False)
    case = db.Column(
        db.Float,
        nullable=False)
    grade_id = db.Column(
        db.Integer,
        db.ForeignKey('grade.id'))
    task_id = db.Column(
        db.Integer,
        db.ForeignKey('task.id'))

class Labor(db.Model):
    __tablename__ = 'labor'
    id = db.Column(
        db.Integer,
        primary_key=True)
    headcount = db.Column(
        db.Float,
        nullable=False)
    start = db.Column(
        db.Time,
        nullable=False)
    end = db.Column(
        db.Time,
        nullable=False)
    breaks = db.Column(
        db.Float,
        nullable=False)
    task_id = db.Column(
        db.Integer,
        db.ForeignKey('task.id'))
