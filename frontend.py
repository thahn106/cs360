from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask import Flask, session
from markupsafe import escape

from functools import wraps


import os
import pymysql
import datetime

frontend = Blueprint('frontend', __name__)

db = pymysql.connect(host = "34.85.123.237", user = "root", passwd = "password", db = "kaistclubdb")
cur = db.cursor()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('frontend.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@frontend.context_processor
def div_dict():
    select_stmt = (
        "SELECT * FROM division"
        )
    cur.execute(select_stmt)
    divs = cur.fetchall()
    return dict(divs=divs)

@frontend.route('/signup')
def signup_get():
    return render_template("signup.html")

# We're adding a navbar as well through flask-navbar. In our example, the
# navbar has an usual amount of Link-Elements, more commonly you will have a
# lot more View instances.
# nav.register_element('frontend_top', Navbar(
#     View('KAIST Clubs', '.index'),
#     View('Home', '.index'),
#     View('Club Registration', '.clubreg'),
#     View('New Event', '.newevent'),
#     ))
@frontend.route('/')
def index():
    return render_template('index.html')

@frontend.route('/eventretrieval')
def eventretrieval():
    return render_template("eventretrieval.html")

@frontend.route('/clubreg', methods=['GET'])
def clubreg():
    return render_template("clubreg.html")

@frontend.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('frontend.index'))
    error = None
    try:
        if request.method == 'POST':
            print("here")
            username_form = request.form['username']
            print("jotto")
            select_stmt = ("SELECT * FROM admin WHERE ID= '%s'" %(username_form))
            print(select_stmt)
            cur.execute(select_stmt)
            print("shibal")
            table = cur.fetchone()
            print(table)

        if table == None:
            print("jokka")
            raise Exception('Invalid username')

        password_form = request.form['password']
        select_stmt1 = ("SELECT PW FROM admin WHERE ID= '%s'" %(username_form))
        print(select_stmt1)
        cur.execute(select_stmt1)

        for row in cur.fetchall():
            print("shipsaekki")
            #if md5(password_form).hexdigest() == row[0]:
            if password_form == row[0]:
                print("ertyui")
                session['username'] = request.form['username']
                return redirect(url_for('frontend.index'))

        raise Exception('Invalid password')
    except Exception as e:
        print("jottoshibal")
        error = str(e)

    return render_template('login.html', error = error)

@frontend.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('frontend.index'))

@frontend.route('/signup')

@frontend.route('/clubreg', methods=['POST'])
def getinfo():
    print(request.form)
    name = request.form['clubname']
    hours = request.form['clubhours']
    location = request.form['location']
    department = request.form['division']
    objective = request.form['Objective']

    insert_stmt = (
    "INSERT INTO club (Name, MeetingHours, ManagerID, Location, Objective, Dname) VALUES (%s, %s, %s, %s, %s, %s)"
    )
    data = (name, hours, '00000', location, objective, department)

    cur.execute(insert_stmt, data)
    db.commit()
    return render_template("index.html")

@frontend.route('/newmember', methods=['GET'])
@login_required
def memberreg():
    clubname = (request.args.get('clubname'))
    return render_template("newmember.html", clubname = clubname)

@frontend.route('/newmember', methods=['POST'])
@login_required
def newmember():
    clubname = request.form['clubname']
    studentid = request.form['sid']
    select_stmt = (
        "SELECT * FROM student"
    )
    cur.execute(select_stmt)
    students = cur.fetchall()
    here = False
    for student in students:
        if(student[1] == studentid):
            here = True
            break

    if(not(here)):
        #student id is not there
        return render_template("newmember.html", clubname=clubname, sid=studentid, err="Unregistered Student ID.")

    here = False
    select_stmt = (
        "SELECT * FROM member"
    )
    cur.execute(select_stmt)
    members = cur.fetchall()


    for member in members:
        if(member[0] == studentid):
            if(member[1] == clubname):
                here = True
                break

    if(here):
        return render_template("newmember.html", clubname=clubname, sid=studentid, err="Student already registered.")

    insert_stmt = (
        "INSERT INTO member (SID, Club) VALUES (%s, %s)"
        )

    data = (studentid, clubname)
    cur.execute(insert_stmt)
    db.commit()

    return render_template("index.html")


@frontend.route('/division')
def division():
    select_stmt = (
        "SELECT * FROM division"
        )
    cur.execute(select_stmt)
    divs = cur.fetchall()
    return render_template("division.html", divs = divs)

@frontend.route('/clubretrieval', methods=['GET'])
def clubretrieval():
    div = (request.args.get('div'))
    try:
        select_stmt = (
            "SELECT * FROM club where Dname='%s'" %(div, )
            )
        cur.execute(select_stmt)
        clubs = cur.fetchall()
        print(clubs)

        select_stmt1 = (
        "CREATE VIEW events AS SELECT 'EventID' FROM hostdiv where Division='%s'" %(div, )
        )
        select_stmt2 = (
        "SELECT Name FROM event NATURAL JOIN events"
        )

        delete_stmt = (
        "DROP VIEW events"
        )
        cur.execute(select_stmt1)
        cur.execute(select_stmt2)
        event1 = cur.fetchall()
        print(event1)
        cur.execute(delete_stmt)

        return render_template("clubretrieval.html", div = div, clubs = clubs, events = event1)
    except pymysql.OperationalError:
        try:
            select_stmt = (
                "SELECT * FROM club where Dname='%s'" %(div, )
                )
            cur.execute(select_stmt)
            clubs = cur.fetchall()
            print(clubs)
            return render_template("clubretrieval.html", div = div, clubs = clubs)
        except pymysql.OperationalError:
            return render_template("index.html")

@frontend.route('/eventinfo', methods=['GET'])
def eventinfo():
    event = (request.args.get('event'))
    select_stmt = (
        "SELECT * FROM event where Name='%s'" %(event, )
    )
    cur.execute(select_stmt)
    info = cur.fetchall()
    eventname = info[0][0]
    datetime = info[0][1]
    location = info[0][2]

    return render_template("eventinfo.html", event = event, eventname= eventname, datetime = datetime, location = location)
#cur.execute(insert_stmt, data)


@frontend.route('/clubinfo', methods=['GET'])
def clubinfo():
    club = (request.args.get('club'))
    select_stmt = (
        "SELECT * FROM club where Name='%s'" %(club, )
    )
    cur.execute(select_stmt)
    info = cur.fetchall()
    clubname = info[0][0]
    division = info[0][5]
    Objective = info[0][4]
    hours = info[0][1]

    select_stmt1 = (
        "CREATE VIEW events AS SELECT EventID FROM hostclub where Club='%s'" %(clubname, )
    )
    select_stmt2 = (
        "SELECT Name FROM event NATURAL JOIN events"
        )

    delete_stmt = (
        "DROP VIEW events"
        )

    cur.execute(select_stmt1)
    cur.execute(select_stmt2)
    event1 = cur.fetchall()
    print(event1)
    cur.execute(delete_stmt)
    return render_template("clubinfo.html", club = club, clubname= clubname, division = division, Objective = Objective, hours = hours, events = event1)


@frontend.route('/newevent')
def newevent():
    return render_template('newevent.html')

# Our index-page just shows a quick explanation. Check out the template
# "templates/index.html" documentation for more details.
