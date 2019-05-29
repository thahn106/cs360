from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask import Flask, session
from markupsafe import escape

from functools import wraps

from hashlib import md5

import os
import datetime
from datetime import datetime
from datetime import timedelta
import pymysql
import sqlalchemy

from synch import *

frontend = Blueprint('frontend', __name__)

db = "Uninitialized"
cur= "Uninitialized"


def init(local = False):
    global db
    global cur
    if (local):
        print("Local init")
        db = pymysql.connect(host = "34.85.123.237", user = "root", passwd = "password", db = "kaistclubdb")
    else:
        print("Server init")
        engine = sqlalchemy.create_engine(
            sqlalchemy.engine.url.URL(
                drivername='mysql+pymysql',
                username='root',
                password='password',
                database='kaistclubdb',
                query={
                    'unix_socket': '/cloudsql/{}'.format('effective-relic-240011:asia-northeast1:kaistclubdb')
                }
            ),
            # ... Specify additional properties here.
            # ...
        )
        db = engine.raw_connection()

    cur = db.cursor()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('frontend.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@frontend.context_processor
def update_dict():
    select_stmt = (
        "SELECT * FROM division"
        )
    cur.execute(select_stmt)
    divs = cur.fetchall()
    clubs=""
    user = ""
    if 'username' in session:
        user = session['username']
        select_stmt = ("SELECT * FROM club WHERE ManagerID= '%s'" %(user))
        cur.execute(select_stmt)
        clubs = cur.fetchall()
    return dict(divs=divs, user=user, myclubs=clubs)

@frontend.route('/')
def index():
    return render_template('index.html')

@frontend.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('frontend.index'))
    error = None
    try:
        if request.method == 'POST':
            username_form = request.form['username']
            select_stmt = ("SELECT * FROM admin WHERE ID= '%s'" %(username_form))
            print(select_stmt)
            cur.execute(select_stmt)
            table = cur.fetchone()
            print(table)

        if table == None:
            print("jokka")
            raise Exception('Invalid username')

        password_form = request.form['password']
        select_stmt1 = ("SELECT PW FROM admin WHERE ID= '%s'" %(username_form))
        print(select_stmt1)
        cur.execute(select_stmt1)

        PW=str(password_form).encode('utf-8')
        for row in cur.fetchall():
            print("checking password")
            print(md5(PW).hexdigest())
            print(row[0])
            if md5(PW).hexdigest() == row[0]:
                session['username'] = request.form['username']
                return redirect(url_for('frontend.index'))

        raise Exception('Invalid password')
    except Exception as e:
        error = str(e)

    return render_template('login.html', error = error)

@frontend.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('frontend.index'))

@frontend.route('/signup', methods=['GET'])
def signup_get():
    return render_template("signup.html")

@frontend.route('/signup', methods=['POST'])
def signup_post():
    print(request.form)
    ID = request.form['ID']
    PW = request.form['PW']
    Pnumber = request.form['Pnumber']
    SID = request.form['SID']
    email = request.form['email']
    insert_stmt = (
    "INSERT INTO admin (ID, PW, Pnumber, SID, email) VALUES (%s, %s, %s, %s, %s)"
    )
    PW=str(PW).encode('utf-8')
    print(md5(PW).hexdigest())
    data = (ID, md5(PW).hexdigest(), Pnumber, SID, email)
    cur.execute(insert_stmt, data)
    db.commit()
    return render_template("signup.html")

@frontend.route('/newstudent', methods=['GET'])
@login_required
def newstudent_get():
    return render_template("newstudent.html")

@frontend.route('/newstudent', methods=['POST'])
@login_required
def newstudent_post():
    print(request.form)
    Name = request.form['Name']
    SID = request.form['SID']
    Department = request.form['Department']
    insert_stmt = (
    "INSERT INTO student (Name, SID, Department) VALUES (%s, %s, %s)"
    )
    data = (Name, SID, Department)
    cur.execute(insert_stmt, data)
    db.commit()
    return render_template("newstudent.html")



@frontend.route('/eventretrieval')
def eventretrieval():
    return render_template("eventretrieval.html")

@frontend.route('/clubreg', methods=['GET'])
@login_required
def clubreg_get():
    return render_template("clubreg.html")

@frontend.route('/clubreg', methods=['POST'])
@login_required
def clubreg_post():
    print(request.form)
    name = request.form['clubname']
    hours = request.form['clubhours']
    location = request.form['location']
    department = request.form['division']
    objective = request.form['Objective']
    username = session['username'];

    try:
        select_stmt = ("SELECT * FROM club WHERE Name= '%s'" %(name,))
        cur.execute(select_stmt)
        clubs = cur.fetchall()
        if clubs:
            return render_template("clubreg.html", err="Club %s already registered."%(name,))

        insert_stmt = (
        "INSERT INTO club (Name, MeetingHours, ManagerID, Location, Objective, Dname) VALUES (%s, %s, %s, %s, %s, %s)"
        )
        data = (name, hours, username, location, objective, department)

        cur.execute(insert_stmt, data)
        db.commit()
        return render_template("index.html", message="Club registered successfully!")
    except pymysql.OperationalError:
        return render_template("index.html", err="Unknown error.")
    return render_template("index.html")

@frontend.route('/newevent', methods=['GET'])
@login_required
def newevet_get():
    return render_template("newevent.html")

@frontend.route('/newevent', methods=['POST'])
@login_required
def newevent_post():
    eventname = request.form['eventname']
    clubname = request.form['clubname']
    date = request.form['date']
    location = request.form['location']
    description = request.form['description']
    divname = request.form['divname']

    print(clubname)
    div = False
    if(clubname == ""):
        div = True

    print(div)

    if(not div):
        select_stmt = (
            "SELECT ManagerID FROM club where Name='%s'"%(clubname, )
        )
        cur.execute(select_stmt)
        admin = cur.fetchone()[0]
        print(admin)

        try:
            if 'username' in session:
                user = session['username']

            if  user == admin:
                count_stmt = (
                    "SELECT COUNT(*) FROM event"
                )
                cur.execute(count_stmt)
                count = str(cur.fetchone()[0])
                while(len(count) < 8):
                    count = "0" + count;

                insert_stmt = (
                    "INSERT INTO event VALUES (%s, %s, %s, %s, %s, %s)"
                )
                data = (count, eventname, clubname, date, location, description)
                cur.execute(insert_stmt, data)
                insert_stmt = (
                    "INSERT INTO hostclub VALUES (%s, %s)"
                )
                data = (count, clubname)
                cur.execute(insert_stmt, data)
                db.commit()
        except pymysql.OperationalError:
            return render_template("index.html", err="Unknown error.")

        return redirect(url_for('frontend.clubinfo', club=clubname))
    else:
        select_stmt = (
            "SELECT HeadID FROM division where Name='%s'"%(divname, )
        )
        cur.execute(select_stmt)
        admin = cur.fetchone()[0]
        print(admin)

        try:
            if 'username' in session:
                user = session['username']

            if  user == admin:
                count_stmt = (
                    "SELECT COUNT(*) FROM event"
                )
                cur.execute(count_stmt)
                count = str(cur.fetchone()[0])
                while(len(count) < 8):
                    count = "0" + count;

                insert_stmt = (
                    "INSERT INTO event VALUES (%s, %s, %s, %s, %s, %s)"
                )
                data = (count, eventname, divname, date, location, description)
                cur.execute(insert_stmt, data)
                insert_stmt = (
                    "INSERT INTO hostdiv VALUES (%s, %s)"
                )
                data = (count, divname)
                cur.execute(insert_stmt, data)
                db.commit()
        except pymysql.OperationalError:
            return render_template("index.html", err="Unknown error.")

        return redirect(url_for('frontend.clubretrieval', div=divname))

@frontend.route('/events')
def view_events():


    dt = datetime.now() - timedelta(days = 1)
    dt = str(dt)
    select_stmt = (
        "SELECT * FROM event where DateTime >= '%s'" %(dt,)
    )
    cur.execute(select_stmt)
    events = cur.fetchall()
    events = list(events)
    print(events)

    for i in range(1, len(events)):
        j = i-1
        next = events[i]
        nxt_element = events[i][3]
# Compare the current element with next one

        while (events[j][3] > nxt_element) and (j >= 0):
            events[j+1] = events[j]
            j=j-1
        events[j+1] = next

    return render_template("events.html", events = events)


@frontend.route('/newmember', methods=['GET'])
@login_required
def newmember_get():
    return render_template("newmember.html")

@frontend.route('/newmember', methods=['POST'])
@login_required
def newmember_post():
    clubname = request.form['clubname']
    studentid = request.form['sid']
    try:
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
        cur.execute(insert_stmt, data)
        db.commit()

        return render_template("newmember.html",message="Member added.")

    except pymysql.OperationalError:
        return render_template("index.html", err="Unknown error.")

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

    print(div)
    try:
        select_stmt = (
            "SELECT * FROM club where Dname='%s'" %(div, )
            )
        cur.execute(select_stmt)
        clubs = cur.fetchall()
        print(clubs)

        select_stmt1 = (
            "CREATE VIEW events AS SELECT Event FROM hostdiv where Division='%s'" %(div, )
        )
        select_stmt2 = (
            "SELECT EventID, EventName FROM event INNER JOIN events ON events.Event = event.EventID"
        )

        delete_stmt = (
            "DROP VIEW events"
        )

        lock_acquire(cur=cur, str="events")

        cur.execute(select_stmt1)
        cur.execute(select_stmt2)
        event1 = cur.fetchall()
        print(event1)
        cur.execute(delete_stmt)
        lock_release(cur=cur, str="events")

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
    print(event)
    select_stmt = (
        "SELECT * FROM event where EventID='%s'" %(event, )
    )
    cur.execute(select_stmt)
    info = cur.fetchall()
    eventname = info[0][1]
    clubname = info[0][2]
    datetime = info[0][3]
    location = info[0][4]
    description = info[0][5]

    return render_template("eventinfo.html", event = event, eventname= eventname, clubname = clubname, datetime = datetime, location = location, description = description)

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
    admin = info[0][3]

    select_stmt1 = (
        "CREATE VIEW events AS SELECT EventID FROM hostclub where Club='%s'" %(clubname, )
    )
    select_stmt2 = (
        "SELECT * FROM event NATURAL JOIN events"
    )

    delete_stmt = (
        "DROP VIEW IF EXISTS events"
    )

    lock_acquire(cur, 'event')
    cur.execute(delete_stmt)
    cur.execute(select_stmt1)
    cur.execute(select_stmt2)
    event1 = cur.fetchall()
    print(event1)
    print("PRINT")
    cur.execute(delete_stmt)
    lock_release(cur, 'event')

    select_stmt1 = (
        "CREATE VIEW manager AS SELECT ManagerID FROM club where Name='%s'" %(clubname, )
    )
    select_stmt2 = (
        "CREATE VIEW managersid AS SELECT SID, Pnumber, Email FROM admin INNER JOIN manager ON manager.ManagerID = admin.ID"
    )
    select_stmt3 = (
        "SELECT * FROM managersid NATURAL JOIN student"
    )

    delete_stmt = (
        "DROP VIEW IF EXISTS manager"
    )
    delete_stmt2 = (
        "DROP VIEW IF EXISTS managersid"
    )
    lock_acquire(cur, 'event')
    cur.execute(delete_stmt)
    cur.execute(delete_stmt2)
    cur.execute(select_stmt1)
    cur.execute(select_stmt2)
    cur.execute(select_stmt3)
    manager = cur.fetchone()
    cur.execute(delete_stmt)
    cur.execute(delete_stmt2)
    lock_release(cur, 'event')
    user=""
    if 'username' in session:
        user = session['username']

    memberlist=""
    if  user == admin:
        select_stmt = (
            "SELECT * FROM member WHERE Club='%s'"%(clubname, )
        )
        cur.execute(select_stmt)
        memberlist = cur.fetchall()
        if not memberlist:
            memberlist = [(None,0)]
    return render_template("clubinfo.html", club = club, clubname= clubname, division = division, Objective = Objective, hours = hours, events = event1, memberlist=memberlist, admin = manager)


# Our index-page just shows a quick explanation. Check out the template
# "templates/index.html" documentation for more details.
