import sqlite3
from flask import Flask, render_template, g, request, redirect, url_for
from datetime import datetime

app = Flask('jobs')

PATH = 'db/jobs.sqlite'
def open_connection():
  connection = getattr(g, '_connection', None)
  if connection is None:
    connection = sqlite3.connect(PATH)
    g._connection = sqlite3.connect(PATH)
  connection.row_factory = sqlite3.Row
  return connection

def execute_sql(sql, values: tuple = (), commit: bool = False, single: bool = False):
  connection = open_connection()
  cursor = connection.execute(sql, values)
  if commit:
    results = connection.commit()
  else:
    results = cursor.fetchone() if single else cursor.fetchall()
  
  cursor.close()
  
  return results

@app.teardown_appcontext
def close_connection(exception: Exception):
  connection = getattr(g, '_connection', None)
  if connection is not None:
    connection.close()

@app.route('/')
@app.route('/jobs')
def jobs():
  jobs = execute_sql('SELECT job.id, job.title, job.description, job.salary, employer.id as employer_id, employer.name as employer_name FROM job JOIN employer ON employer.id = job.employer_id')
  
  return render_template('index.html', jobs=jobs)

@app.route('/job/<job_id>')
def job(job_id: int):
  job = execute_sql('SELECT job.id, job.title, job.description, job.salary, employer.id as employer_id, employer.name as employer_name FROM job JOIN employer ON employer.id = job.employer_id WHERE job.id = ?', [job_id], single=True)
  
  return render_template('job.html', job=job)

@app.route('/employer/<employer_id>')
def employer(employer_id: int):
  employer = execute_sql('SELECT * FROM employer WHERE id=?', [employer_id], single=True)
  jobs = execute_sql('SELECT job.id, job.title, job.description, job.salary FROM job JOIN employer ON employer.id = job.employer_id WHERE employer.id = ?', [employer_id])
  reviews = execute_sql('SELECT review, rating, title, date, status FROM review JOIN employer ON employer.id = review.employer_id WHERE employer.id = ?', [employer_id])
  
  return render_template('employer.html', employer=employer, jobs=jobs, reviews=reviews)

@app.route('/employer/<employer_id>/review', methods=('GET', 'POST'))
def review(employer_id: int):
  if request.method == 'POST':
    review: str = request.form['review']
    rating: int = request.form['rating']
    title: str = request.form['title']
    status: str = request.form['status']

    date = datetime.now().strftime("%m/%d/%Y")
    execute_sql('INSERT INTO review (review, rating, title, date, status, employer_id) VALUES (?, ?, ?, ?, ?, ?)', (review, rating, title, date, status, employer_id), commit=True)
    
    return redirect(url_for('employer', employer_id=employer_id))
  return render_template('review.html', employer_id=employer_id)