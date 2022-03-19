import datetime as dt
from dateutil.relativedelta import relativedelta

from flask import render_template

from app import app
from .forms import MonthForm
from db.month import Month
from db.transaction import TransactionManager

def defaultDate ():
    """Returns the default date for all pages
    """
    date = dt.date.today()
    date = date.replace(day=1)
    date = date - relativedelta(months=1)
    return date

@app.route("/")
def index():
    """The index page for the finance app
    """
    date = defaultDate()
#     form = MonthForm(data={'month_date': date})
#     if form.validate_on_submit():
#         # Handle post
#         print("Post")
#         #    date = form.cleaned_data['month_date']

#     tm = TransactionManager(date)
#     df = tm.transactionsWithTags()
#     session = Session()
#     tags = [ { c.key: getattr(row, c.key) for c in inspect(row).mapper.column_attrs} for row in session.query(Tag).order_by(Tag.name).all()]
    
#     context = {
#         'tabledata': df.to_json(orient='records', date_format='iso'),
#         'tags': tags,
#         'form': form
#     }
    return render_template('index.html', date=date)

@app.route("/month/", defaults={'date': None})
@app.route("/month/<date>")
def month(date):
    date = defaultDate() if not date else date
    return render_template('month.html', date=date)


@app.route("/api/month/<date>")
def api_month(date):
    tm = TransactionManager(date)
    df = tm.transactionsWithTags()
    return df.to_json(orient='records')

@app.route("/months/")
def months():
    return render_template('months.html')

@app.route("/api/months/")
def api_months():
    month = Month()
    
    return (
        month.months()
        .assign(effective_month=lambda x: x.effective_month.astype(str))
        .to_json(orient='records')
    )

@app.route("/diagnostics/")
def diagnostics():
    return render_template('diagnostics.html')

@app.route("/fileimport/")
def fileimport():
    return render_template('fileimport.html')
    
@app.route("/admin/")
def admin():
    return render_template('admin.html')

@app.route("/groups/")
def groups():
    return render_template('groups.html')

@app.route("/tags/")
def tags():
    return render_template('tags.html')

@app.route("/grouptags/")
def grouptags():
    return render_template('grouptags.html')

@app.route("/autotags/")
def autotags():
    return render_template('autotags.html')

@app.route("/tagfilter/")
def tagfilter():
    return render_template('tagfilter.html')

@app.route("/budget/")
def budget():
    return render_template('budget.html')

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    # form = MyForm()
    # if form.validate_on_submit():
    #     print("Boom")
    return render_template('submit.html', form=form)

@app.route("/api/tags")
def api_tags():
    return {}

@app.route("/api/tagfilter/<date>", defaults={"tags": ""})
@app.route("/api/tagfilter/<date>/<tags>")
def api_tagfilter(date, tags):
    return {}

@app.route("/api/tagfilter/<int:transation_id>/<tags>")
def api_tagtransaction(transaction_id, tags):
    return {}

@app.route("/api/tagfilter/<int:transaction_id>/<int:tag>")
def api_removetag(transaction_id, tag):
    return {}

@app.route("/api/deletegroup/<int:group_id>")
def api_deletegroup(group_id):
    return {}

@app.route("/api/addgroup/<group_name>")
def api_addgroup(group_id):
    return {}

@app.route("/api/deletetag/<int:tag_id>")
def api_deletetag(tag_id):
    return {}

@app.route("/api/addtag/<tag_name>")
def api_addtag(tag_name):
    return {}

@app.route("/api/autotag/<month>")
def api_autotag(month):
    return {}

    # path('ajax/importfile/<account>/<path:filename>', views.ajaximportfile, name='ajaximportfile'),

#{{ form.csrf_token }}
#{{ form.name.label }} {{ form.name(size=20) }}
if __name__ == "__main__":
    app.run("0.0.0.0")

#from django.shortcuts import render
#from .models import *
#from .transaction import TransactionManager
#from .readfile import ReadFile
#import datetime as dt
#import pandas as pd
#from forms.forms import MonthForm, FileUploadForm
#from django import forms
#from forms.uploads import Upload
#from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
#from sqlalchemy import inspect
#from .forms import ImportForm, NameForm
#import json
#import logging
#from dateutil.relativedelta import relativedelta
#import pickle
#from django.template import Context, Template
#from django.views.decorators.csrf import csrf_exempt
#from finance.utils import QueryRunner
#import ipdb




#def month(request, date = None):
#    """The index page for the analysis app

#    :request: TODO
#    :returns: TODO

#    """
#    date = defaultDate() if not date else date
#    if request.method == 'POST':
#        form = MonthForm(request.POST)
#        if form.is_valid():
#            date = form.cleaned_data['month_date']
#    else:
#        form = MonthForm(initial = {'month_date': date})

#    tm = TransactionManager(date)
#    df = tm.transactionsWithTags()
#    session = Session()
#    tags = [ { c.key: getattr(row, c.key) for c in inspect(row).mapper.column_attrs} for row in session.query(Tag).order_by(Tag.name).all()]
    
#    context = {
#        'tabledata': df.to_json(orient='records', date_format='iso'),
#        'tags': tags,
#        'form': form
#    }
#    return render(request, 'analysis/month.html', context)

#def months(request):
#    session = Session()
#    q = QueryRunner()
#    data = q.execute(
#            session.\
#            query(Transaction.effective_month).\
#            distinct().\
#            order_by(Transaction.effective_month), returnval = 'list')
#    newdata = []
#    for d in data:
#        newdata.append(d['effective_month'].isoformat())
#    context = {
#        'data': newdata
#    }
#    return render(request, 'analysis/months.html', context)

#def budget(request, date=None):
#    """Show a monthly budget"""
#    date = defaultDate() if not date else date
#    if request.method == 'POST':
#        form = MonthForm(request.POST)
#        if form.is_valid():
#            date = form.cleaned_data['month_date']
#    else:
#        form = MonthForm(initial = {'month_date': date})
#    tm = TransactionManager(date)
    
#    context = {
#        'form': form,
#        'budget': tm.budget()
#    }
#    return render(request, 'analysis/budget.html', context)
    

#def diagnostics(request):
#    """Do some diagnostics for the given month

#    :request: TODO
#    :returns: TODO

#    """
#    date = defaultDate()
#    if request.method == 'POST':
#        form = MonthForm(request.POST)
#        if form.is_valid():
#            date = form.cleaned_data['month_date']
#    else:
#        form = MonthForm(initial = {'month_date': date})
#    tm = TransactionManager(date)
#    context = {
#        'expenseincometransfer': tm.expenseIncomeTagged(),
#        'transferbalance': tm.transferBalanceReport(),
#        'untagged': len(tm.untagged()),
#        'form': form
#    }
#    return render(request, 'analysis/diagnostics.html', context)

#def fileimport(request):
#    """Allow file imports

#    :request: TODO
#    :returns: TODO

#    """
#    context = {}
#    if request.method == 'POST':
#        form = FileUploadForm(request.POST, request.FILES)
#        if form.is_valid():
#            upl = Upload(request.FILES['file_upload'])
#            upl.save()
#            rd = ReadFile(upl.uploadedFile())
#            rd.read()
#            context['filecontent'] = rd.df.to_json(orient='records', date_format='iso')
#            form2 = ImportForm(initial={'filepath': upl.uploadedFile()})
#            context['form2'] = form2
#            #return HttpResponseRedirect('/analysis/')
#    else:
#        form = FileUploadForm()

#    context['form'] = form
#    return render(request, 'analysis/fileimport.html', context)
    
#def tagfilter(request):
#    """Provides a list of filters to tag by

#    :request: TODO
#    :returns: TODO

#    """
#    date = defaultDate()
#    if request.method == 'POST':
#        form = MonthForm(request.POST)
#        if form.is_valid():
#            date = form.cleaned_data['month_date']
#    else:
#        form = MonthForm(initial = {'month_date': date})
#    session = Session()
#    data = [ { c.key: getattr(row, c.key) for c in inspect(row).mapper.column_attrs} for row in session.query(Tag).order_by(Tag.name).all()]
#    context = {
#        'data': data,
#        'form': form,
#    }
#    return render(request, 'analysis/tagfilter.html', context)

#def admin(request):
#    "The admin home page"
#    context = {}
#    return render(request, 'analysis/admin.html', context)

#def groups(request):
#    "Define and remove tag groups"
#    session = Session()
#    groups = [ { c.key: getattr(row, c.key) for c in inspect(row).mapper.column_attrs} for row in session.query(TagGroup).order_by(TagGroup.id).all()]
#    form = NameForm()
#    context = {
#        'groups': groups,
#        'form': form,
#    }
#    return render(request, 'analysis/groups.html', context)

#def tags(request):
#    "Define and remove tag groups"
#    session = Session()
#    tags = [ { c.key: getattr(row, c.key) for c in inspect(row).mapper.column_attrs} for row in session.query(Tag).order_by(Tag.id).all()]
#    form = NameForm()
#    context = {
#        'tags': tags,
#        'form': form,
#    }
#    return render(request, 'analysis/tags.html', context)

#@csrf_exempt
#def grouptags(request):
#    """Allows to select the tags for a group

#    :request: TODO
#    :returns: TODO

#    """
##    form = FormForm()
##    if request.method == 'POST':
##        form = FormForm(request.POST)
##
##    t = Template("""<form method="post" action=".">{{f}}<input type="submit"><form>""")
##    c = {'f': form.as_p()}
##    return HttpResponse(t.render(Context(c)))
    
#    context = {
#    }
#    return render(request, 'analysis/grouptags.html', context)

#def autotags(request):
#    """List of auto tags and the associated Regexs
#    """
#    context = {
#    }
#    return render(request, 'analysis/autotags.html', context)


#def ajaxtagfilter(request, date, tags=None):
#    """Returns the transactions filtered by tag

#    :request: TODO
#    :returns: TODO

#    """
#    date = dt.date.fromisoformat(date)
#    tm = TransactionManager(date)
#    tags = json.loads(tags)
#    df = tm.transactionTagFilter(tags)
    
#    return JsonResponse({'date': date, 'tags': tags, 'result': df.to_json(orient='records', date_format='iso')})

#def ajaxtaglist(request):
#    """Ajax: returns a list of tags with their id's

#    :request: TODO
#    :returns: TODO

#    """
#    data = [ { c.key: getattr(row, c.key) for c in inspect(row).mapper.column_attrs} for row in session.query(Tag).order_by(Tag.name).all()]
#    return JsonResponse(data, safe=False) 

#def ajaxtagtransaction(request, transaction_id, tags):
#    """Tags a transaction with the given tags

#    :request: TODO
#    :returns: TODO

#    """
#    t = tags.split(",")
#    t = [x.strip() for x in t if x]
#    tm = TransactionManager()
#    tm.tagTransaction([transaction_id], t)
#    response = {
#        'status': 'success',
#        'transaction_id': transaction_id,
#        'tags': t,
#        'tag_string': ",".join(t)
#    }
#    return JsonResponse(response)

#def ajaxremovetag(request, transaction_id, tag):
#    """Remove the specified tag, and returns the new tag string

#    :request: TODO
#    :transaction_id: TODO
#    :tag: TODO
#    :returns: TODO

#    """
#    tm = TransactionManager()
#    tm.removeTag(transaction_id, tag)
#    response = {
#        'status': 'success',
#        'transaction_id': transaction_id,
#        'tag': tag,
#        'tag_string': tm.transactionTags(transaction_id, True)
#    }
#    return JsonResponse(response)
    
#def ajaximportfile(request, account, filename):
#    """Imports the specified file
#    :returns: TODO

#    """
#    response = {
#        'status': 'success',
#        'account': account,
#        'filename': filename
#    }
#    try:
#        rd = ReadFile(filename)
#        rd.read()
#        rd.save(account)
#    except:
#        response['status'] = 'error'

#    return JsonResponse(response)

#def ajaxdeletegroup(request, group_id):
#    """Deletes a group and return new group list

#    :request: TODO
#    :returns: TODO

#    """
#    session = Session()
#    group = session.query(TagGroup).get(group_id)
#    if group:
#        session.delete(group)
#        session.commit()
#    groups = [ { c.key: getattr(row, c.key) for c in inspect(row).mapper.column_attrs} for row in session.query(TagGroup).order_by(TagGroup.id).all()]

#    response = {
#        'status': 'success',
#        'groups': groups,
#    }
#    return JsonResponse(response)

#def ajaxaddgroup(request, group_name):
#    """Adds a group and return new group list

#    :request: TODO
#    :returns: TODO

#    """
#    session = Session()
#    group = TagGroup(name=group_name)
#    if group:
#        session.add(group)
#        session.commit()
#    groups = [ { c.key: getattr(row, c.key) for c in inspect(row).mapper.column_attrs} for row in session.query(TagGroup).order_by(TagGroup.id).all()]

#    response = {
#        'status': 'success',
#        'groups': groups,
#    }
#    return JsonResponse(response)

#def ajaxaddtag(request, tag_name):
#    """Adds a tag and return the list of tags

#    :request: TODO
#    :returns: TODO

#    """
#    session = Session()
#    tag = Tag(name=tag_name)
#    if tag:
#        session.add(tag)
#        session.commit()
#    tags = [ { c.key: getattr(row, c.key) for c in inspect(row).mapper.column_attrs} for row in session.query(Tag).order_by(Tag.id).all()]

#    response = {
#        'status': 'success',
#        'tags': tags,
#    }
#    return JsonResponse(response)

#def ajaxdeletetag(request, tag_id):
#    """Removes a tag and returns the new list of tags

#    :request: TODO
#    :returns: TODO

#    """
#    session = Session()
#    tag = session.query(Tag).get(tag_id)
#    if tag:
#        session.delete(tag)
#        session.commit()
#    tags = [ { c.key: getattr(row, c.key) for c in inspect(row).mapper.column_attrs} for row in session.query(Tag).order_by(Tag.id).all()]

#    response = {
#        'status': 'success',
#        'tags': tags,
#    }
#    return JsonResponse(response)

#def ajaxautotag(selfrequest, month):
#    """Auto tag all transactions in the current month"""
#    response = {
#        'status': 'success',
#        'month': month
#    }
#    try:
#        month = dt.date.fromisoformat(month)
#        trans = TransactionManager(month)
#        trans.auto_tag()
#    except Exception as exc:
#        response['status'] = 'error'
#        print(exc)
    
#    return JsonResponse(response)

#"""
#An example of minimum requirements to make MultiValueField-MultiWidget for Django forms.
#"""
#class MultiWidgetBasic(forms.widgets.MultiWidget):
#    def __init__(self, attrs=None):
#        widgets = [forms.TextInput(),
#                   forms.TextInput()]
#        super(MultiWidgetBasic, self).__init__(widgets, attrs)

#    def decompress(self, value):
#        if value:
#            return pickle.loads(value)
#        else:
#            return ['', '']


#class MultiExampleField(forms.fields.MultiValueField):
#    widget = MultiWidgetBasic

#    def __init__(self, *args, **kwargs):
#        list_fields = [forms.fields.CharField(max_length=31),
#                       forms.fields.CharField(max_length=31)]
#        super().__init__(list_fields, *args, **kwargs)

#    def compress(self, values):
#        ## compress list to single object                                               
#        ## eg. date() >> u'31/12/2012'                                                  
#        return pickle.dumps(values)


#class FormForm(forms.Form):
#    a = forms.BooleanField(required=False)
#    b = forms.CharField(max_length=32, required=False)
#    c = forms.CharField(max_length=32, widget=forms.widgets.Textarea(), required=False)
#    d = forms.CharField(max_length=32, widget=forms.widgets.SplitDateTimeWidget(), required=False)
#    e = forms.CharField(max_length=32, widget=MultiWidgetBasic(), required=False)
#    f = MultiExampleField(required=False)


#def page(request):
#    form = FormForm()
#    if request.method == 'POST':
#        form = FormForm(request.POST)

#    t = Template("""<form method="post" action=".">{{f}}<input type="submit"><form>""")
#    c = {'f': form.as_p()}
#    return HttpResponse(t.render(Context(c)))
