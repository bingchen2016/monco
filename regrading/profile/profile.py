from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from ..forms import ChangepasswordForm
from ..models import db

# Blueprint Configuration
profile_bp = Blueprint(
    'profile_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@profile_bp.route('/profile', methods=['GET'])
def user_profile():
    """Logged-in user profile page."""
    return render_template(
        'profile.html',
        title='User Profile',
        template='profile-template',
        user=current_user
    )


@profile_bp.route('/profile/changepassword', methods=['GET', 'POST'])
@login_required
def changepassword():
    form = ChangepasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(password=form.oldpassword.data):
            current_user.set_password(form.password.data)

            try:
                db.session.commit()
                flash('password changed!', 'info')
            except Exception as e:
                print(e)
                return "There was a problem updating your password"
            return redirect(url_for('profile_bp.user_profile'))
        else:
            flash('Your existing password does not match')
    return render_template(
        'password.html',
        title='change password',
        user=current_user,
        form=form
    )
