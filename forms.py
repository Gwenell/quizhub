from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, FieldList, FormField, BooleanField, FileField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class QuizForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Create Quiz')

class AnswerForm(FlaskForm):
    answer = StringField('Answer', validators=[DataRequired()])
    correct = BooleanField('Correct')

class QuestionForm(FlaskForm):
    text = StringField('Question Text', validators=[DataRequired()])
    type = SelectField('Type', choices=[('multiple', 'Multiple Choice'), ('boolean', 'True/False')], validators=[DataRequired()])
    answers = FieldList(FormField(AnswerForm), min_entries=2, max_entries=4)
    media_file = FileField('Media File')
    submit = SubmitField('Add Question')
