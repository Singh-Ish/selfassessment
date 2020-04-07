import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or "secret_string"

    # changing the server name 
    #SERVER_NAME = '127:0.0.1:6000'

    #database setting
    MONGODB_SETTINGS= {'db' :'assessment'}

    #admin setting
    FLASK_ADMIN_SWATCH = 'cerlean'


    # file upload settings
    UPLOAD_FOLDER = 'sapp/static/docs'
    #ALLOWED_EXTENSIONS = {'pdf'}

    # Flask-Mail settings
    MAIL_SERVER = 'smtp.sce.carleton.ca'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False

    MAIL_USERNAME = 'ishdeepsingh@sce.carleton.ca'
    MAIL_PASSWORD = 'Change.711'
