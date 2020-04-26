from sapp import app,db,mail,s,urldns
from flask import render_template, request,json,Response, redirect , url_for , session, jsonify, send_file,send_from_directory, url_for
from sapp.models import User, rubics, projects, samatrix, emailtemplate, feedback, faculty, role
from sapp.forms import LoginForm, RegisterForm 
from flask import flash
from werkzeug.utils import secure_filename
import os
import pandas as pd
from flask_restplus import Resource
from flask_mail import Mail, Message
from itsdangerous import URLSafeSerializer , SignatureExpired

#from flask_user import role_required, UserManager, UserMixin
#from flask_mail import Mail

#############################


"""
## api for users ##
@api.route('/api/user','/api/user/')
class getpost(Resource):
    #get all
    def get(self):
        return jsonify(User.objects.all())

    #POST 
    def post(self):
        data=api.payload
        user = User(userId=data['userId'],firstName=data['firstName'],lastName=data['lastName'],email=data['email'],password=data['password'])
        user.save()
        r = role(userId=data['userId'])
        r.save()
        return jsonify(User.objects(userId=data['userId']))


    #put

@api.route('/api/user/<idx>')
class user_update_delete(Resource):
    # get data request
    def get(self, idx):
        return jsonify(User.objects(userId=idx))

    #Put 
    def put(self,idx):
        data = api.payload
        User.objects(userId=idx).update(**data)
        return jsonify(User.objects(userId=idx))

    # delete data  reqest
    def delete(self, idx):
        User.objects(userId=idx).delete()
        role.objects(userId=idx).delete()
        return jsonify("User "+idx+" is deleted")

#############################
"""

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
        flash("you are already logged in ", "success")
        return redirect(url_for('home'))

    '''
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
    '''

    if request.method == 'POST':
        email = request.form['email']
        
        if not User.objects(email=email):
            flash(f"you have don't have access to the portal. Kindly contact the admin staff","danger")
            return redirect(url_for('home'))

        print(email)
        token = s.dumps(email, salt='emailsession')

        msg = Message('confirm Email token login',sender='ishdeepsingh@sce.carleton.ca', recipients=[email])

        # link to the token 
        link = url_for('confirm_mail', token=token, _external=True)
        print(link)
        externallink = (urldns + link)
        #print(externallink)
        
        msg.body = ' \n Hi your login link is \n \n {}'.format(externallink)
        #mail.send(msg)
        flash(f"An Email has been sent with authorization token to {email} please verify to login", "success")
        return redirect(url_for("login"))
    
    if not role.objects(rname="admin").first():
        u = User(userId=1,firstName="Ish",lastName="singh",email="ishdeepsingh@sce.carleton.ca")
        u.save() 
        ro = role(userId=1,rname="admin")
        ro.save()
        
    return render_template("auth/login.html", title="Login", login=True )


@app.route('/confirm_mail/<token>')
def confirm_mail(token):
    try:
        email = s.loads(token, salt='emailsession', max_age=600) # token will be valid for 10 minutes 

        user = User.objects(email=email).first()
        
        if user:
            
            session['userId'] = user.userId
            session['username'] = user.firstName

            r = role.objects(userId=user.userId).first()
            session['role'] = r.rname
            if(r.rname == 'admin'):
                flash(
                    f"{user.firstName}, you are successfully logged in and have admin priveledges!", "success")
                return redirect(url_for("admindash"))

            flash(f"{user.firstName}, you are successfully logged in!", "success")
            return redirect(url_for("sdash"))
        else:
            flash("you are Not a valid user. please contact the faculty or department Admin","danger")
            return redirect(url_for("home"))
        

    except SignatureExpired:
        flash("the token has expired. Please try to login again","danger")
        return redirect(url_for("login"))

'''
    # check the access role of the user map it to student details and create the route according to that 
    user = User.objects(email=email).first()
       if user and password == user.password:
            flash(f"{user.firstName}, you are successfully logged in!", "success")
            session['userId'] = user.userId
            session['username'] = user.firstName

            r = role.objects(userId=user.userId).first()
            session['role'] = r.rname
            if(r.rname == 'admin'):
                return redirect("admindash")

            # implement various routes depemnding on the security roles
            return redirect("/sdash")
        else:
            flash("Sorry, Invalid login Information ", "danger")
    return "the token works and the email is {}".format(email)


@app.route("/register",methods=['GET','POST']) # once register it should go to the admin to approve and connect the supervisor to the project
def register():
    if session.get('username'):
        flash("you are already registered in ","success")
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
        if  User.objects(userId=userId).first() or User.objects(email=email).first():
            flash("user Id  already exist")
            return redirect(url_for('register'))

        # adding the user to the database 
        user=User(userId=userId, email=email, firstName=firstName, lastName=lastName, password=password  )
        #user.set_password(password)
        user.save()

        # assigning  the deafult role to the user as student 
        r = role(userId=userId)
        r.save()

        session['userId'] = user.userId
        session['username'] = user.firstName


        
        r = role.objects(userId=user.userId).first()
        session['role'] = r.rname
        
        flash("you are successfully registeres!", "success")
        return redirect("sdash")
         
    return render_template("auth/register.html", title="Register", form=form, register=True )
'''

@app.route("/logout")
def logout():
    session['userId']=False
    session.pop('username',None)
    session.pop('role',None)
    return redirect(url_for('home'))

#####################################################
# dashboard routes
@app.route("/sdash/")
def sdash():
    if not session.get('username'):
        flash(f"you are not currently logged in. Kindly login to proceed","danger")
        return redirect(url_for('login'))
    userId= session.get('userId')
    # if no group number just move to home 
    if not projects.objects(userId=userId).first():
        flash("you are successfully logged in! but you don't belong to any group", "danger")
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

    user = User.objects(userId=userId).first() # checking if used has admin rights or not 
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
        
        try:
            samatrix.eval()
            print("evaluated the assessment and saved in the file ")
        except:
            print("can't evaulate the matrix ")

        return redirect(url_for('sdash'))
    return render_template("other/fsa.html")


#############################
# upload the rubics excel file to the database
@app.route('/uploader', methods=['GET','POST']) # rubics  Uploader 
def uploader():
    if request.method =='POST':
        if (session['role'] == 'admin'):
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
            #print(os.path.join(app.config['UPLOAD_FOLDER'], sf))
            f.save(os.path.join(app.config['UPLOAD_FOLDER'],sf))
            flash("uploaded file successfully","success")
            try:
                rubics.uploadnew()        # update the rubics data in the database
                flash("successfully saved the rubics cube details to the database", "success")
            except:
                flash("can't update save the rubics cube details to the database","danger")

            return redirect(url_for('admindash'))
        else:
            flash("You don't have admin privledges to upload")


@app.route('/pupload', methods=['GET', 'POST']) # project uploader 
def pupload():
    if request.method == 'POST':
       
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part', "danger")
            return redirect(url_for('admindash'))

        f = request.files['file']
        print(f.filename)
            # if user does not select file , browser also submit an empty part filename
        if f.filename == '':
            flash('No Project File selected for upload', "danger")
            return redirect(url_for('admindash'))

        if f.filename != 'projectDetails.xlsx':
            flash('please upload the correct project details file with the same name and format', "danger")
            return redirect(url_for('admindash'))

        sf = secure_filename(f.filename)
        #print(os.path.join(app.config['UPLOAD_FOLDER'], sf))
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], sf))
        
        
        try:
            projects.pupload()       # update the project data in the database fucntion in models
            flash("successfully saved the Project details to the database", "success")
        except:
            flash("can't update save the Project details to the database","danger")
        
        return redirect(url_for('admindash'))


@app.route('/uupload', methods=['GET', 'POST'])  # project uploader
def uupload():
    if request.method == 'POST':

        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part', "danger")
            return redirect(url_for('admindash'))

        f = request.files['file']
        
        # if user does not select file , browser also submit an empty part filename
        if f.filename == '':
            flash('No User File selected to upload', "danger")
            return redirect(url_for('admindash'))

        if f.filename != 'userDetails.xlsx':
            flash('please upload the correct user details file with the same name and format', "danger")
            return redirect(url_for('admindash'))
        print(f.filename)
        sf = secure_filename(f.filename)
        #print(os.path.join(app.config['UPLOAD_FOLDER'], sf))
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], sf))

        #User.userUpload()
        
        try:
            User.userUpload()      # update the User data in the database fucntion in models
            flash("successfully saved the User details to the database", "success")
        except:
            flash("can't update  the User details to the database", "danger")
        
        return redirect(url_for('admindash'))


@app.route('/fdupload', methods=['GET', 'POST'])  # project uploader
def fdupload():
    if request.method == 'POST':

        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part', "danger")
            return redirect(url_for('admindash'))

        f = request.files['file']

        # if user does not select file , browser also submit an empty part filename
        if f.filename == '':
            flash('No faculty File selected to upload', "danger")
            return redirect(url_for('admindash'))

        if f.filename != 'facultyDetails.xlsx':
            flash(
                'please upload the correct faculty details file with the same name and format', "danger")
            return redirect(url_for('admindash'))
        print(f.filename)
        sf = secure_filename(f.filename)
        #print(os.path.join(app.config['UPLOAD_FOLDER'], sf))
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], sf))

        #faculty.newf()
        try:
            faculty.newf()      # update the User data in the database fucntion in models
            flash("successfully saved the User details to the database", "success")
        except:
            flash("can't update  the faculty details to the database", "danger")
        
        

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
    print("Clicked  userId is ",id)
    s = User.objects(userId=id).first()
    print(s.email)
    temail = emailtemplate.objects().first()
    return render_template("email.html", s=s, temail=temail)


@app.route('/emailall', methods=['GET', 'POST'])
def emailall():

    stu = list(projects.objects(assessmentStatus=0).aggregate(*[
        {
            '$lookup': {
                'from': 'user',
                'localField': 'userId',
                'foreignField': 'userId',
                'as': 'userdata'
            }
        }, {
            '$unwind': {
                'path': '$userdata'
            }
        }
    ]))

    


    temail = emailtemplate.objects().first()
    for s in stu:
        s = dict(s)
        
        recipients = s['userdata']['email']
        # use the aggreatatory function to get the email
        recipients = list(recipients.split(","))
        subject = temail.subject
        link = url_for('home')
        link = urldns + link
        body = ("Dear " + s['firstName'] +',' + '\n'+ temail.message +'\n \n' + "Access the self assessment portal {}".format(link))
        sender = temail.sender
        msg = Message(sender=sender, subject=subject, body=body, recipients=recipients)
        mail.send(msg)
    # write code to check for the assessment for all the user and then send them the mail 
    flash("Mail has been Sent to all the students", "success")
    return redirect(url_for('admindash'))


@app.route('/sendmail', methods=['GET','POST'])
def sendmail():  
    rec = request.form["reciever"]
    recipients = list(rec.split(","))
    link = url_for('home')
    link = urldns + link
    body = (request.form["message"]+'\n \n' +
            "Access the self assessment portal {}".format(link))
    subject = request.form["subject"]
    temail = emailtemplate.objects().first()

    
    sender = temail.sender
    msg = Message(subject=subject, body=body,
                  sender=sender, recipients=recipients)
    mail.send(msg)
    
    ''' 
    #adding attachment
    with app.open_resource("image.png") as fp:
        msg.attach("image.png", "image/png", fp.read())
    '''
    
    flash(f"Mail has been Sent to {rec}", "success")
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


@app.route('/emailself', methods=['GET', 'POST'])
def emailself():
    id = session.get('userId')

    cuser = User.objects(userId=id).first()
    recipients = [cuser.email]
    #recipients = ['ishdeep.711@gmail.com']
    print(recipients)
    body = " Hi  \n Please find attached the Self assessment results, excel sheet. \n Regards  "
    subject = " Self assesment results"
    
    msg = Message(subject=subject, body=body, recipients=recipients)

    filename = "assessmentresult.xlsx"
    filepath=os.path.join(os.getcwd(), filename)

    with app.open_resource(filepath) as fp:
        msg.attach("assessmentresult.xlsx", "application/xlsx", fp.read())
    
    
    try:
        mail.send(msg)
        flash(f"The Email has been sent and the result has been send as an attachement to {cuser.email} ", "success")
    except:
        flash("Can't send mail, contact your administrator ", "danger")

    
    return redirect(url_for('admindash'))


########### eval 

    


@app.route('/download', methods=['GET', 'POST'])
def download():
    print(" hello from download ")
    filename = "assessmentresult.xlsx"
    try: 
        return send_file(os.path.join(os.getcwd(), filename), as_attachment=True)

    except:
        flash("can't downlaod the file please contact the developer","danger")
        return redirect(url_for('admindash'))




    
