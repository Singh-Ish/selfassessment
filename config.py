import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or "secret_string"

    #database setting
    MONGODB_SETTINGS= {'db' :'assessment'}

    #admin setting
    FLASK_ADMIN_SWATCH = 'cerlean'


    # file upload settings
    UPLOAD_FOLDER = 'sapp/static/docs'
    #ALLOWED_EXTENSIONS = {'pdf'}

    # Flask-Mail settings
    MAIL_USERNAME = 'email@example.com'
    MAIL_PASSWORD = 'MAIL_PASSWORD'
    MAIL_DEFAULT_SENDER =   '"MyApp" <noreply@example.com>'
    MAIL_SERVER =  'smtp.gmail.com'
    MAIL_PORT =    465
    MAIL_USE_SSL = int(True)
