from flask import Flask, render_template
from flask import request
from flask_bootstrap import Bootstrap
from flask_nav import Nav

import os
import MySQLdb
import datetime


db = MySQLdb.connect(host = "34.85.123.237", user = "root", passwd = "password", db = "kaistclubdb")
cur = db.cursor()
nav = Nav()
app = Flask(__name__)
bootstrap = Bootstrap(app)


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/eventretrieval')
def eventretrieval():
    return render_template("eventretrieval.html")

@app.route('/clubreg', methods=['GET'])
def clubreg():
    #getinfo()
    return render_template("clubreg.html") 

@app.route('/clubreg', methods=['POST'])
def getinfo():
    print(request.form)
    name = request.form['clubname']
    hours = request.form['clubhours']
    location = request.form['location']
    department = request.form['division']
    objective = request.form['Objective']
    
    ind = int(department)
    departments = ["Culture", "Performing Art", "Creative Arts", "Band Music", "Vocal Music", "Instrumental Music", "Society", "Religion", "Ball Sport", "Life Sport", "Science & Engineering", "Liberal Arts"]

    insert_stmt = (
    "INSERT INTO club (Name, MeetingHours, ManagerID, Location, Objective, Dname) VALUES (%s, %s, %s, %s, %s, %s)"
    )
    data = (name, hours, '00000', location, objective, departments[ind - 1])

    cur.execute(insert_stmt, data)
    db.commit()
    return render_template("index.html")

@app.route('/division')
def division():
    select_stmt = (
        "SELECT * FROM division"
        )
    cur.execute(select_stmt)
    divs = cur.fetchall()
    return render_template("division.html", divs = divs)

@app.route('/clubretrieval', methods=['GET'])
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
        "CREATE VIEW events AS SELECT EventID FROM hostdiv where Division='%s'" %(div, )
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
    except MySQLdb.OperationalError:
        try:
            select_stmt = (
                "SELECT * FROM club where Dname='%s'" %(div, )
                )
            cur.execute(select_stmt)
            clubs = cur.fetchall()
            print(clubs)
            return render_template("clubretrieval.html", div = div, clubs = clubs)
        except MySQLdb.OperationalError:
            return render_template("index.html")
        
@app.route('/eventinfo', methods=['GET'])
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
  

@app.route('/clubinfo', methods=['GET'])
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
#cur.execute(insert_stmt, data)


#db.commit()
#db.close()

if __name__ == '__main__':
    app.run()
