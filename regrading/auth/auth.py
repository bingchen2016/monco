from flask import redirect, render_template, make_response, flash, Blueprint, request, url_for
from flask_login import current_user, login_user, login_required, logout_user
from ..forms import LoginForm, OldsizecaseForm, NewsizecaseForm, LaborForm, TaskForm, ReportForm
from ..models import db, User, Product, Grade, Customer, Task, Oldsizecase, Newsizecase, Labor
from .. import login_manager
from datetime import datetime, date, time
from io import StringIO
import csv

# Blueprint Configuration
auth_bp = Blueprint(
    'auth_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@auth_bp.route('/', methods=['GET'])
def home():
    return render_template('index.html', title='Monco')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Log-in page for registered users.

    GET requests serve Log-in page.
    POST requests validate and redirect user to dashboard.
    """
    # Bypass if user is logged in
    if current_user.is_authenticated:
        return redirect(url_for('regrad_bp.regrad'))

    form = LoginForm()
    # Validate login attempt
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.active and user.check_password(password=form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('auth_bp.welcome'))
        flash('Invalid username/password combination')
        return redirect(url_for('auth_bp.login'))
    return render_template(
        'login.html',
        form=form,
        title='Log in.',
        template='forms-page',
        body="Log in with your User account."
    )


@auth_bp.route('/welcome')
@login_required
def welcome():
    return render_template(
        'welcome.html',
        current_user=current_user
    )


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth_bp.login'))


@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in upon page load."""
    if user_id is not None:
        return User.query.get(user_id)
    return None


@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    flash('You must be logged in to view that page.')
    return redirect(url_for('auth_bp.login'))


@auth_bp.route('/regrade', methods=['GET', 'POST'])
@login_required
def regrade():
    # mydate = date.today()
    form = TaskForm()
    """
    if form.is_submitted():
        print('we are inside, error:')
        print(form.errors)
    if form.validate():
        print('validated!')
    else:
        print('validation wrong')
        #print(form.errors)
        for idx, data in enumerate(form.newsizecases.data):
            print('index is {}'.format(idx))
            print('data is: {}'.format(data))
    """

    if form.validate_on_submit():
        existing_job = Task.query.filter(
            Task.date==form.date.data,
            Task.product_id==form.product.data.id,
            Task.lot==form.lot.data,
            Task.item==form.item.data,
            Task.customer_id==form.customer.data.id
            ).first()
        if existing_job is None:
            job = Task(
                date = form.date.data,
                product_id = form.product.data.id,
                lot = form.lot.data,
                item = form.item.data,
                customer_id = form.customer.data.id
            )
            try:
                db.session.add(job)
                db.session.flush()
            except Exception as e:
                print(e)
                return "There was a problem adding new job"
            
            for field in form.oldsizecases:
                oldsizecase = Oldsizecase(
                    task_id = job.id,
                    size = field.size.data,
                    case = field.case.data
                )
                db.session.add(oldsizecase)
                db.session.commit()
            for field in form.newsizecases:
                newsizecase = Newsizecase(
                    task_id = job.id,
                    grade_id = field.grade.data.id,
                    size = field.size.data,
                    case = field.case.data
                )
                db.session.add(newsizecase)
                db.session.commit()
            for field in form.labors:
                labor = Labor(
                    task_id = job.id,
                    headcount = field.headcount.data,
                    start = field.start.data,
                    end = field.end.data,
                    breaks = field.breaks.data
                )
                db.session.add(labor)
                db.session.commit()
            if request.form['todo'] == 'submit':  # check sumbit value
                flash('regrade task for {} completed!'.format(job.customer.name),'info')
                return redirect(url_for('auth_bp.regrade'))   
            else:
                return redirect(url_for('auth_bp.dailyreport', mydate=job.date))  
        else:
            flash('task exists, you can edit it')
            return redirect(url_for('auth_bp.updatetask', id=existing_job.id))
    return render_template(
        'task.html',
        form=form
    )

@auth_bp.route('/updatetask/<int:id>', methods=['GET', 'POST'])
@login_required
def updatetask(id=None):
    # mydate = date.today()
    task = Task.query.filter_by(id=id).first()
    if not task:
        flash('No such task exists')
        return redirect(url_for('auth_bp.regrade'))
    
    """
    #print(task.oldsizecases)
    y = "len: {}".format(task.oldsizecases.count())
    for o in task.newsizecases:
        print("o: {}, {}, {}, {}".format(o.id, o.size, o.grade_id, o.grade.name))
        o.case = o.case + 1
        db.session.commit()
        y += "size: {}; case: {}".format(o.size, o.case)

    return(y)
    """

    form = TaskForm(obj=task)
    if form.validate_on_submit():
        if (task.lot != form.lot.data or task.item != form.item.data or task.product_id != form.product.data.id or 
                task.customer_id != form.customer.data.id or task.date != form.date.data):
            task.lot = form.lot.data
            task.item = form.item.data
            task.product_id = form.product.data.id
            task.customer_id = form.customer.data.id
            task.date = form.date.data
            try:
                db.session.commit()
            except Exception as e:
                print(e)
                return "There was a problem updating this task"

        oldlist = []
        for field in form.oldsizecases:
            oldlist.append({'size': field.size.data, 'case': field.case.data})
        i = 0
        for o in task.oldsizecases:
            if i < len(oldlist):
                if o.size != oldlist[i].get('size') or o.case != oldlist[i].get('case'):
                    o.size = oldlist[i].get('size')
                    o.case = oldlist[i].get('case')
                    db.session.commit()
            else:
                db.session.delete(o)
                db.session.commit()
            i += 1
        while i < len(oldlist):
            oldsizecase = Oldsizecase(
                task_id = task.id,
                size = oldlist[i].get('size'),
                case = oldlist[i].get('case')
            )
            db.session.add(oldsizecase)
            db.session.commit()
            i += 1

        newlist = []
        for field in form.newsizecases:
            newlist.append({'size': field.size.data, 'case': field.case.data,
                'grade_id': field.grade.data.id})
        i = 0
        for n in task.newsizecases:
            if i < len(newlist):
                if n.size != newlist[i].get('size') or n.case != newlist[i].get('case') or n.grade_id != newlist[i]['grade_id']:
                    n.size = newlist[i]['size']
                    n.case = newlist[i]['case']
                    n.grade_id = newlist[i]['grade_id']
                    db.session.commit()
            else:
                db.session.delete(n)
                db.session.commit()
            i += 1
        while i < len(newlist):
            newsizecase = Newsizecase(
                task_id = task.id,
                size = newlist[i].get('size'),
                case = newlist[i].get('case'),
                grade_id = newlist[i].get('grade_id')
            )
            db.session.add(newsizecase)
            db.session.commit()
            i += 1

        lablist = []
        for field in form.labors:
            lablist.append({'headcount': field.headcount.data, 'start': field.start.data, 'end': field.end.data, 'breaks': field.breaks.data})
        i = 0
        for l in task.labors:
            if i < len(lablist):
                if (l.headcount != lablist[i].get('headcount') or 
                        l.start != lablist[i].get('start') or 
                        l.end != lablist[i].get('end') or 
                        l.breaks != lablist[i].get('breaks')):
                    l.headcount = lablist[i].get('headcount')
                    l.start = lablist[i].get('start')
                    l.end = lablist[i].get('end')
                    l.breaks = lablist[i].get('breaks')
                    db.session.commit()
            else:
                db.session.delete(l)
                db.session.commit()
            i += 1
        while i < len(lablist):
            labor = Labor(
                task_id = task.id,
                headcount = lablist[i].get('headcount'),
                start = lablist[i].get('start'),
                end = lablist[i].get('end'),
                breaks = lablist[i].get('breaks')
            )
            db.session.add(labor)
            db.session.commit()
            i += 1
        flash('regrade task {} updated successfully!'.format(task.customer.name),'info')
        return redirect(url_for('auth_bp.tasksummary', id=task.id))   
    return render_template(
        'task.html',
        id=id,
        form=form
    )


def rec_sum(task):
    """task is a Task object, return its summary:
    date, product, lot, total old and new cases, time
    """
    oldcases = 0
    newcases = 0
    dumpcases = 0
    hours = 0
    for o in task.oldsizecases:
        oldcases += o.case
    for n in task.newsizecases:
        if n.grade.name == 'Dump':
            dumpcases += n.case
        else:
            newcases += n.case
    for l in task.labors:
        today = date.today()
        duration = datetime.combine(today, l.end) - datetime.combine(today, l.start)
        dur_hour = (duration.total_seconds() - l.breaks * 60)/3600  # timedelta seconds
        hours += dur_hour * l.headcount
    hours = round(hours, 2)  # round 2 decimal
    taskdict = {
        "id": task.id,
        "date": task.date,
        "product": task.product.name,
        "customer": task.customer.name,
        "lot": task.lot,
        "oldcases": oldcases,
        "newcases": newcases,
        "dumpcases": dumpcases,
        "hours": hours
    }
    return taskdict


@auth_bp.route('/tasksummary')
@auth_bp.route('/tasksummary/<int:id>')
@login_required
def tasksummary(id=None):
    # mydate = date.today()
    if id:
        tasks = Task.query.filter_by(id=id).all() # we know its only 1
    else:
        pass
    
    records = []
    for task in tasks:
        taskdict = rec_sum(task)
        records.append(taskdict)
    csv_columns = ['date', 'product', 'customer', 'lot',
            'oldcases', 'newcases', 'dumpcases', 'hours']
    value = make_csv(records, csv_columns)
    return render_template(
        'tasksum.html',
        records=records,
        download=value
    )

@auth_bp.route('/viewtask/<int:id>')
@login_required
def viewtask(id=None):
    # mydate = date.today()
    if not id:
        return redirect(url_for('auth_bp.regrade'))
    task = Task.query.filter_by(id=id).first() 
    if not task:
        return redirect(url_for('auth_bp.regrade'))
    form = TaskForm(obj=task)
    return render_template(
        'taskview.html',
        id=id,
        form=form
    )


@auth_bp.route('/report', methods=['GET', 'POST'])
@login_required
def report():
    form = ReportForm()
    if form.validate_on_submit():
        sdate = form.fromdate.data
        edate = form.todate.data
        products = form.products.data
        grades = form.grades.data
        customers = form.customers.data
        show = form.show.data

        if show == 'daily':
            tasks = Task.query.filter(Task.date == sdate)
        else: 
            if not products:
                products=[0]
            if not grades:
                grades=[0]
            if not customers:
                customers=[0]
            
            if 0 not in products:
                if 0 not in customers:
                    if 0 not in grades:
                        tasks = db.session.query(Task).join(Newsizecase).filter(
                            Task.id == Newsizecase.task_id
                        ).filter(
                            Task.date >= sdate,
                            Task.date <= edate,
                            Task.product_id.in_(products),
                            Task.customer_id.in_(customers),
                            Newsizecase.grade_id.in_(grades)
                        )
                    else:   # no grade specified
                        tasks = Task.query.filter(
                            Task.date >= sdate,
                            Task.date <= edate,
                            Task.product_id.in_(products),
                            Task.customer_id.in_(customers)
                        )
                else:   # no customer specified
                    if 0 not in grades:
                        tasks = db.session.query(Task).join(Newsizecase).filter(
                            Task.id == Newsizecase.task_id
                        ).filter(
                            Task.date >= sdate,
                            Task.date <= edate,
                            Task.product_id.in_(products),
                            Newsizecase.grade_id.in_(grades)
                        )
                    else:   # no grade specified
                        tasks = Task.query.filter(
                            Task.date >= sdate,
                            Task.date <= edate,
                            Task.product_id.in_(products),
                        )
            else:   # no product specified
                if 0 not in customers:
                    if 0 not in grades:
                        tasks = db.session.query(Task).join(Newsizecase).filter(
                            Task.id == Newsizecase.task_id
                        ).filter(
                            Task.date >= sdate,
                            Task.date <= edate,
                            Task.customer_id.in_(customers),
                            Newsizecase.grade_id.in_(grades)
                        )
                    else:   # no grade specified
                        tasks = Task.query.filter(
                            Task.date >= sdate,
                            Task.date <= edate,
                            Task.customer_id.in_(customers)
                        )
                else:   # no customer specified
                    if 0 not in grades:
                        tasks = db.session.query(Task).join(Newsizecase).filter(
                            Task.id == Newsizecase.task_id
                        ).filter(
                            Task.date >= sdate,
                            Task.date <= edate,
                            Newsizecase.grade_id.in_(grades)
                        )
                    else:   # no grade specified
                        tasks = Task.query.filter(
                            Task.date >= sdate,
                            Task.date <= edate,
                        )

        records = []
        if show == 'summary':
            for task in tasks:
                taskdict = rec_sum(task)
                records.append(taskdict)
            csv_columns = ['date', 'product', 'customer', 'lot',
                    'oldcases', 'newcases', 'dumpcases', 'hours']
            value = make_csv(records, csv_columns)
            return render_template(
                'tasksum.html',
                records=records,
                download=value
            )
        else:
            for task in tasks:
                records = records + rec_csv(task)
            csv_columns = ['date', 'product', 'customer', 'item', 'lot',
                    'size', 'case',
                    'grade', 'nsize', 'ncase',
                    'workers', 'start', 'end', 'breaks']
            value = ''
            if show == 'csv':
                value = make_csv(records, csv_columns)
            return render_template(
                'taskdaily.html',
                records=records,
                flag=show,
                download=value
            )
    return render_template(
        'report.html',
        form=form
    )

def make_csv(records, csv_columns):
    if not records:
        return None 
    si = StringIO()
    writer = csv.DictWriter(si, fieldnames=csv_columns)
    writer.writeheader()
    for rec in records:
        # I need rec remain the same, so no pop, Dec 26 2020
        #rec.pop('id', None)  # remove key 'id', avoid KeyError
        temp_dict = {i:rec[i] for i in rec if i!='id'}
        writer.writerow(temp_dict)
    return si.getvalue()
    

@auth_bp.route('/download/<value>')
@login_required
def download(value):
    if not value:
        return redirect(url_for('auth_bp.report'))
    output = make_response(value)
    output.headers["Content-Disposition"] = "attachment; filename=export.csv"
    output.headers["Content-type"] = "text/csv"
    return output    

def rec_csv(task):
    """task is a Task object, return a list of dictionary
    date, product, lot, item, customer, (size, case), (grade, size, case),
    (#workers, start, end, breaks)
    """
    list_of_dict = []
    oldsc = []
    newsc = []
    labor = []
    for o in task.oldsizecases:
        oldsc.append({'size': o.size, 'case': o.case})
    for n in task.newsizecases:
        newsc.append({'grade': n.grade.name, 'nsize': n.size, 'ncase': n.case})
    for l in task.labors:
        labor.append({'workers': l.headcount, 'start': l.start, 'end': l.end, 'breaks': l.breaks})
    t1 = [{'id': task.id, 'date': task.date, 'product': task.product.name,
            'lot': task.lot, 'item': task.item, 'customer': task.customer.name}]
    
    i = 0
    while i < max(len(oldsc), len(newsc), len(labor), len(t1)):
        dtemp = {}
        if i < len(t1):
            dtemp.update(t1[i])
        if i < len(oldsc):
            dtemp.update(oldsc[i])
        if i < len(newsc):
            dtemp.update(newsc[i])
        if i < len(labor):
            dtemp.update(labor[i])
        list_of_dict.append(dtemp)
        i += 1
    return list_of_dict


@auth_bp.route('/dailyreport/<mydate>')
@login_required
def dailyreport(mydate):
    if not mydate:
        mydate = date.today()
    tasks = Task.query.filter(Task.date == mydate).all() 
    
    records = []
    for task in tasks:
        records = records + rec_csv(task)
    return render_template(
        'taskdaily.html',
        records=records,
        flag='daily'
    )