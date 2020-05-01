import flask
from sapp import db 
#from werkzeug.security import generate_password_hash, check_password_hash
from sapp import admin
import pandas as pd
import os
from flask import flash,json

# database  schema  are described here
class User(db.Document):
    # user authentication information 
    userId = db.IntField(unique=True) # same as student id
    email = db.StringField( max_length=50, unique=True)
    firstName = db.StringField(max_length=50)
    lastName = db.StringField(max_length=50)
    
    def userUpload():
        # check if the role is student or admin 
        print("hello from the user upload function ")
        
        ro = role.objects()
        #data = User.objects()
        
        # resetting the access for students 
        
    
        for r in ro:
            if (r.rname == 'student'):
                data = User.objects(userId=r.userId)
                r.delete()
                data.delete()
        
        print("reading the excel file ")
        # adding the user details to the database 
        ur = pd.read_excel('sapp/static/docs/userDetails.xlsx')
        ur.reset_index(inplace=False)
        usr = ur.to_dict("records")
        print(usr)

        #flash("can't read the file headers", "danger")

        for u in usr:
            
            userId = u['userId']
            firstName = u['firstName']
            lastName = u['lastName']
            email = u['email']
            
                
            s = User(userId=userId,firstName=firstName,lastName=lastName,email=email)
            s.save()

            ro = role(userId=userId)
            ro.save()
            #print("uploaded the new user {} to the database".format(userId))

        print("added the users to the database")    
    
    '''
    password = db.StringField()

    # user information 
    firstName = db.StringField( max_length=50)
    lastName = db.StringField( max_length=50)

    roles = db.relationship('Role',secondary='user_roles', backref = db.backref('users,lazy='dynamic'))

    def set_password(self,password):
        self.password = generate_password_hash(password)

    def get_password(self,password):
        return check_password_hash(self.password, password)

    '''


class rubics(db.Document):
    Indicator = db.StringField()
    Beginning = db.StringField()
    Developing = db.StringField()
    Accomplished = db.StringField()
    Exemplary = db.StringField()

    def uploadnew():
        #deleting all the previous data
        data = rubics.objects()
        data.delete()
        #db.DeleteMany({})
        ru = pd.read_excel('sapp/static/docs/rubicsMetrix.xlsx')
        ru.reset_index(inplace=False)
        rub = ru.to_dict("records")

        for r in rub:
            #print(r['Indicator'])
            Indicator = r['Indicator']
            Beginning = r['Level 1: Beginning']
            Developing = r['Level 2: Developing']
            Accomplished = r['Level 3: Accomplished']
            Exemplary = r['Level 4: Exemplary']
            s = rubics(Indicator=Indicator,Beginning=Beginning,Developing=Developing,Accomplished=Accomplished,Exemplary=Exemplary)
            s.save()
            print("uploaded the new rubics to the database")


class projects(db.Document):
    groupNo = db.IntField()
    title = db.StringField(max_length=200)
    supervisor = db.StringField(max_length=200)
    coSupervisor = db.StringField(max_length=200)
    userId = db.IntField(unique=True , required=True)
    lastName = db.StringField( max_length=50)
    firstName = db.StringField( max_length=50)
    assessmentStatus = db.IntField()

    def pupload():
        
        #deleting all the previous data
        data = projects.objects()
        data.delete()

        # reading the file from the uploaded location 
        pf = pd.read_excel('sapp/static/docs/projectDetails.xlsx')
        pf = pf.fillna(method='ffill')
        pf.groupNo = pf.groupNo.astype(int)
        pf.userId = pf.userId.astype(int)
        pf.assessmentStatus = pf.assessmentStatus.astype(int)
        pf.coSupervisor = pf.coSupervisor.astype(object)
        #print(pf.dtypes)
        # removing the duplication enteries and creating a new dataframe df
        pf = pf.drop_duplicates()
        
        #print(pf.columns)
        pf.reset_index(inplace=False)
        pf = pf.to_dict("records")
        #print(pf)

        for p in pf:
            groupNo = p['groupNo']
            title = p['title']
            supervisor = p['supervisor']
            coSupervisor = str(p['coSupervisor'])
            userId = p['userId']
            lastName = p['lastName']
            firstName = p['firstName']
            assessmentStatus = p['assessmentStatus']
            
            s = projects(groupNo=groupNo, title=title, supervisor=supervisor, coSupervisor=coSupervisor, userId=userId,
                             lastName=lastName, firstName=firstName, assessmentStatus=assessmentStatus)
            s.save()
            print("uploaded the new projects data to the database")
        


######## sa Matrix
class samatrix(db.Document):
    sid = db.IntField()
    fsid = db.IntField()
    fsname = db.StringField()
    Indicator = db.StringField()
    value = db.IntField()

    #### defining a fuction eval


    def eval():
        # doing the export the result first

        pro = projects.objects(assessmentStatus=1)

        # reading all the projects who have filled the assessment
        ru = rubics.objects.all()

        result = []
        for p in pro:
            rin = dict([('userId', p.userId), ('firstName',
                                            p.firstName), ('lastName', p.lastName)])

            for r in ru:
                res = samatrix.objects(fsid=p.userId, Indicator=r.Indicator)
                res = res.to_json()
                res = json.loads(res)
                df = pd.DataFrame(res)

                vavg = df[['value']].mean()
                vavg = int(vavg)
                #print(vavg)
                rinl = dict([(r.Indicator, vavg)])

                rin.update(rinl)

            result.append(rin)

        # adding the projects where students havent given assessment

        pro = projects.objects(assessmentStatus=0)

        # reading all the projects who have filled the assessment
        ru = rubics.objects.all()

        eresult = []
        for p in pro:
            rin = dict([('userId', p.userId), ('firstName',
                                            p.firstName), ('lastName', p.lastName)])

            for r in ru:
                vavg = 'NA'
                #print(vavg)
                rinl = dict([(r.Indicator, vavg)])

                rin.update(rinl)

            eresult.append(rin)

        cresult = result + eresult

        #print(cresult)

        dru = pd.read_excel('sapp/static/docs/rubicsMetrix.xlsx')
        dru = dru.set_index('Indicator')
        dru.to_excel("result.xlsx")


        dfres = pd.DataFrame(cresult)
        dfres = dfres.sort_values(by=['userId'])
        
        dfres['name'] = dfres['firstName'].astype(str) + " " + dfres['lastName'].astype(str) 
        dfres = dfres.drop(columns=['firstName','lastName','userId'])
    
        dfres = dfres[["name", "6.1 Personal and group time management",
                       "6.2 Group culture, group dynamics", "6.3 Leadership: initiative and mentoring, areas of expertise, and interdisciplinary teams"]]
        dfres_t = dfres.set_index('name').transpose()
        
        dfres_t.to_excel("tresult.xlsx")
        res = pd.concat([dru,dfres_t],axis=1,sort=False)
        #print(res)
        filename = 'assessmentresult.xlsx'
        res.to_excel(filename)

        #print(" save the xls file")



class emailtemplate(db.Document):
    #userId = db.IntField(unique=True, required=True) in future there will be multiple admins so multiple templates
    sender = db.StringField(default='ishdeepsingh@sce.carleton.ca')
    subject = db.StringField(default='self assessment portal')
    message = db.StringField(default='please submit your assessment ')

########## students comments and feedback 
class feedback(db.Document):
    userId = db.IntField(unique=True)
    name = db.StringField()
    comment = db.StringField()


####### faculty related data for sending email automatically once all the groups submit the assesment 
class faculty(db.Document):
    lastName = db.StringField(unique=True)
    firstName = db.StringField()
    email = db.StringField(max_length=30, unique=True)

    def newf():
        #deleting all the previous data
        data = faculty.objects()
        data.delete()
        #db.DeleteMany({})
        fu = pd.read_excel('sapp/static/docs/facultyDetails.xlsx')
        fu.reset_index(inplace=False)
        fa = fu.to_dict("records")

        print(fa)
        
        
        for r in fa:
            lastName = r['lastName']
            firstName = r['firstName']
            email = r['email']
            s = faculty(lastName=lastName,firstName=firstName,email=email)
            s.save()
            #print("uploaded the new faculty data to the database")
        

#######role based authentication 
class role(db.Document):
    userId = db.IntField(unique=True)
    rname = db.StringField(max_length=30, default='student')

