from sapp import app,db,api
from flask import render_template, request,json,Response, redirect , url_for , session, jsonify
from sapp.models import User, rubics, projects , samatrix
from sapp.forms import LoginForm, RegisterForm
from flask import flash
from werkzeug.utils import secure_filename
import os
import pandas as pd
from flask_restplus import Resource
from sapp import db

#from flask_user import role_required, UserManager, UserMixin
#from flask_mail import Mail

#############################
#API
@api.route('/api','/api/')
class GetAndPost(Resource):
    #get all
    def get(self):
        return jsonify(User.objects.all())

    #post data
    def post(self):
        data = api.payload
        user=User(userId=data['userId'], email=data['email'], firstName=['firstName'], lastName=['lastName'] )
        user.set_password(data['password'])
        user.save()
        return jsonify(User.objects(userId = data['userId']))


@api.route('/api/<idx>')
class GetUpdateDElte(Resource):
    def get(self,idx):
        return jsonify(User.objects(userId=idx))

    def put(self,idx):
        data = api.payload
        User.objects(user)

#############################


@app.route("/")
@app.route("/index")
@app.route("/home")
def home():
    if session.get('username'):
        lo = True
    else:
        lo = False
    return render_template("index.html", home=lo)

# login and registeration route
@app.route("/login", methods=['GET','POST'])
def login():
    if session.get('username'):
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.objects(email=email).first()
        if user and password ==user.password:
            flash(f"{user.firstName}, you are successfully logged in!", "success")
            session['userId'] = user.userId
            session['username'] = user.firstName
            return redirect("/sdash") # implement various routes depemnding on the security roles
        else:
            flash("Sorry, something went wrong.","danger")
    return render_template("auth/login.html", title="Login", form=form, login=True )


@app.route("/register",methods=['GET','POST']) # once register it should go to the admin to approve and connect the supervisor to the project
def register():
    if session.get('username'):
        return redirect(url_for('home'))
    # check if the student is registered or not using a unique user Id
    form = RegisterForm()
    if form.validate_on_submit():
        userId = form.userId.data
        email = form.email.data
        password = form.password.data
        firstName = form.firstName.data
        lastName = form.lastName.data

        user=User(userId=userId, email=email, firstName=firstName, lastName=lastName )
        user.set_password(password)
        user.save()
        flash("you are successfully registeres!","success")
        return redirect(url_for('sdash'))
    return render_template("auth/register.html", title="Register", form=form, register=True )

@app.route("/logout")
def logout():
    session['userId']=False
    session.pop('username',None)
    return redirect(url_for('home'))

#####################################################
# dashboard routes
@app.route("/sdash/")
def sdash():
    if not session.get('username'):
        return redirect(url_for('login'))
    userId= session.get('userId')
    su = projects.objects(userId=userId).first()
    mgroup = projects.objects(groupNo=su.groupNo)
    return render_template("dash/sdash.html",sdata= su, mgroup=mgroup, sdash=True)


@app.route("/admindash",methods=['GET','POST'])
def admindash():
    ru=rubics.objects()
    proj = projects.objects.all()
    return render_template("dash/admindash.html",ru =ru, proj=proj, adminDash=True)

@app.route("/fdash")
def fdash():
    ru=rubics.objects()
    proj = projects.objects.all()
    return render_template("dash/fdash.html", proj=proj, ru=ru,fdash=True)

# submitting the student response matrix
@app.route("/saSubmit",methods=['GET','POST'])
def saSubmit():


    userId= session.get('userId')
    name = session['username']
    # resetting the data in samatrix for the user
    samatrix.objects(sid=userId).delete()

    # initializing the rubics objects
    ru=rubics.objects()

    # retrieving the relevant data from Projects
    su = projects.objects(userId=userId).first()
    mgroup = projects.objects(groupNo=su.groupNo)
    # creating the sa matrix table variable

    for g in mgroup:
        sid = userId
        fsid = g.userId
        fsname = g.firstName +" "+ g.lastName

        for r in ru:
            indicator = r.Indicator
            value = 1
            sam = samatrix(sid= sid, fsid=fsid,fsname=fsname,Indicator=indicator,value=value)
            sam.save()
            print(sam)
            print("initializing samatrix for {id}".format(id=fsid) )
            #! if already there then update it don't create more variables

    # retrieving the values for the id from database
    samat=samatrix.objects(sid=userId)


    return render_template("saSubmit.html",samat = samat,mgroup=mgroup, ru =ru, name = name,  saSubmit=True)

# sasubmit fo rthe values

@app.route("/samsubmit",methods=['GET','POST'])
def samsubmit():
    # getting value from form and saving it to samatrix
    if request.method == 'POST':
        value = request.form.get('val')
        print(value)
        flash("response have been saved!","success")
    else:
        flash("response not saved","danger")
        return redirect(url_for('saSubmit'))

    return redirect(url_for('fsa'))


# route for fsa
@app.route("/fsa")
def fsa():
    ## update the assessment status to 1 
    return render_template("other/fsa.html")


#############################
# upload the excel file to the database
@app.route('/uploader', methods=['GET','POST'])
def uploader():
    if request.method =='POST':

        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part',"danger")
            return redirect(url_for('admindash'))

        f=request.files['file']
        print(f.filename)
        # if user does not select file , browser also submit an empty part filename
        if f.filename =='':
            flash('No selected File',"danger")
            return redirect(url_for('admindash'))

        if f.filename != 'rubicsMetrix.xlsx':
            flash('please upload the correct rubix file',"danger")
            return redirect(url_for('admindash'))

        sf = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'],sf))
        flash("uploaded file successfully","success")
        rubics.uploadnew()        # update the rubics data in the database


        return redirect(url_for('admindash'))


######################################
# viewing the user database

@app.route("/user")
def user():
    #User(userId=111,firstName="Christian",lastName="hur",email="christian@uta.com", password="abc1234").save()
    #User(userId=222,firstName="Mary",lastName="jane",email="mary.jane@uta.com", password="password123").save()

    users = User.objects.all()
    return render_template("user.html",users=users)

@app.route("/project")
def project():
    proj = projects.objects.all()
    return render_template("project.html",proj=proj)