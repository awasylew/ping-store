from flask import Flask, request, url_for
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
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
    success = Column(Integer)
    rtt = Column(Integer)

    def __repr__(self):
        return "PingResult(id=%s, time=%s, origin=%s, target=%s, succes=%s, rtt=%s)" % \
            (self.id, self.time, self.origin, self.target, self.success, self.rtt)

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
    return 'single ping'
	
	
@app.route('/pings', methods=['POST'])
@app.route('/pings-post')    # do testów
def pings_post():
    time = request.args.get('time')
    # kontrola czy jest
    # kontrola czy poprawny
    # kontrola czy nie odrzucić z powodu starości
    origin = request.args.get('origin')
    # kontrole ...
    target = request.args.get('target')
    # kontrole ...
    success = request.args.get('success')
    # kontrole ...
    rtt = request.args.get('rtt')	
    p1=PingResult( time=time, origin=origin, target=target, success=success, rtt=rtt)
    db.session.add(p1)
    db.session.commit()
    resp = app.make_response('posted!<br>' + str(p1))
    scheme = request.headers.get('X-Forwarded-Proto')
    if scheme is None:
        scheme = request.scheme
    resp.headers['Location'] = url_for('pings_get_id', id=p1.id, _scheme=scheme, _external=True)
    return resp
    # return 'posted!<br>' + str(p1)

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
    return '<!doctype html><html><body><a target="_blank" href="https://dashboard.heroku.com/apps/ping-store">manage app</a></body></html>'

if __name__ == '__main__':
    port = int(os.getenv("PORT"))
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=port)
