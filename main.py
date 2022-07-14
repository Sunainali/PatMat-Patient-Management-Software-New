from email import message
from functools import wraps
from flask_login import login_required, login_user, LoginManager, logout_user, current_user

from flask import Flask, request, render_template, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime as dt


db_loc = "sqlite:///data.db"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = db_loc
app.secret_key = 'HYTURIWODH'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    admin = db.Column(db.Boolean, nullable=False)
    status = db.Column(db.Boolean, nullable=False)

    def to_json(self):
        return {
            "name": self.name,
            "email": self.email
        }

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def is_admin(self):
        return self.admin

class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicine.id'))
    patint_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    time = db.Column(db.String, nullable=False)
    dosage = db.Column(db.String, nullable=False)

class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    pres = db.relationship(Prescription, backref='medicine')

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(30), nullable=False)
    lastname = db.Column(db.String(30), nullable=False)
    gender = db.Column(db.String(1), nullable=False)
    dob = db.Column(db.DateTime, nullable=False)
    joiningdate = db.Column(db.DateTime, nullable=False)
    prescriptions = db.relationship(Prescription, backref='patient')

    def __str__(self):
        return f"Patient {self.id}: {self.firstname} {self.lastname}"


def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            if current_user.is_admin():
                return fn(*args, **kwargs)
            else:
                return jsonify(msg="Admins only!"), 403

        return decorator

    return wrapper


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()

@app.route('/')
def main():
    if current_user.is_authenticated:
        return redirect('/home')
        
    return redirect('/login')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            message = "An account already exists with that email address."
        else:
            user = User(
                name = username,
                password = password,
                email = email,
                admin = False,
                status = False
            )

            db.session.add(user)
            db.session.commit()

            message = 'Request sent for approval'

        return render_template(
            'login.html',
            message=message,
        )

@app.route('/login', methods=['POST', 'GET'])
def login():
    message=''
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(
            email=email,
            password=password,
            admin=False,
        ).first()

        if user:
            if user.status:
                login_user(user)
                return redirect('/home')
            else:
                message = "Your request is waiting approval"

        else:
            message='Incorrect Username or Password'

    if current_user.is_authenticated:
        return redirect('/')
    
    return render_template(
        "login.html",
        message=message
    )

@app.route('/logout')
@login_required
def logout():
    logout_user()

    return redirect('/login')


@app.route('/home')
@login_required
def home():
    return render_template(
        'index.html',
        curr_user=current_user
    )

@app.route('/medicine')
@login_required
def medicine():
    all_medicines = Medicine.query.all()
    return render_template(
        'medicine.html',
        medicines = all_medicines,
    )

@app.route('/patients')
@login_required
def patients():
    all_patients = Patient.query.all()
    return render_template(
        'patients.html',
        patients = all_patients,
    )

@app.route('/add-medicine', methods=['POST'])
@login_required
def add_medicine():
    if request.method == 'POST':
        name = request.form.get('med')
        
        m = Medicine()
        m.name = name

        db.session.add(m)
        db.session.commit()

    return redirect('/medicine')

@app.route('/delete-medicine/<int:mid>')
@login_required
def delete_medicine(mid):
    med = Medicine.query.filter_by(id = mid).one()
    
    db.session.delete(med)
    db.session.commit()

    return redirect('/medicine')

@app.route('/add-patient', methods=['POST'])
@login_required
def add_patient():
    if request.method == 'POST':
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        gender = request.form.get('gender')
        dob = request.form.get('dob')
        joiningdate = request.form.get('joiningdate')

        dob = dt.strptime(dob, '%Y-%m-%d')
        joiningdate = dt.strptime(joiningdate, '%Y-%m-%d')

        patient = Patient()
        patient.firstname = fname
        patient.lastname = lname
        patient.gender = gender
        patient.dob = dob
        patient.joiningdate = joiningdate

        db.session.add(patient)
        db.session.commit()
    
    return redirect('/patients')

@app.route('/show-patient/<int:pid>')
@login_required
def show_patient_info(pid):
    patient = Patient.query.filter_by(id = pid).one()
    all_medicine = Medicine.query.all()

    #print(f"Prescriptions: {patient.prescriptions[0].medicine}")

    return render_template(
        'patient.html',
        patient=patient,
        all_medicine=all_medicine,
    )

@app.route('/update-patient/<int:pid>', methods=['POST', 'GET'])
@login_required
def update_patient(pid):
    patient = Patient.query.filter_by(id = pid).one()

    if request.method == 'POST':
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        gender = request.form.get('gender')
        dob = request.form.get('dob')
        joiningdate = request.form.get('joiningdate')

        dob = dt.strptime(dob, '%Y-%m-%d')
        joiningdate = dt.strptime(joiningdate, '%Y-%m-%d')

        patient = Patient.query.filter_by(id = pid).one()

        patient.firstname = fname
        patient.lastname = lname
        patient.gender = gender
        patient.dob = dob
        patient.joiningdate = joiningdate

        db.session.commit()

        return redirect('/patients')

    
    return render_template(
        'updatepatient.html',
        patient=patient,
    )

@app.route('/delete-patient/<int:pid>')
@login_required
def delete_patient(pid):
    patient = Patient.query.filter_by(id = pid).one()
    
    db.session.delete(patient)
    db.session.commit()

    return redirect('/patients')

@app.route('/prescribe/<int:pid>', methods=['POST'])
@login_required
def prescribe(pid):
    if request.method == 'POST':
        medicine_id = request.form.get('prescribed_med')
        med_time = request.form.get('med_time')
        med_dosage = request.form.get('med_dosage')

        patient = Patient.query.filter_by(id = pid).one()
        medicine = Medicine.query.filter_by(id = medicine_id).one()

        p = Prescription()
        p.medicine = medicine
        p.patient = patient
        p.time = med_time
        p.dosage = med_dosage

        db.session.add(p)
        db.session.commit()
    
    return redirect('/show-patient/' + str(pid))

@app.route('/show-patient/<int:pid>/delete-prescription/<int:prid>')
@login_required
def delete_prescription(pid, prid):
    pres = Prescription.query.filter_by(id = prid).one()
    
    db.session.delete(pres)
    db.session.commit()

    return redirect('/show-patient/' + str(pid))

@app.route('/admin', methods=['POST', 'GET'])
def admin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(
            email=email,
            password=password,
            admin=True,
        ).first()

        if user:
            login_user(user)
            return redirect('/admin/panel')

        else:
            return render_template(
                'admin_login.html',
                error_message='Incorrect Username or Password'
            )

    if current_user.is_authenticated:
        return redirect('/admin/panel')
    
    return render_template(
        "admin_login.html",
        error_message=''
    )

@app.route('/admin/panel')
@login_required
@admin_required()
def admin_panel():
    pending_approvals = User.query.filter_by(status=False).all()

    return render_template(
        'admin_panel.html',
        pending_approvals=pending_approvals,
    )

@app.route('/admin/panel/approve-<int:uid>')
@login_required
@admin_required()
def approve_user(uid):
    user = User.query.get(uid)
    user.status = True
    db.session.commit()

    return redirect('/admin/panel')

@app.route('/admin/panel/reject-<int:uid>')
@login_required
@admin_required()
def reject_user(uid):
    user = User.query.get(uid)
    db.session.delete(user)
    db.session.commit()

    return redirect('/admin/panel')

if __name__ == "__main__":
    #db.drop_all()
    #db.create_all()
    app.run()



