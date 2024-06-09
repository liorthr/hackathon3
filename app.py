from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
import pandas as pd

app = Flask(__name__)

class Patient:
    def __init__(self, name, age, gender, vaccinate):
        self.name = name
        self.age = age
        self.gender = gender
        self.vaccinate = vaccinate

class Doctor:
    def __init__(self, name, speciality, active):
        self.name = name
        self.speciality = speciality
        self.active = active

class Appointment:
    def __init__(self, patient, doctor, date, time):
        self.patient = patient
        self.doctor = doctor
        self.date = date
        self.time = time

class Hospital:
    def __init__(self):
        self.conn = sqlite3.connect('hospital.db', check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS patients (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    age INTEGER,
                    gender TEXT,
                    vaccinate TEXT
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS doctors (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    speciality TEXT,
                    active TEXT
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS appointments (
                    id INTEGER PRIMARY KEY,
                    patient_id INTEGER,
                    doctor_id INTEGER,
                    date TEXT,
                    time TEXT,
                    FOREIGN KEY (patient_id) REFERENCES patients (id),
                    FOREIGN KEY (doctor_id) REFERENCES doctors (id)
                )
            """)

    def add_patient(self, patient):
        with self.conn:
            self.conn.execute("""
                INSERT INTO patients (name, age, gender, vaccinate) VALUES (?, ?, ?, ?)
            """, (patient.name, patient.age, patient.gender, patient.vaccinate))

    def add_doctor(self, doctor):
        with self.conn:
            self.conn.execute("""
                INSERT INTO doctors (name, speciality, active) VALUES (?, ?, ?)
            """, (doctor.name, doctor.speciality, doctor.active))

    def schedule_appointment(self, patient_id, doctor_id, date, time):
        with self.conn:
            self.conn.execute("""
                INSERT INTO appointments (patient_id, doctor_id, date, time) VALUES (?, ?, ?, ?)
            """, (patient_id, doctor_id, date, time))

    def view_table(self, table_name):
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql_query(query, self.conn)
        return df

    def export_table_to_csv(self, table_name):
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql_query(query, self.conn)
        file_name = f"{table_name}.csv"
        df.to_csv(file_name, index=False)
        return file_name

hospital = Hospital()

@app.route('/')
def menu():
    return render_template('menu.html')

@app.route('/patient', methods=['GET', 'POST'])
def patient():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        vaccinate = request.form['vaccinate']
        new_patient = Patient(name, age, gender, vaccinate)
        hospital.add_patient(new_patient)
        return redirect(url_for('menu'))
    return render_template('patient.html')


@app.route('/doctor', methods=['GET', 'POST'])
def doctor():
    if request.method == 'POST':
        name = request.form['name']
        speciality = request.form['speciality']
        active = 'Yes' if 'active' in request.form else 'No'
        new_doctor = Doctor(name, speciality, active)
        hospital.add_doctor(new_doctor)
        return redirect(url_for('menu'))
    return render_template('doctor.html')


@app.route('/appointment', methods=['GET', 'POST'])
def appointment():
    if request.method == 'POST':
        patient_id = request.form['patient_id']
        doctor_id = request.form['doctor_id']
        date = request.form['date']
        time = request.form['time']
        hospital.schedule_appointment(patient_id, doctor_id, date, time)
        return redirect(url_for('menu'))
    return render_template('appointment.html')

@app.route('/view_table/<table_name>')
def view_table(table_name):
    df = hospital.view_table(table_name)
    return render_template('view_table.html', table_name=table_name, data=df)

@app.route('/export_table/<table_name>')
def export_table(table_name):
    file_name = hospital.export_table_to_csv(table_name)
    return send_file(file_name, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
