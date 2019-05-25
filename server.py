from flask import Flask, render_template
from flask import request

import os
import MySQLdb
import datetime


db = MySQLdb.connect(host = "34.85.123.237", user = "root", passwd = "password", db = "kaistclubdb")
cur = db.cursor()
app = Flask(__name__)



@app.route('/')
def index():
    return render_template("index.html")

@app.route('/eventretrieval')
def eventretrieval():
    bob = 5;
    return render_template("eventretrieval.html")


"""@app.route('/',methods=["POST"])
def login():
    print (request.form)
    if request.form['type'] == 'signup':
        email = request.form['email']
        password = request.form['password1']
        user_id =  request.form['id']
        sid = request.form['sid']
        pnumber = request.form['phone number']
        try:
            insert_stmt = (
                "INSERT INTO admin (ID, PW, Pnumber, Email, SID) VALUES (%s, %s, %s, %s, %s)"
                )
            data = (user_id, password, pnumber, email, sid)
            cur.execute(insert_stmt, data)
        except sqlite3.IntegrityError:
            return render_template("signup.html", warning="Sorry, email already taken.")

        db.commit()
        return render_template("index.html")
    else:
        user_id = request.form['id']
        password = request.form['password']
        query = "SELECT * from user_info where ID='%s' and PW='%s'" %(user_id.strip(),password.strip())
        print (query)
        cur.execute(query)
        user_info = cur.fetchall()
        print (user_info)
        if not user_info:
            warning = "Incorrect id or password. Please try again."
            return render_template("index.html", warning=warning)
        return extract(user_info[0][2])

    cur.execute("SELECT expertise from expertise where id=?", (user_id,))"""


@app.route('/clubreg', methods = ['POST'])
def clubreg():
    name = request.form['validationCustom01']
    hours = request.form['validationCustom02']
    location = request.form['validationCustom03']
    depatment = request.form['validationCustom04']
    objective = request.form['Objective']

    departments = ["Culture", "Performing Art", "Creative Art", "Band Music", "Vocal Music", "Instrumental Music", "Society", "Religion", "Ball Sports", "Life Sports", "Science & Engineering", "Liberal Arts"]


    insert_stmt = (
    "INSERT INTO club (Name, MeetingHours, ManagerID, Location, Objective, Dname) VALUES (%s, %s, %s, %s, %s)"
        )
    data = (name, hours, '00000', location, objective, departments[department-1])

    cur.execute(insert_stmt, data)
    db.commit()


#cur.execute(insert_stmt, data)

"""insert_stmt = (
    "INSERT INTO admin (ID, PW, Pnumber, Email, SID) VALUES (%s, %s, %s, %s, %s)"
        )
data = (user_id, password, pnumber, email, sid)

cur.execute(insert_stmt, data)

select_stmt = (
    "SELECT * FROM event"
    )

#cur.execute(select_stmt)
cur.execute("DELETE FROM event")
print(cur.fetchall())"""


#db.commit()
#db.close()

if __name__ == '__main__':
    app.run()