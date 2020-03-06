from flask import Flask
from config import Config
from flask_mongoengine import MongoEngine
from flask_admin import Admin
from flask_admin.contrib.pymongo import ModelView
from flask_restplus import Api



app=Flask(__name__)

app.config.from_object(Config)

# admin setting
admin = Admin(app)

#admin.add_view(ModelView(User,db.session))
    # adding admin to the view

# adding the API for the application
api=Api()
api.init_app(app)



app.run()
# database settings
try :
    db = MongoEngine()
    print("Connected to database successfully")
except:
    print("unable to connect to database")

db.init_app(app)

#admin.add_view(ModelView(User,db.session))

# Initializing flask mail server
#mail = Mail(app)

from sapp import routes
