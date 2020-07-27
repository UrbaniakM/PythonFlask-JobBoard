import sqlite3
from flask import Flask, render_template, g

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
