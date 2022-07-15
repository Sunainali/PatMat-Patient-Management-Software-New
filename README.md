# PatMat-Patient-Management-Software-New
This project has been developed by Osborne, Bobby and Sunain. Front-end part has developed by Osborne and bobby they have worked both together and  Sunain have made database and developed backend.

We have used only one device (LAPTOP) as a hardware components. 
As Software components, we have used Visual Studio Code as an IDE and the complete program is written on HTML as a main basic language and CSS for its styling and we have chosen Python as main langaguge for backend and MySQL for database queries.

INSTRUCTIONS:
Step 1:
Unzip all the files in any folder and run it
Step 2: 
Open the folder/file in Visual Studio or anyother IDE.
Step 3:
Write python main.py in the terminal and run it.
Step 4:
Open the browser, and write localhost:5000.
Step 5:
Try to signup with your details requierd.
Step 6:
Then go back, Signup as admin either to approve or reject the request for signup. 
Admin Credentials are:
Email: admin@admin.com
Pass: admin
Step 7:
Login with the credentials entered in step 5, you will be redirected to the main Welcome Page of PaTMat.
Step 8:
If you click on Patients' Link, you will be able to enter new patients and/or manage the existings one. 
Step 9:
If you click Medicine Link, you will be able to enter new medicine to the PHARMACY and you will also be able to manage the existing one (for example to delete).


Programming FRONT-END Explanation:
In admin file:
In a head section, we have given a title to admin page and connected it the CSS file for login.
In body Section, added a form with button that allows you to signin as an admin with predefined credentails.
Afterwards in admin panel, a new table was added with UID, NAME and EMAIL  and two links either for approval or rejection of any specific user.

In login file:
In head section, after title styling link for CSS is linked and JS query is applied for a bit of animation while turning from admin to login page or vice-versa.
Same as Admin page, a complete data form is added but along some message if someone is not registered ? SIGNUP will be redirected to that specifice page. 
And if you are an admin click on LOGIN as an Admin.

In main index/Welcome file:
Styling is done in a head section and in body section after in a heading part a query is added his/her name will be displayed according to the signup name as given and two main links are provided one for the Patients' management and one for the Pharmacy.

In Patients Link:
Styling is also done in head section, and a form is added to let the user to enter details and below that a table is added which shows the patients addded, with python/html quries and a user will be able to See the details of the patient, update or delete them.


In PATIENT file:
Styling is done in a head file, and a python/html query is written that shows the details of the person entered.
A new div is added for medicines, a form with option(dropdown) for medicine to choose from two inputs and one button is added to enter the details an dthose will be shown below in the table same as for patients' file.

In Medicine file:
After heading, same as above a form is added with post method and tables are given below to show the respective added medicine with particular Medicine ids.

Programming Backend and Database Explanantion:

Database queries:
Created a table for login with username of VARCHAR limit of 20  and same as with password VARCHAR of 20.
Created another table with patient ID as a primary key and other details repectively. 
Another table is created for medicine, MID as a primary key for this table.
Last table was added in DATABASE queries for prescripition, in which pid and mid are set as froeign key to assign specific medicines to specific patients with their respective ids.

In main.py file:
In VS Code Imported a flask and SQLAlchemy for database.
db_loc = "sqlite:///data.db" database file in linked with the main file.
4 classes were defined linked with the databse for users, Patient, medicine and prescription.
Nex, a function is defined for the admin, when admin login with right credentials it authenticates else ERORR 403 and message only admins. if else statement is subjected in this case. 
Another fuction is defined for signup as for POST and GET. get the data on the signup page and IF existing user "User.query.filter_by(email=email).first()"
Message will be displayed "An account already exists with that email address." ELSE the user will be able to continue to signup but will be unable to signup as an admin. because admin and status are defined as False. Same as for Login If ELSE statement is applied if the user.status is not yet approved by admin then the message will be appeared = "Your request is waiting approval" if rejected 'Incorrect Username or Password'.
At the main page, a function is defined for logout " def logout(): logout_user() " and will redirected to login page.
Two functions are called one for medicines and one d=for patients both the defined function classes and queries are same to call either all the medicines or all the patients on respective HTML pages. 
A new function is defined to add the mdeicines with form.get method to add the medicine in the database and same is for delete to delete any specific medicine. 
Same is for patients, another function is called to add the patients with .get format. only in date input fields, this format is pre-defined ('%Y-%m-%d'). 
In show  patient page, def show_patient_info(pid): this function is defined to show specific patient's data according to PID and all the medicines prescribed. 
delete button is defined with this function 
    delete_patient(pid):
    patient = Patient.query.filter_by(id = pid).one()
    db.session.delete(patient)
    db.session.commit(). 
    
Afterwards, Prescription function is called to add the specific medicines to the table added. 
def prescribe(pid):
    if request.method == 'POST':
        medicine_id = request.form.get('prescribed_med')
        med_time = request.form.get('med_time')
        med_dosage = request.form.get('med_dosage')

        patient = Patient.query.filter_by(id = pid).one()
        medicine = Medicine.query.filter_by(id = medicine_id).one()
 you can also delete any medicine from the suggested medicine table with the function given below:
    def delete_prescription(pid, prid):
    pres = Prescription.query.filter_by(id = prid).one()
    
    db.session.delete(pres)
    db.session.commit()

    return redirect('/show-patient/' + str(pid))

Now comes the main admin panel area, 
This function is called for the admin:

def admin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(
            email=email,
            password=password,
            admin=True,
        ).first()

if the user not an admin will try to login into admin area the below function will be called:
 if user:
            login_user(user)
            return redirect('/admin/panel')

        else:
            return render_template(
                'admin_login.html',
                error_message='Incorrect Username or Password'
            )
            
 If the main admin will login below function will be called:
 
 if current_user.is_authenticated:
        return redirect('/admin/panel')
    
    return render_template(
        "admin_login.html",
        error_message=''
    )

After logging into admin page, the below function will be called if there would be any approvals pending:

def admin_panel():
    pending_approvals = User.query.filter_by(status=False).all()

    return render_template(
        'admin_panel.html',
        pending_approvals=pending_approvals,
    )

if the admin wants to approve the permission for the signup user the below function will be called:
def approve_user(uid):
    user = User.query.get(uid)
    user.status = True
    db.session.commit()

    return redirect('/admin/panel')
    
if admins wants to rejects the permission the below function will be called:
def reject_user(uid):
    user = User.query.get(uid)
    db.session.delete(user)
    db.session.commit()

    return redirect('/admin/panel').
 
 
It's all about our front/backend programming explained.


