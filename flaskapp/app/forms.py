
from flask_wtf import FlaskForm
from wtforms.fields import StringField, DateField
from wtforms.validators import DataRequired

class MyForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])

# class ImportForm(forms.Form):
#     account = forms.fields.ChoiceField(label='Account', choices=session.query(Account.id, Account.name).all()) 
#     filepath = forms.fields.CharField(widget=forms.HiddenInput())

# class NameForm(forms.Form):
#     name_field = forms.fields.CharField(label='Name')

class MonthForm(FlaskForm):
    month_date = DateField('Month') 

# class DateForm(forms.Form):
#     month_date = fields.DateField(label='Date') 

# class FileUploadForm(forms.Form):
#     file_upload = forms.fields.FileField(label='File name')
