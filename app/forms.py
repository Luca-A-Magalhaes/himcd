from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, TextAreaField, DateTimeField, PasswordField
from wtforms.validators import DataRequired
from app.models import User
from app import db
from werkzeug.security import check_password_hash
from flask_babelex import lazy_gettext as _l
from app.compare import get_all_places, get_all_countries_response
# countries_init = get_all_countries()

class CompareCountryForm(FlaskForm):
    # numCountries = StringField('Num COuntries', validators=[DataRequired()])
    countries = SelectField(_l('Please choose a place'), choices=[(c, c) for c in get_all_places(level='countries')], validators=[DataRequired()])
    submit = SubmitField(_l('Show Report'))

class CompareCityForm(FlaskForm):
    # numCountries = StringField('Num COuntries', validators=[DataRequired()])
    cities = SelectField(_l('Please choose a city'), choices=[(c, c) for c in get_all_places(level='cities')], validators=[DataRequired()])
    submit = SubmitField(_l('Show Report'))

class SubmitEventRequestForm(FlaskForm):
    country = SelectField(_l('Please choose a place'), choices=[(c, c) for c in get_all_places(level='countries')], validators=[DataRequired()])
    date = DateTimeField(_l('Event date'), validators=[DataRequired()])
    desc = StringField(_l('Briefly describe the event'), validators=[DataRequired()])
    fulltext = TextAreaField(_l('Describe the event in detail'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit event'))

# Define login and registration forms (for flask-login)
class LoginForm(FlaskForm):
    email = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Invalid user')

        # we're comparing the plaintext pw with the the hash from the db
        if not check_password_hash(user.password, self.password.data):
        # to compare plain text passwords use
        # if user.password != self.password.data:
            raise validators.ValidationError('Invalid password')

    def get_user(self):
        return db.session.query(User).filter_by(email=self.email.data).first()
class ResponseCountryForm(FlaskForm):
    # numCountries = StringField('Num COuntries', validators=[DataRequired()])
    countries = SelectField(_l('Please choose a place'), choices=[(c, c) for c in get_all_countries_response()], validators=[DataRequired()])
    # submit = SubmitField(_l('Show Report'))
    
