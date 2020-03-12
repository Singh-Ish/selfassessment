from sapp import app,db,api,mail
from flask import render_template, request,json,Response, redirect , url_for , session, jsonify
from sapp.models import User, rubics, projects, samatrix, emailtemplate
from sapp.forms import LoginForm, RegisterForm 
from flask import flash
from werkzeug.utils import secure_filename
import os
import pandas as pd
from flask_restplus import Resource
from sapp import db
from flask_mail import Mail, Message

#from flask_user import role_required, UserManager, UserMixin
#from flask_mail import Mail

#############################
#API
@api.route('/api','/api/')
class GetAndPost(Resource):
    #get all
    def get(self):
        return jsonify(samatrix.objects.all())

    #post data
    def post(self):
        data = api.payload
        matrix=samatrix(sid=data['sid'], fsid=data['fsid'], fsname=data['fsname'], Indicator=data['Indicator'],value=data['value'] )
        matrix.save()
        return jsonify(samatrix.objects(userId = data['userId']))


@api.route('/api/<idx>')
class GetUpdateDelete(Resource):
    # get data request
    def get(self,idx):
        return jsonify(samatrix.objects(sid=idx))

    # put data
    def put(self,idx):
        data = api.payload
        samatrix.objects(sid = idx).update(**data)
        return jsonify(samatrix.objects(sid=idx))

    # delete data  reqest
    def delete(self,idex):
        samatrix.objects(sid=idx).delete()
        return jsonify("User is deleted")
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
    etemp = emailtemplate.objects().first()
    return render_template("dash/admindash.html",etemp=etemp,ru =ru, proj=proj, adminDash=True)

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
    # creating the sa matrix table variable and setting the deafult value to 4 ( max )

    for g in mgroup:
        sid = userId
        fsid = g.userId
        fsname = g.firstName +" "+ g.lastName

        for r in ru:
            indicator = r.Indicator
            value = 4
            sam = samatrix(sid= sid, fsid=fsid,fsname=fsname,Indicator=indicator,value=value)
            sam.save()
            print("The assessment drop down list have been reset")
            #print(sam)
            #print("initializing samatrix for {id}".format(id=fsid) )
            #! if already there then update it don't create more variables

    # retrieving the values for the id from database
    samat=samatrix.objects(sid=userId)

    # retrieving the value of drop down and saving it to database 
    if request.method == 'POST':
        value = request.form.getlist('val')
        print(value)
        flash("response have been saved!","success")
        return redirect(url_for('fsa'))

    return render_template("saSubmit.html",samat = samat,mgroup=mgroup, ru =ru, name = name,  saSubmit=True)




# route for fsa
@app.route("/fsa")
def fsa():
    ## update the assessment status to 1 
    
    userId= session.get('userId')  
    su = projects.objects(userId=userId).first()
    if (su.assessmentStatus==0):
        print(" the assessment status is")
        print(su.assessmentStatus)
        su.assessmentStatus=1
        su.save()
    print("Alredy submitted the assessment")
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



############# sending a Email ############

@app.route('/emailone', methods=['GET', 'POST'])
def emailone():
    id = request.form["userId"]
    print("id clicked is ",id)
    #print(id)
    s = User.objects(userId=id).first()
    print(s.email)
    temail = emailtemplate.objects().first()
    return render_template("email.html", s=s, temail=temail)


@app.route('/emailall', methods=['GET', 'POST'])
def emailall():

    stu = projects.objects(assessmentStatus=0)
    temail = emailtemplate.objects().first()
    for s in stu:
        reciever = s.userId # use the aggreatatory function to get the email 
        subject = temail.subject
        message = "Dear " + s.firstName +',' + '\n'+ temail.message
        print(reciever)
        print(message)
    # write code to check for the assessment for all the user and then send them the mail 
    flash("Mail has been Sent to all the students", "success")
    return redirect(url_for('admindash'))


@app.route('/sendmail', methods=['GET','POST'])
def sendmail():  
    recipients = request.form["reciever"]
    recipients = list(recipients.split(","))
    body = request.form["message"]
    subject = request.form["subject"]
    print(recipients)
    print(type(subject))
    print(type(body))

    #subject = 'Mail from flask server'
    #msg = "testing the body message form flask mail "
    #recipients = 'ishdeep.711@gmail.com'
    sender = 'ishdeepsingh@sce.carleton.ca'
    msg = Message(subject=subject, body=body,
                  sender=sender, recipients=recipients)
    mail.send(msg)
    print("Mail has been sent  ")
    ''' adding attachment
    with app.open_resource("image.png") as fp:
        msg.attach("image.png", "image/png", fp.read())
    '''
    
    flash("Mail has been Sent to ", "success")
    return redirect(url_for('admindash'))


@app.route('/emailtemp', methods=['GET', 'POST'])
def emailtemp():
    temail= emailtemplate.objects.first()
    
    sen = request.form["sender"]
    subject = request.form["subject"]
    message = request.form["message"]
    #semail = emailtemplate(sender=sen, subject=subject, message=message)
    
    temail.sender=sen
    temail.subject=subject
    temail.message=message
    
    temail.save()
    
    flash("Email Template has been saved ", "success")
    return redirect(url_for('admindash'))
