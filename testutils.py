from functools import wraps
from hashlib import md5

import os
import datetime
import pymysql

db = pymysql.connect(host = "34.85.123.237", user = "root", passwd = "password", db = "kaistclubdb")
cur = db.cursor()

for i in range(10000):
    try:
        insert_stmt = "INSERT INTO student (Name, SID, Department) VALUES ('Testname', 2015%04d, 'CS')" %(i,)
        cur.execute(insert_stmt)
        db.commit()
    except pymysql.OperationalError:
        print("ERROR")
    except pymysql.IntegrityError:
        print("INTERROR")


print("DONE")
