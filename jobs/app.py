from flask import Flask, render_template

app = Flask('jobs')

@app.route('/')
@app.route('/jobs')
def jobs():
  return render_template('index.html')
