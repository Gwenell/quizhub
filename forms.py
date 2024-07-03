from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, FieldList, FormField, BooleanField, FileField
from wtforms.validators import DataRequired
from flask_babelex import _

# Form for admin login
class LoginForm(FlaskForm):
    username = StringField(_('Username'), validators=[DataRequired()])
    password = PasswordField(_('Password'), validators=[DataRequired()])
    submit = SubmitField(_('Login'))

# Form for creating a new quiz
class QuizForm(FlaskForm):
    title = StringField(_('Title'), validators=[DataRequired()])
    description = TextAreaField(_('Description'), validators=[DataRequired()])
    submit = SubmitField(_('Create Quiz'))

# Form for creating answers within a question
class AnswerForm(FlaskForm):
    answer = StringField('Answer', validators=[DataRequired()])
    correct = BooleanField('Correct')

# Form for creating a new question
class QuestionForm(FlaskForm):
    text = StringField('Question', validators=[DataRequired()])
    type = SelectField('Type', choices=[('multiple_choice', 'Multiple Choice'), ('true_false', 'True/False')], validators=[DataRequired()])
    media_file = FileField('Media File')
    answers = FieldList(FormField(AnswerForm), min_entries=4)
    submit = SubmitField('Add Question')

# Form for player to enter pseudonym
class PlayerForm(FlaskForm):
    pseudonym = StringField(_('Pseudonym'), validators=[DataRequired()])
    submit = SubmitField(_('Join Quiz'))
