from flask import Flask, render_template, request, session, redirect, url_for
import pickle
import numpy as np
import sqlite3 as sql

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super secret key'

# ---------------------- Home & Info ----------------------
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/aboutus")
def aboutus():
    return render_template("aboutus.html")

# ---------------------- Login Pages ----------------------
@app.route("/adminlogin")
def adminlogin():
    return render_template("adminlogin.html")

@app.route("/userlogin")
def userlogin():
    return render_template("userlogin.html")

@app.route("/patientlogin")
def patientlogin():
    return render_template("patientlogin.html")

# ---------------------- Signup ----------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    msg = None
    if request.method == "POST":
        uname = request.form.get("uname")
        uphone = request.form.get("uphone")
        username = request.form.get("username")
        password = request.form.get("upassword")
        if uname and uphone and username and password:
            try:
                with sql.connect("stroke.db") as con:
                    con.execute("INSERT INTO signup (uname, uphone, username, upassword) VALUES (?, ?, ?, ?)",
                                (uname, uphone, username, password))
                    con.commit()
                    msg = "Your account has been created!"
            except sql.IntegrityError:
                msg = "Username already exists!"
        else:
            msg = "All fields are required."
    return render_template("signup.html", msg=msg)

# ---------------------- Login Actions ----------------------
@app.route('/userloginNext', methods=['POST'])
def userloginNext():
    msg = None
    username = request.form.get('username')
    upassword = request.form.get('upassword')
    with sql.connect("stroke.db") as con:
        c = con.cursor()
        c.execute("SELECT * FROM signup WHERE username = ? AND upassword = ?", (username, upassword))
        if c.fetchone():
            session["logedin"] = True
            session["fusername"] = username
            return redirect(url_for("userhome"))
        else:
            msg = "Please enter valid username and password"
    return render_template("userlogin.html", msg=msg)

@app.route('/patientloginNext', methods=['POST'])
def patientloginNext():
    msg = None
    pusername = request.form.get('pusername')
    ppassword = request.form.get('ppassword')
    with sql.connect("stroke.db") as con:
        c = con.cursor()
        c.execute("SELECT * FROM patient WHERE ausername = ? AND apassword = ?", (pusername, ppassword))
        if c.fetchone():
            session["logedin"] = True
            session["fusername"] = pusername
            return redirect(url_for("patienthome"))
        else:
            msg = "Please enter valid username and password"
    return render_template("patientlogin.html", msg=msg)

@app.route('/adminloginNext', methods=['POST'])
def adminloginNext():
    msg = None
    ausername = request.form.get('ausername')
    apassword = request.form.get('apassword')
    with sql.connect("stroke.db") as con:
        c = con.cursor()
        c.execute("SELECT * FROM adminlogin WHERE ausername = ? AND apassword = ?", (ausername, apassword))
        if c.fetchone():
            session["logedin"] = True
            session["fusername"] = ausername
            return redirect(url_for("adminhome"))
        else:
            msg = "Please enter valid username and password"
    return render_template("adminlogin.html", msg=msg)

# ---------------------- Home Pages ----------------------
@app.route('/userhome')
def userhome():
    if session.get("logedin"):
        return render_template("userhome.html")
    return redirect(url_for("userlogin"))

@app.route('/patienthome')
def patienthome():
    if session.get("logedin"):
        return render_template("patienthome.html")
    return redirect(url_for("patientlogin"))

@app.route('/adminhome')
def adminhome():
    if session.get("logedin"):
        return render_template("adminhome.html")
    return redirect(url_for("adminlogin"))

# ---------------------- Logout ----------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# ---------------------- Appointment ----------------------
@app.route("/bookappointmentNext", methods=["GET", "POST"])
def bookappointmentNext():
    msg = None
    if request.method == "POST":
        pname = request.form.get("pname")
        phone = request.form.get("phone")
        specialist = request.form.get("specialist")
        if pname and phone and specialist:
            with sql.connect("stroke.db") as con:
                con.execute("INSERT INTO appointment VALUES (?, ?, ?)", (pname, phone, specialist))
                con.commit()
                msg = "Appointment booked successfully"
        else:
            msg = "All fields are required."
    return render_template("bookappointment.html", msg=msg)

@app.route('/viewappointment')
def viewappointment():
    if session.get("logedin"):
        con = sql.connect("stroke.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("SELECT pname, pnumber, specialist FROM appointment")
        rows = cur.fetchall()
        return render_template("viewappointment.html", rows=rows)
    return redirect(url_for("userlogin"))

# ---------------------- Stroke Prediction ----------------------
@app.route("/result", methods=['POST'])
def result():
    gender = int(request.form['gender'])
    age = int(request.form['age'])
    hypertension = int(request.form['hypertension'])
    heart_disease = int(request.form['heart_disease'])
    work_type = int(request.form['work_type'])
    Residence_type = int(request.form['Residence_type'])
    avg_glucose_level = float(request.form['avg_glucose_level'])
    bmi = float(request.form['bmi'])
    smoking_status = int(request.form['smoking_status'])

    x = np.array([gender, age, hypertension, heart_disease, work_type, Residence_type,
                  avg_glucose_level, bmi, smoking_status]).reshape(1, -1)

    scaler = pickle.load(open('scalar.pkl', 'rb'))
    x = scaler.transform(x)

    with sql.connect("stroke.db") as con:
        con.execute("INSERT INTO predict VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (
            str(gender), str(age), str(hypertension), str(heart_disease), str(work_type),
            str(Residence_type), str(avg_glucose_level), str(bmi), str(smoking_status)
        ))
        con.commit()

    model = pickle.load(open('finalized_model.pkl', 'rb'))
    y_pred = model.predict(x)

    return render_template("nostroke.html" if y_pred == 0 else "stroke.html")

if __name__ == "__main__":
    app.run(debug=True)
