import flask
from sapp import db
from werkzeug.security import generate_password_hash, check_password_hash
from sapp import admin
import pandas as pd
import os

# database  schema  are described here
class User(db.Document):
    # user authentication information 
    userId = db.IntField(unique=True) # same as student id
    email = db.StringField( max_length=30, unique=True)
    password = db.StringField()

    # user information 
    firstName = db.StringField( max_length=50)
    lastName = db.StringField( max_length=50)

    #roles = db.relationship('Role',secondary='user_roles', backref = db.backref('users,lazy='dynamic'))

    def set_password(self,password):
        self.password = generate_password_hash(password)

    def get_password(self,password):
        return check_password_hash(self.password, password)

class Role(db.Document):
    #id=db.Integer(unique=True)
    name = db.StringField(max_length=50)



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
        try: 

            pf = pd.read_excel('sapp/static/docs/projectDetails.xlsx')
            pf = pf.fillna(method='ffill')
            pf.groupNo = pf.groupNo.astype(int)
            pf.userId = pf.userId.astype(int)
            pf.assessmentStatus = pf.assessmentStatus.astype(int)
            pf.coSupervisor = pf.coSupervisor.astype(object)
            print(pf.dtypes)
            # removing the duplication enteries and creating a new dataframe df
            pf = pf.drop_duplicates()
        
            print(pf.columns)
            pf.reset_index(inplace=False)
            pf = pf.to_dict("records")
            print(pf)

            for p in pf:
                groupNo = p['groupNo']
                title = p['title']
                supervisor = p['supervisor']
                coSupervisor = p['coSupervisor']
                userId = p['userId']
                lastName = p['lastName']
                firstName = p['firstName']
                assessmentStatus = p['assessmentStatus']
                try:
                    s = projects(groupNo=groupNo, title=title, supervisor=supervisor, userId=userId,
                             lastName=lastName, firstName=firstName, assessmentStatus=assessmentStatus)
                    s.save()
                    print("uploaded the new projects data to the database")
                except:
                    print("can't save the project dat to the database")
        except:
            print(" can't read the project data file ")


######## sa Matrix
class samatrix(db.Document):
    sid = db.IntField()
    fsid = db.IntField()
    fsname = db.StringField()
    Indicator = db.StringField()
    value = db.IntField()



class emailtemplate(db.Document):
    #userId = db.IntField(unique=True, required=True) in future there will be multiple admins so multiple templates
    sender = db.StringField()
    subject = db.StringField()
    message = db.StringField()

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
        #data = faculty.objects()
        #data.delete()
        #db.DeleteMany({})
        ru = pd.read_excel('sapp/static/docs/SCEfaculty.xlsx')
        ru.reset_index(inplace=False)
        rub = ru.to_dict("records")

        print(rub)
        
        for r in rub:
            lastName = r['lastName']
            firstName = r['firstName']
            email = r['email']
            s = faculty(lastName=lastName,firstName=firstName,email=email)
            s.save()
            print("uploaded the new faculty data to the database")
        

#######role based authentication 
class role(db.Document):
    userId = db.IntField(unique=True)
    rname = db.StringField(max_length=30, default='student')

