from flask import Flask, render_template

app = Flask('Job board')

def jobs():
  return render_template('index.html')

app.route('/')(jobs)
app.route('/jobs')(jobs)