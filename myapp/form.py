
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError

class NoRequiredForm(FlaskForm):
    class Meta:
        def render_field(self, field, render_kw):
            render_kw.setdefault('required', False)
            return super().render_field(field, render_kw)

class RegisterForm(NoRequiredForm):
    username = StringField('Username', render_kw={"placeholder": "Enter your username"},
                           validators=[DataRequired(message="Bắt buộc nhập"), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(message="Bắt buộc nhập")])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
