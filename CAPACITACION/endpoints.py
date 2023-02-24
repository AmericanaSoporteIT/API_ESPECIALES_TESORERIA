from AppContext import app, cors, get_db, base_url_path
from SQLQueries import *
from flask import Flask, request,jsonify, make_response, json
from odbc import *
from serialization import *
import gzip



from werkzeug.local import LocalProxy

db = LocalProxy(get_db)


@app.route(f'{base_url_path}/v2/data.json')
def compress_test():
    cursor = db.cursor()
    res = toJsonDump(cursor.execute(QueryEmployee))    
    content = gzip.compress(json.dumps(res).encode('utf8'), 5)
    response = make_response(content)
    response.headers['Content-length'] = len(content)
    response.headers['Content-Encoding'] = 'gzip'
    return response


def compress(result):
    content = gzip.compress(json.dumps(result).encode('utf8'), 5)
    response = make_response(content)
    response.headers['Content-length'] = len(content)
    response.headers['Content-Encoding'] = 'gzip'
    return response


@app.route(f'{base_url_path}v2/employees', methods=['GET'])
def get_employees():
    if request.args:
        offset = request.args.get('offset', default=10, type=int)
        fetch_next = request.args.get('next', default=50, type=int)
        cursor = db.cursor()
        res = compress( toJson(
            cursor.execute(QueryEmployee + ' OFFSET ? ROWS FETCH NEXT ? ROWS ONLY', offset, fetch_next ) 
        ))
        return res
    else:
        cursor = db.cursor()
        res = compress(toJson(cursor.execute(QueryEmployee)))
        return res


@app.route(f'{base_url_path}v2/listStateEmployee', methods=['GET'])
def list_state_employee():
    cursor = db.cursor()
    res =  compress(toJsonDump( cursor.execute(QueryListStateEmployee)))
    return res

@app.route(f'{base_url_path}v2/companies')
def list_companies():
    cursor = db.cursor()
    res = compress(toJsonDump(cursor.execute(QueryListCompanies)))
    return res

@app.route(f'{base_url_path}v2/photo', methods=['GET'])
def get_photo():
    if request.args:
        cui = request.args.get('id')
        cursor = db.cursor()
        res = compress( toJson(
            cursor.execute(QueryGetPhoto + ' AND cui = ? ', cui) 
        ))
        return res
    else:
        cursor = db.cursor()
        res = compress(toJson(cursor.execute(QueryGetPhoto)))
        return res


import os
os.environ["FLASK_ENV"] = 'development' 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port="5010", debug=True)