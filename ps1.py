from flask import Flask, request, url_for, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker

import random
import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pings.db'
app.config['SQLALCHEMY_ECHO'] = True
# app.config.update(dict(  PREFERRED_URL_SCHEME = 'https'))
db = SQLAlchemy(app)

@app.route('/makedb')
def make_database():
    db.create_all()
    return 'db created!'

class PingResult(db.Model):
    __tablename__ = 'ping_results'

    id = Column(Integer, primary_key=True)
    time = Column(String)
    origin = Column(String)
    target = Column(String)
    success = Boolean(Integer)
    rtt = Column(Integer)

    def __repr__(self):
        return "PingResult(id=%s, time=%s, origin=%s, target=%s, succes=%s, rtt=%s)" % \
            (self.id, self.time, self.origin, self.target, self.success, self.rtt)
    def toDict(self): # taka konwencja nazewnyczna zmiany typu na dict?
        return {'id':self.id, 'time':str(self.time), \
            'origin':str(self.origin), 'target':str(self.target), \
            'success':str(self.success), 'rtt':self.rtt}	

def query_add_args(q):
    id=request.args.get('id')
    if id is not None:
        q = q.filter(PingResult.id == id)

    start=request.args.get('start')
    if start is not None:
        q = q.filter(PingResult.time >= start)

    end=request.args.get('end')
    if end is not None:
        q = q.filter(PingResult.time < end)

    origin=request.args.get('origin')
    if origin is not None:
        q = q.filter(PingResult.origin == origin)

    target=request.args.get('target')
    if target is not None:
        q = q.filter(PingResult.target == target)

    limit=request.args.get('limit')
    if limit is not None:
        q = q.limit(limit)

    offset=request.args.get('offset')
    if offset is not None:
        q = q.offset(offset)

    return q

@app.route('/pings', methods=['GET'])
def pings_get():
    q = db.session.query(PingResult)
    q = query_add_args(q)
    return "<br>".join([ str(r) for r in q])

@app.route('/pings/<int:id>', methods=['GET'])
def pings_get_id(id):
    q = db.session.query(PingResult).filter(PingResult.id==id)
    pr = q.first()
    if pr is None:
        return 'Not found', 404
#    return str(jsonify(dict(pr)))		
    return jsonify(pr.toDict())
	
@app.route('/pings', methods=['POST'])
@app.route('/pings-post')    # do testów
def pings_post():
    id = request.args.get('id')
	# dozwolony tutaj?
	# kontrole
	# błąd przy podaniu istniejącego
    time = request.args.get('time')
    # kontrola czy jest
    # kontrola czy poprawny
    # kontrola czy nie odrzucić z powodu starości
    origin = request.args.get('origin')
    # kontrole ...
    target = request.args.get('target')
    # kontrole ...
    success = request.args.get('success').upper() not in ['FALSE', '0'] 
    print(success)
    # kontrole ...
    rtt = request.args.get('rtt')

    p = PingResult(id=id, time=time, origin=origin, target=target, success=success, rtt=rtt)
    db.session.add(p)
    db.session.commit()

    # resp = app.make_response(jsonify(p.toDict()))

    scheme = request.headers.get('X-Forwarded-Proto')       # metoda specyficzna na heroku, czy będzie dobrze działać w innych układach?
    if scheme is None:
        scheme = request.scheme
    
    headers = {}
    headers['Location'] = url_for('pings_get_id', id=p.id, _scheme=scheme, _external=True)
    headers['Content-Type'] = 'application/json'
    
    return app.make_response((jsonify(p.toDict()), 201, headers)) 

@app.route('/pings', methods=['DELETE'])
@app.route('/pings-delete') # do testów
def pings_delete():
    q = db.session.query(PingResult)
    query_add_args(q).delete(synchronize_session=False)
    db.session.commit()
    return 'deleted!'

@app.route('/origins')
def origins():
    q = db.session.query(PingResult.origin).distinct()
    q = query_add_args(q)
    return "<br>".join([ str(r) for r in q])

@app.route('/targets')
def targets():
    q = db.session.query(PingResult.target).distinct()
    q = query_add_args(q)
    return "<br>".join([ str(r) for r in q])
	
@app.route('/')
def root():
#    return '<!doctype html><html><body><a target="_blank" href="https://dashboard.heroku.com/apps/ping-store">manage app</a></body></html>'
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.getenv("PORT"))
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=port)
