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
import os
import sqlite3 as SQL
import csv
from flask import Flask, request, render_template, flash, redirect, url_for
from werkzeug.utils import secure_filename

import argparse

UPLOAD_FOLDER = 'Uploads'
ALLOWED_EXTENSIONS = {'csv','CSV'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/test')
def test():
    return render_template('home.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload.html', methods=['GET', 'Post'])
def upload():
    global filenames
    if request.method != 'POST':
        return render_template('upload.html')
    if 'file' not in request.files:
        return render_template('upload.html')
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        filenames = setup_db()       
        return redirect('/')

@app.route('/', methods=['GET', 'POST'])
def index():
    if fieldnames is None:
        return redirect('upload.html')
    
    if request.method == 'POST':
        data = request.form
        search = [f"{x} like '%{data[x]}%'" for x in data if data[x] != '']
        db=SQL.connect('CamJam.db')
        db.row_factory = SQL.Row
        cursor=db.cursor()
        if search:
            sql = f'''SELECT * FROM tickets WHERE {' and '.join(search)}'''
        else:
            sql = "select * from tickets"
        results = cursor.execute(sql).fetchall()
        print(f'Fields:\t{fieldnames}\tResults\t{results}')
        return render_template('index.html',fields=fieldnames,results=results)
        
    else:
        results = []
        fields = []
        print(f'Fields:\t{fieldnames}\tResults\t{results}')
        return render_template('index.html',fields=fieldnames,results=results)


@app.route('/toggle')
def toggle():
    db = SQL.connect('CamJam.db')
    cursor = db.cursor()
    record = request.args.get('id')
    cursor.execute('UPDATE tickets SET Checked_In = NOT Checked_In WHERE id = ?',[record])
    db.commit()
    print('Checked in status toggled')
    return 'OK'

@app.route('/release')
def release():
    db = SQL.connect('CamJam.db')
    cursor = db.cursor()
    record = request.args.get('id')
    cursor.execute(f'UPDATE tickets SET Released = NOT Released where id = ? and Released !=1;',[record])
    db.commit()
    results = cursor.execute("SELECT Ticket_ID from tickets where id = ?",[record]).fetchone()
    print(results)
    cursor.execute("INSERT INTO tickets (Ticket_ID, First_Name, Surname, QTY, Type,Checked_in,Released) Values (?,'Spare','','1','Dropin','0',0)",results )
    db.commit()
    return "ok"

@app.route('/stats')
def statistics():
    results={}
    db = SQL.connect('CamJam.db')
    cursor = db.cursor()  
    sql = "Select count(*) from tickets where Checked_In = 1"
    results['total'] = cursor.execute(sql).fetchone()
    sql = "Select count(*) from tickets where Type like '%JamMaker%' AND Checked_In = 1"
    results['jammaker'] = cursor.execute(sql).fetchone()
    sql = "Select count(*) from  tickets where Type like '%Adult%' AND Checked_In = 1"
    results['adult'] = cursor.execute(sql).fetchone()
    sql = "Select count(*) from tickets where Type like '%Child%' AND Checked_In = 1"
    results['children'] = cursor.execute(sql).fetchone()
    sql = "Select count(*) from tickets where type like '%Dropin%' AND Checked_In = 1"
    results['dropins'] = cursor.execute(sql).fetchone()
    return render_template('statistics.html',results=results)

def cam_jam():
    try:
        return setup_db()
    except FileNotFoundError:
        return None
    
def format_values(data):
    values = list()
    for row in data:
        value = tuple(row.values())
        values.append(value)
    return values

def setup_db():
    db = SQL.connect('CamJam.db')
    with open('Uploads/CamJam.csv','r') as camjam:
        data = csv.DictReader(camjam)
        data.fieldnames = [x.replace(" ","_") for x in data.fieldnames]
#        db = SQL.connect('CamJam.db')
        cursor=db.cursor()
        sql = ['CREATE TABLE IF NOT EXISTS tickets (id INTEGER PRIMARY KEY']
        for key in  data.fieldnames:
            sql.append(key +" text")
        sql = ','.join(sql)+')'
        print(sql)
        cursor.execute(sql)
        cursor.execute(f"PRAGMA table_info(tickets);")
        columns = [row[1] for row in cursor.fetchall()]  # Extract column names (row[1] is the name)
        if "Checked_In" not in columns:
            # Add the column
            cursor.execute(f"ALTER TABLE tickets ADD COLUMN Checked_In text Default 0;")
 
        if "Released" not in columns:
            # Add the column
            cursor.execute(f"ALTER TABLE tickets ADD COLUMN Released text Default 0;")
        values=format_values(data)
        for value in values:
            sql = f'''SELECT id FROM tickets WHERE Ticket_ID = {value[0]}'''
            results = cursor.execute(sql)
            if len(results.fetchall()) == 0:
                sql = f'INSERT INTO tickets({",".join(data.fieldnames)}) VALUES ({",".join('?'*len(data.fieldnames))})'
                cursor.execute(sql,value)
        db.commit()
        data.fieldnames.append("Checked_In")
        data.fieldnames.append("Released")

        return data.fieldnames

if __name__ == "__main__":
    parser  = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', help='Use in Memory Database', action="store_true")
    args = parser.parse_args()
    fieldnames=cam_jam()
    app.run()
