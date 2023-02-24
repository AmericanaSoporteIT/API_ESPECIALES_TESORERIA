from flask import Flask, g
from  flask_cors import CORS
from odbc import *

base_url_path = '/api/'

app = Flask(__name__, instance_relative_config=True)
app.config["JSON_SORT_KEYS"] = False 
cors = CORS(app, resources={f"{base_url_path}*": {"origins": "*"}})

def get_db():
    mssql = Odbc("TESOSRERIA")
    if 'db' not in g:
        #auto_comit defaul is false
        g.db =  mssql.connect(char_encode='', auto_commit=False) 
        return g.db

@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()
