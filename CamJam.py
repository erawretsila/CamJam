#! venv/bin/python
#  
#  Copyright 2026 Unknown <alister.ware@ntlworld.com>
#  
#  This programm uses no AI and depends solely on NS (Natural Stupidity)
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

import sqlite3 as SQL
import csv
from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/test')
def test():
    return render_template('home.html')

@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'POST':
        data = request.form
        search = [f"{x} like '%{data[x]}%'" for x in data if data[x] != '']
        db=SQL.connect('CamJam.db')
        cursor=db.cursor()
        if search:
            sql = f'''SELECT * FROM tickets WHERE {' and '.join(search)}'''
        else:
            sql = "select * from tickets"
        results = cursor.execute(sql).fetchall()
    else:
        results = []
    return render_template('index.html',fields=fieldnames,results=results)

@app.route('/toggle')
def toggle():
    db = SQL.connect('CamJam.db')
    cursor = db.cursor()
    record = request.args.get('id')
    cursor.execute('UPDATE tickets SET Checked_In = NOT Checked_In WHERE id = ?',[record])
    db.commit()
    return 'OK'

def cam_jam():
    db = setup_db()   
    return db

def format_values(data):
    values = list()
    for row in data:
        value = tuple(row.values())
        values.append(value)
    return values

def setup_db():
    with open('CamJam.csv','r') as camjam:
        data = csv.DictReader(camjam)
        db = SQL.connect('CamJam.db')
        cursor=db.cursor()
        sql = ['CREATE TABLE IF NOT EXISTS tickets (id INTEGER PRIMARY KEY']
        for key in  data.fieldnames:
            sql.append(key +" text")
        sql = ','.join(sql)+')'
        cursor.execute(sql)
        values=format_values(data)
        for value in values:
            sql = f'''SELECT id FROM tickets WHERE Ticket_ID = {value[0]}'''
            results = cursor.execute(sql)
            if len(results.fetchall()) == 0:
                sql = f'INSERT INTO tickets({",".join(data.fieldnames)}) VALUES ({",".join('?'*len(data.fieldnames))})'
                cursor.execute(sql,value)
        db.commit()
        return data.fieldnames

if __name__ == "__main__":
    fieldnames=cam_jam()
    app.run()
