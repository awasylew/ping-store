from flask import Flask, request, url_for, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

import random
import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pings.db'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

@app.route('/makedb')
def make_database():
    """zainicjowanie schematu bazy danych (potrzebne szczególnie dla baz ulotnych, typowo w pamięci)"""
    db.create_all()
    return 'db created!', 200

@app.route('/sample-results')
def sample_results():
    """wstawienie przykładowych wyników ping (wartości losowe, czas bieżący)"""
    time=datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    for i in range(100):
        rtt = float(random.randrange(50))/10
        if rtt < 0.2:
            rtt = 0.0
        pings_post_generic({'origin':'sample-'+random.choice(['a', 'b', 'c']), \
            'target':'sample-'+random.choice(['1', '2', '3']), \
            'success':bool(rtt>0), 'rtt':rtt if rtt>0 else None, 'time':time})
    return 'posted!', 200

class PingResult(db.Model):
    __tablename__ = 'ping_results'

    id = Column(Integer, primary_key=True)
    time = Column(String)                   #YYYYmmddHHMMSS
    origin = Column(String)
    target = Column(String)
    success = Column(Boolean)
    rtt = Column(Integer)

    def __repr__(self):
        return "PingResult(id=%s, time=%s, origin=%s, target=%s, succes=%s, rtt=%s)" % \
            (self.id, self.time, self.origin, self.target, self.success, self.rtt)
    def toDict(self):                   # taka konwencja nazewnyczna zmiany typu na dict?
        return {'id':self.id, 'time':str(self.time), \
            'origin':str(self.origin), 'target':str(self.target), \
            'success':self.success, 'rtt':self.rtt}

def query_add_args_id(q):
    id=request.args.get('id')
    if id is not None:
        q = q.filter(PingResult.id == id)
    return q

def query_add_args_time(q):
    start=request.args.get('start')
    if start is not None:
        q = q.filter(PingResult.time >= start)
    end=request.args.get('end')
    if end is not None:
        q = q.filter(PingResult.time < end)
    prefix=request.args.get('time_prefix')
    if prefix is not None:
        q = q.filter(PingResult.time.like(prefix+'%'))
    return q

def query_add_args_hosts(q):
    origin=request.args.get('origin')
    if origin is not None:
        q = q.filter(PingResult.origin == origin)
    target=request.args.get('target')
    if target is not None:
        q = q.filter(PingResult.target == target)
    return q

def query_add_args_window(q):
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
    q = query_add_args_id(q)
    q = query_add_args_time(q)
    q = query_add_args_hosts(q)
    q = query_add_args_window(q)
    l = [i.toDict() for i in q]
    return jsonify(l), 200

@app.route('/pings/<int:id>', methods=['GET'])
def pings_get_id(id):
    q = db.session.query(PingResult).filter(PingResult.id==id)
    pr = q.first()
    if pr is None:
        return 'Not found', 404
    return jsonify(pr.toDict()), 200

def pings_post_generic(args):
    # args powinno być neutralnym słownikiem, a nie dopasowage do request!

    id = args.get('id')
	# dozwolony tutaj?
	# kontrole
	# błąd przy podaniu istniejącego
    time = args.get('time')
    # kontrola czy jest
    # kontrola czy poprawny
    # kontrola czy nie odrzucić z powodu starości
    origin = args.get('origin')
    # kontrole ...
    target = args.get('target')
    # kontrole ...
    success = args.get('success')
#    success = succ_arg is not None and succ_arg.upper() not in ['FALSE', '0']
#    print(success)
    # kontrole ...
    rtt = args.get('rtt')

    p = PingResult(id=id, time=time, origin=origin, target=target, success=success, rtt=rtt)
    db.session.add(p)
    db.session.commit()

    # resp = app.make_response(jsonify(p.toDict()))

    scheme = request.headers.get('X-Forwarded-Proto')       # metoda specyficzna na heroku, czy będzie dobrze działać w innych układach?
    if scheme is None:
        scheme = request.scheme

#    headers = {}
#    headers['Location'] = url_for('pings_get_id', id=p.id, _scheme=scheme, _external=True)
#    headers['Content-Type'] = 'application/json'      # niepotrzebne, bo jsonify już ustawia Content-Type

    return app.make_response((jsonify(p.toDict()), 201, \
        {'Location':  url_for('pings_get_id', id=p.id, _scheme=scheme, _external=True)}))

@app.route('/pings', methods=['POST'])
def pings_post():
    return pings_post_generic( request.json )

@app.route('/pings-post')    # do testów
def pings_post_pseudo():
#    args = {dict(request.args)}
    args = {k:request.args.get(k) for k in request.args}
#    print(args)
    succ_arg = args.get('success')
    success = succ_arg is not None and succ_arg.upper() not in ['FALSE', '0']
    args['success'] = success
    return pings_post_generic( args )

@app.route('/pings', methods=['DELETE'])
@app.route('/pings-delete') # do testów
def pings_delete():
    q = db.session.query(PingResult)
#    query_add_args(q).delete(synchronize_session=False)
    q = query_add_args_id(q)
    q = query_add_args_time(q)
    q = query_add_args_hosts(q)
#    q = query_add_args_window(q)
    q.delete(synchronize_session=False)
    db.session.commit()
    return 'deleted!', 204

@app.route('/origins')
def get_origins():
    q = db.session.query(PingResult.origin).distinct()
    q = query_add_args_id(q)
    q = query_add_args_time(q)
    q = query_add_args_hosts(q)
#    q = query_add_args_window(q)
#    l = [i[0] for i in q]
#    return jsonify(l), 200
    l = []
    for i in q:
        origin = i[0]
        links = []
#        links.append({'rel':'pings', 'href':url_for('pings_get', target=origin, _external=True)})
#        links.append({'rel':'minutes', 'href':url_for('get_minutes', target=origin, _external=True)})
#        links.append({'rel':'hours', 'href':url_for('get_hours', target=origin, _external=True)})
        links.append({'rel':'targets', 'href':url_for('get_targets', origin=origin,_external=True)})
        l.append({'origin':origin, 'links':links})
    return jsonify(l), 200

@app.route('/targets')
def get_targets():
    q = db.session.query(PingResult.origin, PingResult.target).distinct() # tak na sztywno czy wg argumentów?
    q = query_add_args_id(q)
    q = query_add_args_time(q)
    q = query_add_args_hosts(q)
#    q = query_add_args_window(q)
    l = []
    for i in q:
        origin = i[0]
        target = i[1]
        links = []
        links.append({'rel':'pings', 'href':url_for('pings_get', origin=origin, target=target, _external=True)})
        links.append({'rel':'minutes', 'href':url_for('get_minutes', origin=origin, target=target, _external=True)})
        links.append({'rel':'hours', 'href':url_for('get_hours', origin=origin, target=target, _external=True)})
        l.append({'target':target, 'links':links})
    return jsonify(l), 200
#    return "<br>".join([ str(r) for r in q]), 200

@app.route('/minutes')
def get_minutes():
    return get_periods('minute', 12)

@app.route('/hours')
def get_hours():
    return get_periods('hour', 10)

def get_periods( period_name, prefix_len ):
    q = db.session.query(PingResult.origin, PingResult.target, \
        func.substr(PingResult.time,1,prefix_len)).distinct()
    q = query_add_args_id(q)
    q = query_add_args_time(q)
    q = query_add_args_hosts(q)
    l = []
    for i in q:
        origin = i[0]
        target = i[1]
        prefix = i[2]
        count1 = query_add_args_id(query_add_args_hosts(query_add_args_time( \
            db.session.query(PingResult.origin)))).\
            filter(PingResult.time.like(prefix+'%'))
        count_all = count1.count()
        count_success = count1.filter(PingResult.success == True).count()
        l.append({'origin':origin, 'target':target, period_name:prefix, \
            'count':count_all, 'count_success':count_success,
            'links':[{'rel':'pings', 'href':url_for('pings_get', origin=origin, \
                target=target, time_prefix=prefix, _external=True)}]})
    return jsonify(l), 200

"""
@app.route('/hours')
def get_hours():
    q = db.session.query(func.substr(PingResult.time,1,10)).distinct()
    l = [i[0] for i in q]
    return jsonify(l), 200
"""

@app.route('/')
def root():
#    return '<!doctype html><html><body><a target="_blank" href="https://dashboard.heroku.com/apps/ping-store">manage app</a></body></html>'
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.getenv("PORT"))
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=port)
