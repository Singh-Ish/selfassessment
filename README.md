# Self Assessment Portal 

[Department of System and Computer Engineering, 
Carleton Univeristy](https://carleton.ca/sce/)


# SA Portal 

Self Assessment portal is to get Student's Assessment about themself and other team members based on the defined rubrics metrix. 


# Features 
    - Student Dashboard 
    - Admin Dashboard
    - Dynamic project, rubics and user update option 
    - Currently for one paticular course or project based Assessment
    
Other Features 
- Email token based authentication 
- Intuitive admin dashbaord 
- Inbuild Reminder system 

## Tech

SA Portal  uses a number of open source projects to work properly:


* [markdown-it] - Markdown parser done right. Fast and easy to extend.
* [Bootstrap] - great UI boilerplate for modern web apps
* [python- Flask] - evented I/O for the backend
* [jQuery] - Javascript
* [Mongo DB ] - No SQl Database for storing the data 


## Installation
The Installation Enviernment is easy to install 

#### 1. Clone the source code to the local machine 

```sh
$ mkdir Saportal 
$ git clone https://github.com/Singh-Ish/selfassessment.git
$ cd selfassessment
```
#### 2. Installing dependencies and environment, Make sure you have python3, MongoDB Installed on the machine. 

- Installing pip and virtual environment 
```sh
$ python3 get-pip.py
$ pip install virtualenv
$ virtualenv env  ; Note env is the environment name 
```

- Activating the virtual Environment

```sh
$ \env\Scripts\activate.bat
```

- Installing the project dependent packages 

```sh
$ pip install -r requirement.txt
```

- Update the Configuration File with the credentials 


### 3. Running Application  
we have already configured .flaskenv to run main.py when using "flask run" command.

```sh
$ flask run
```
Output will be like this. You can also change the host and port details by simply using " Flask run --host 0.0.0.0 --port 3000" 
```sh
 * Serving Flask app "main.py" (lazy loading)
 * Environment: development
 * Debug mode: on
 * Restarting with stat
Connected to database successfully
 * Debugger is active!
 * Debugger PIN: 247-067-783
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
Connected to database successfully
```

Verify the deployment by navigating to your server address in your preferred browser.
```sh
http://127.0.0.1:5000/ 
```

### 4. Run and Configure MongoDb Database

Make sure local instance of MongoDB is up and running.

The "Flask run" command will create database collections automatically, 

Database Name : assessment

It will have below Collections Database schema Overview 

- User : have the details about the user that have access to the portal
- Project : project or course that the students are in group together 
- role : Role of the user weather a is a student or admin ; Access level
- rubics : evaluating matrix 
- samatrix : student response collection
- emailtemplate : default reminder template
- faculty : faculty details 
- feedback : user feedback about the portal or about the course 

Re-run step 3 




# running the code in production on red hat server 
webserver: Nginx 
python webserver: Supervisor and gunicorn 

## server restart 

check the status 
'''sh 
$sudo systemctl status nginix
< needs to be active > 

$sudo systemctl status supervisord 
< need to be active > 

'''



# Code Architecture Design Explanation  
Its an open source projet and for the ease providing the details code description for better collaboration.

- Requirement.txt contains list of all the packages need to be preinstalled into the system before running the application 

- main.py is the starting point of the application. It imports the actual app sapp to the applicaiton.

- Config.py, contains the Configuration setting of the applicaiton like the 
    - Database setting 
    - Upload Folder settings 
    - Email configuration 


- Sapp folder contains all the files related code to the development of the applicaiton 
    - Static Folder
         - Css , external css file for styling the html  
        - Docs, all the uploaded documents are stored and read from this folder. location can be changed in config 
        - Images, contains the images like the logo etc
        - Sample Docs, Contains a sample document which are allowed to upload on the portal. 
    
    - Templates Folder 
    - (__init__.py) file, contains all the basic instance creation whenever the sapp folder is imported 
    - forms.py, Optional creating the wtf forms for registeration or login etc 
    - models.py , Database schema 
    -routes.py, defines the url routes for application, this also import the data from database 

### Use case 
The Canadian Engineering Accreditation Board requires graduates of engineering programs to possess 12 attributes at the time of graduation. You have been asked to complete a self –assessment of yourself and your group for Graduate Attribute 6: Individual and team work related to your 4th Year Capstone Project . Graduate Attribute 6 represents a student’s ability to work effectively as a member and leader in teams, preferably in a multi-disciplinary setting. Graduate attribute measurements will not be taken into consideration in determining a student’s grade in the course.


# Coming Soon New Features!
- Self Assessment for Multiple courses
- Scheduled reminder system 





License
----

GNU General Public License v3.0


**Free Software, Hell Yeah!**


   [git-repo-url]: <https://github.com/Singh-Ish/selfassessment.git>



 
