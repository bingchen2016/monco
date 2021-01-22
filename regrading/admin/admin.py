from flask import Blueprint, flash, render_template, redirect, request, url_for
from flask_login import current_user, login_required
from ..models import db, User, Product, Grade, Customer
from ..forms import SignupForm, ProductForm, GradeForm, CustomerForm

# Blueprint Configuration
admin_bp = Blueprint(
    'admin_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@admin_bp.route('/admin', methods=['GET'])
@login_required
def admin():
    return render_template('admin.html')


@admin_bp.route('/admin/listusers')
@login_required
def listusers():
    if not current_user.admin:
        return redirect(url_for('admin_bp.admin'))
    users = User.query.order_by(User.id).all()
    return render_template('userlist.html', users=users)

@admin_bp.route('/admin/listitems')
@admin_bp.route('/admin/listitems/<string:category>')
@login_required
def listitems(category=None):
    if not category:
        flash('Nothing to show!')
        return redirect(url_for('admin_bp.admin'))
    if not current_user.admin:
        return redirect(url_for('admin_bp.admin'))
    if category == 'Product':
        items = Product.query.order_by(Product.id).all()
    elif category == 'Grade':
        items = Grade.query.order_by(Grade.id).all()
    else:
        items = Customer.query.order_by(Customer.id).all()
    return render_template('itemlist.html', items=items, category=category)


@admin_bp.route('/admin/signup', methods=['GET', 'POST'])
@login_required
def signup():
    if not current_user.admin:
        return redirect(url_for('admin_bp.admin'))

    form = SignupForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user is None:
            user = User(
                firstname=form.firstname.data,
                lastname=form.lastname.data,
                email=form.email.data,
                phone=form.phone.data,
                active=form.active.data,
                admin=form.admin.data
            )
            user.set_password(form.password.data)
            try:
                db.session.add(user)
                db.session.commit()  # Create new user
                flash("{} {}'s account is created!".format(
                    user.firstname, user.lastname), 'info')
                return redirect(url_for('admin_bp.listusers'))
            except Exception as e:
                print(e)
                return "There was a problem adding new user"
        flash('A user already exists with that email address.')
    return render_template(
        'signup.html',
        title='Create an Account.',
        form=form
    )

@admin_bp.route('/admin/itemadd', methods=['GET', 'POST'])
@admin_bp.route('/admin/itemadd/<string:category>', methods=['GET', 'POST'])
@login_required
def itemadd(category=None):
    if not current_user.admin or not category:
        return redirect(url_for('admin_bp.admin'))

    if category == 'Product':
        form = ProductForm()
    elif category == 'Grade':
        form = GradeForm()
    else:
        form = CustomerForm()
    if form.validate_on_submit():
        if category == 'Product':
            existing_item = Product.query.filter_by(name=form.name.data).first()
        elif category == 'Grade':
            existing_item = Grade.query.filter_by(name=form.name.data).first()
        else:
            existing_item = Customer.query.filter_by(name=form.name.data).first()
        if existing_item is None:
            if category == 'Product':
                item = Product(name=form.name.data)
            elif category == 'Grade':
                item = Grade(name=form.name.data)
            else:
                item = Customer(name=form.name.data)
            try:
                db.session.add(item)
                db.session.commit()
                flash("{} {} is created!".format(
                    item.name, category), 'info')
                return redirect(url_for('admin_bp.listitems', category=category))
            except Exception as e:
                print(e)
                return "There was a problem adding new {}".format(category)
        flash('This {} already exists.'.format(category))
    return render_template(
        'itemadd.html',
        form=form,
        category=category
    )

@admin_bp.route('/admin/useredit', methods=['GET', 'POST'])
@admin_bp.route('/admin/useredit/<int:id>', methods=['GET', 'POST'])
@login_required
def useredit(id=None):
    if not current_user.admin:
        return redirect(url_for('admin_bp.admin'))

    if not id:
        flash("No user record to update!")
        return redirect(url_for('admin_bp.listusers'))
    reset = request.args.get('reset')
    auser = User.query.filter_by(id=id).first()
    if not auser:
        flash('No such user exists')
        return redirect(url_for('admin_bp.listusers'))

    # this didn't populate checkboxes
    #form = SignupForm(formdata=request.form, obj=auser)
    form = SignupForm(obj=auser)
    if reset and reset == 'y':
        del form.firstname
        del form.lastname
        del form.email
        del form.phone
        del form.active
        del form.admin
    else:
        del form.password
        del form.confirm

    if form.validate_on_submit():
        if reset and reset == 'y':
            auser.set_password(form.password.data)
        else:
            auser.firstname = form.firstname.data
            auser.lastname = form.lastname.data
            auser.email = form.email.data
            auser.phone = form.phone.data
            auser.active = form.active.data
            auser.admin = form.admin.data

        try:
            db.session.commit()
            flash('user "{} {}" updated!'.format(
                auser.firstname, auser.lastname), 'info')
        except Exception as e:
            print(e)
            return "There was a problem updating new user"
        return redirect(url_for('admin_bp.listusers'))
    return render_template(
        'useredit.html',
        title='Update user',
        user=auser,
        reset=reset,
        form=form
    )


@admin_bp.route('/admin/itemedit', methods=['GET', 'POST'])
@admin_bp.route('/admin/itemedit/<int:id>/<string:category>', methods=['GET', 'POST'])
@login_required
def itemedit(id=None, category=None):
    if not current_user.admin or not id or not category:
        return redirect(url_for('admin_bp.admin'))
    if category == 'Product':
        item = Product.query.filter_by(id=id).first()
    elif category == 'Grade':
        item = Grade.query.filter_by(id=id).first()
    else:
        item = Customer.query.filter_by(id=id).first()
    if not item:
        flash('No such {} exists'.format(category))
        return redirect(url_for('admin_bp.listitems', category=category))

    if category == 'Product':
        form = ProductForm(obj=item)
    elif category == 'Grade':
        form = GradeForm(obj=item)
    else:
        form = CustomerForm(obj=item)
    if form.validate_on_submit():
        item.name = form.name.data
        try:
            db.session.commit()
            flash('{} "{}" updated!'.format(
                category, item.name), 'info')
        except Exception as e:
            print(e)
            return "There was a problem updating {}".format(category)
        return redirect(url_for('admin_bp.listitems', category=category))
    return render_template(
        'itemedit.html',
        item=item,
        form=form,
        category=category
    )

@admin_bp.route('/admin/itemdel', methods=['GET', 'POST'])
@admin_bp.route('/admin/itemdel/<int:id>/<string:category>', methods=['GET', 'POST'])
@login_required
def itemdel(id=None, category=None):
    if not current_user.admin or not id or not category:
        return redirect(url_for('admin_bp.admin'))

    if category == 'Product':
        item = Product.query.get_or_404(id)
    elif category == 'Grade':
        item = Grade.query.get_or_404(id)
    else:
        item = Customer.query.get_or_404(id)
    try:
        db.session.delete(item)
        db.session.commit()
        flash('{} "{}" deleted!'.format(
            category, item.name), 'info')
    except Exception as e:
        print(e)
        return "There was a problem deleting {}".format(category)
    return redirect(url_for('admin_bp.listitems', category=category))
