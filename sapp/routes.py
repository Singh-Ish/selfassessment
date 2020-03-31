from sapp import app,db,api,mail
from flask import render_template, request,json,Response, redirect , url_for , session, jsonify
from sapp.models import User, rubics, projects, samatrix, emailtemplate, feedback, faculty, role
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
            

            r= role.objects(userId=user.userId).first()
            session['role']=r.rname
            if(r.rname=='admin'):
                return redirect("admindash")

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

        # check if user already exist or not 
        user=User(userId=userId, email=email, firstName=firstName, lastName=lastName )
        user.set_password(password)
        user.save()
        r = role(userId=userId)
        r.save()
        flash("you are successfully registeres!","success")
        return redirect(url_for('admindash'))
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
    # if no group number just move to home 
    if not projects.objects(userId=userId).first():
        flash("you are successfully logged in! but you don't belong to any group", "success")
        return redirect(url_for('home'))
    su = projects.objects(userId=userId).first()
    mgroup = projects.objects(groupNo=su.groupNo)
    return render_template("dash/sdash.html",sdata= su, mgroup=mgroup, sdash=True)


@app.route("/admindash",methods=['GET','POST'])
def admindash():
    userId = session.get('userId')
    if not userId: 
        flash("kindly login to proceed","danger")
        return redirect(url_for('login'))

    r = role.objects(userId=userId).first()

    user = User.objects(userId=userId).first()
    if(r.rname == 'admin'):
        ru=rubics.objects()
        proj = projects.objects.all()
        etemp = emailtemplate.objects().first()
        return render_template("dash/admindash.html",user=user,etemp=etemp,ru =ru, proj=proj, adminDash=True)
    flash("you don't have permission to access this page kingly contact your administrtor", "danger")
    return redirect(url_for('home'))

@app.route("/fdash")
def fdash():
    userId = session.get('userId')
    if not userId:
        flash("kindly login to proceed", "danger")
        return redirect(url_for('login'))

    r = role.objects(userId=userId).first()
    user = User.objects(userId=userId).first()
    print(r.rname)

    if(r.rname == 'admin'):
        ru=rubics.objects()
        proj = projects.objects.all()
        return render_template("dash/fdash.html", user=user, proj=proj, ru=ru,fdash=True)
    flash("you don't have permission to access this page kingly contact your administrtor", "danger")
    return redirect(url_for('home'))

# submitting the student response matrix
@app.route("/saSubmit",methods=['GET','POST'])
def saSubmit():
    userId= session.get('userId')
    name = session['username']

    # initializing the rubics objects
    ru=rubics.objects()

    # retrieving the relevant data from Projects
    su = projects.objects(userId=userId).first()
    mgroup = projects.objects(groupNo=su.groupNo)

    user = projects.objects(userId=userId).first()
    # resetting the data in samatrix for the user
    if  user.assessmentStatus == 0:
        samatrix.objects(sid=userId).delete()

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

        i=0
        sid = userId
        for r in ru:
            ind = r.Indicator
            for g in mgroup:
                fsid = g.userId
                fsname = g.firstName + " " + g.lastName
                user = samatrix.objects(sid=sid,fsid=fsid,Indicator=ind).first()
                user.value = value[i]
    
                user.save()
                #print(user.Indicator)
                #print(fsname)
                #print(ind)
                #print("value" + value[i] )
                i = i+1

       # flash("self assessment resposne has been saved ", "success")
        return redirect(url_for('fsa'))

    return render_template("saSubmit.html",samat = samat,mgroup=mgroup, ru =ru, name = name,  saSubmit=True)




############# route for fsa and changing assessment status
@app.route("/fsa" , methods=['GET', 'POST'])
def fsa():
    ## update the assessment status to 1 
    userId= session.get('userId')  
    su = projects.objects(userId=userId).first()
    if (su.assessmentStatus==0):
        print(" the assessment status is")
        print(su.assessmentStatus)
        su.assessmentStatus=1
        su.save()
    

    # need to save the response form the feedback
    if request.method == 'POST':
        com = request.form['comment']
        userId = session.get('userId')
        uf = feedback.objects(userId=userId).first()
        if uf:
            uf.comment = com
            uf.save()
            print("comment has been updated to the database")
        else: 
            user = projects.objects(userId=userId).first()
            name = user.firstName = " " + user.lastName
            f = feedback(userId=userId, name=name , comment = com)
            f.save()
            print("comment has been saved to the database")
        
        flash("response have been saved!", "success")
        return redirect(url_for('sdash'))
    return render_template("other/fsa.html")


#############################
# upload the rubics excel file to the database
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
    userId = session.get('userId')
    if not userId:
        flash("kindly login to proceed", "danger")
        return redirect(url_for('login'))

    r = role.objects(userId=userId).first()

    if(r.rname == 'admin'):
        users = User.objects.all()
        return render_template("dbview/user.html", users=users)
    flash("you don't have permission to access this page kingly contact your administrtor", "danger")
    return redirect(url_for('home'))
    

@app.route("/project")
def project():
    userId = session.get('userId')
    if not userId:
        flash("kindly login to proceed", "danger")
        return redirect(url_for('login'))

    r = role.objects(userId=userId).first()

    if(r.rname == 'admin'):
        proj = projects.objects.all()
        return render_template("dbview/project.html", proj=proj)

    flash("you don't have permission to access this page kingly contact your administrtor", "danger")
    return redirect(url_for('home'))
    

@app.route("/scomment")
def scomment():
    userId = session.get('userId')
    if not userId:
        flash("kindly login to proceed", "danger")
        return redirect(url_for('login'))

    r = role.objects(userId=userId).first()

    if(r.rname == 'admin'):
        com = feedback.objects.all()
        return render_template("dbview/scomment.html", comm=com)

    flash("you don't have permission to access this page kingly contact your administrtor", "danger")
    return redirect(url_for('home'))
    
    

@app.route("/facultymembers")
def facultymembers():
    #faculty.newf()
    #flash("added new faculty list to database","success")
    userId = session.get('userId')
    if not userId:
        flash("kindly login to proceed", "danger")
        return redirect(url_for('login'))

    r = role.objects(userId=userId).first()

    if(r.rname == 'admin'):
        fac = faculty.objects.all()
        return render_template("dbview/facultyview.html", fac=fac)

    flash("you don't have permission to access this page kingly contact your administrtor", "danger")
    return redirect(url_for('home'))

    

@app.route("/arole")
def arole():
    userId = session.get('userId')
    if not userId:
        flash("kindly login to proceed", "danger")
        return redirect(url_for('login'))

    r = role.objects(userId=userId).first()

    if(r.rname == 'admin'):
        userrole = list(role.objects.aggregate(*[
            {
                '$lookup': {
                    'from': 'user',
                    'localField': 'userId',
                    'foreignField': 'userId',
                    'as': 'user'
                }
            }, {
                '$unwind': {
                    'path': '$user',
                    'preserveNullAndEmptyArrays': False
                }
            }
        ]))

        return render_template("dbview/arole.html", urole=userrole)

    flash("you don't have permission to access this page kingly contact your administrtor", "danger")
    return redirect(url_for('home'))

    

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
