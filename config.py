# ==== Configuration file ====


import os

class Config(object):

    """
    Config class defines the deafult configuration for the applicaiton 
    - Database
    - Flask-Admin
    - Upload Folder 
    - Email Configuration  

    """

    SECRET_KEY = os.environ.get('SECRET_KEY') or "secret_string"

    # changing the server name 
    #SERVER_NAME = '127:0.0.1:6000'

    #database setting
    MONGODB_SETTINGS= {'db' :'assessment'}

    #admin setting
    FLASK_ADMIN_SWATCH = 'cerlean'

    #changing the server name 
    #SERVER_NAME='saportal.sce.carleton.ca'

    # file upload settings
    UPLOAD_FOLDER = 'sapp/static/docs'
    #ALLOWED_EXTENSIONS = {'pdf'}

    # Flask-Mail settings
    MAIL_SERVER = 'smtp.sce.carleton.ca'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_ASCII_ATTACHMENTS = False
    MAIL_USERNAME = 'ishdeepsingh@sce.carleton.ca'
    MAIL_PASSWORD = 'Change.711'
    MAIL_DEFAULT_SENDER = ('Self-Assessment Portal',
                           'saportal@sce.carleton.ca')
