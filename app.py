import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, abort
##Some of these imports may be unecessary

app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'your secret key'

@app.route('/')
def index():
    
    return render_template('index.html')

app.run()