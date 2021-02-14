from flask import redirect, url_for, request, abort
from app import app
from app.forms import LoginForm
from app.models import *
from flask_admin import Admin, AdminIndexView
from flask_admin import expose
from flask_login import LoginManager
import flask_login as login
from flask_security import Security, SQLAlchemyUserDatastore
from flask_admin.contrib.sqla import ModelView

# Initialize admin users
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Initialize flask-login
def init_login():
    login_manager = LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(User).get(user_id)

# Create customized index view class that handles login & registration
class MyAdminIndexView(AdminIndexView):

    @expose('/')
    def index(self):
        print('/')
        print(login.current_user)
        if not login.current_user.is_authenticated:
            print('not loged')
            return redirect(url_for('.login_view'))
        return super(MyAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = LoginForm()
        if form.validate_on_submit():
            print('form validate')
            user = form.get_user()
            login.login_user(user)
            next_page = request.args.get('next')

            # is_safe_url should check if the url is safe for redirects.
            # if not is_safe_url(next):
            #     return abort(400)

            return redirect(next_page or url_for('.index'))

        print('loading index view')
        self._template_args['form'] = form
        return super(MyAdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('.index'))

# Initialize flask-login
init_login()

# Making ModelView
class AdminModelView(ModelView):

    def is_accessible(self):
        return login.current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('admin.login_view', next=request.url))

# Create admin
admin = Admin(app, 'HIMCD: COVID-19', index_view=MyAdminIndexView(), base_template='admin/master.html')
admin.add_view(AdminModelView(Event, db.session))
