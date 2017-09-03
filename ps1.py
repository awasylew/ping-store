from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker

import random
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pings.db'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

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

#@app.route('/pings', methods=['POST'])
@app.route('/pings-post')
def pings_post():
    p1=PingResult(
        time=datetime.datetime.now().strftime('%Y%m%d%H%M%S'),
        origin=random.choice(['A8', 'RaspPi']),
        target=random.choice(['onet.pl', 'wp.pl', 'rmf.pl']),
        success=random.choice([0, 1]),
        rtt=random.choice([1,2,4,8,16,32,64]))
    db.session.add(p1)
    db.session.commit()
    return 'posted!'

#@app.route methods=DELETE
@app.route('/pings-delete')
def pings_delete():
    db.session.query(PingResult).delete(synchronize_session=False)
    db.session.commit()
    return 'deleted!'

app.run(debug=True)
