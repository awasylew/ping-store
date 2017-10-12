from flask import Flask, request, url_for, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

import random
import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pings.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

from testprep import aw_testing
if aw_testing:
    Base = declarative_base()
    def pseudo_jsonify(x): return x    # usunąć jeśli już potrzebne
    jsonify = pseudo_jsonify
    class Dummy: pass
    request = Dummy()
else:
    db = SQLAlchemy(app)
    Base = db.Model

class PingResult(Base):
    """główna treść bazy danych ping - wynik pojedynczego wywołania"""

    __tablename__ = 'ping_results'

    id = Column(Integer, primary_key=True)
    time = Column(String)                   #YYYYmmddHHMMSS
    origin = Column(String)
    target = Column(String)
    success = Column(Boolean)
    rtt = Column(Float)

    def __repr__(self):
        return "PingResult(id=%s, time=%s, origin=%s, target=%s, succes=%s, rtt=%s)" % \
            (self.id, self.time, self.origin, self.target, self.success, self.rtt)
    def to_dict(self):
        return {'id':self.id, 'time':str(self.time), \
            'origin':str(self.origin), 'target':str(self.target), \
            'success':self.success, 'rtt':self.rtt}

if aw_testing:
    engine = create_engine('sqlite:///:memory:', echo=False)
    # engine = create_engine('sqlite:///:memory:', echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    test_session = Session()
    db = Dummy()
    db.session = test_session
else:
    pass

@app.route('/makedb')
def make_database():
    """zainicjowanie schematu bazy danych (potrzebne szczególnie dla baz ulotnych, typowo w pamięci)"""
    """test: na razie bez testowania, bo zbyt pokręcone mockowanie"""
    """test: brak bazy, operacja bazodanowa powoduje błąd"""
    """test: brak bazy, make_database(), operacja bazodanowa się udaje"""
    db.create_all()
    return 'db created!', 200

@app.route('/sample-results')
def sample_results():
    """wstawienie przykładowych wyników ping (wartości losowe, czas bieżący)"""
    """bez testowania, bo to metoda nieprodukcyjna"""
    time=datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    for i in range(100):
        rtt = float(random.randrange(50))/10
        if rtt < 0.2:
            rtt = 0.0
        # dlaczego tutaj używamy post zamiast session.add?
        pings_post_generic({'origin':'sample-'+random.choice(['a', 'b', 'c']), \
            'target':'sample-'+random.choice(['1', '2', '3']), \
            'success':bool(rtt>0), 'rtt':rtt if rtt>0 else None, 'time':time})
    return 'posted!', 200

# lepsza organizacja query_add_args_*: jedne procedura ze wskazaniem, które części uwzględniać bool, z jakimś default?"""
def query_add_args_id(q):
    """dodanie do zapytania SQLAlchemy warunku na id jeśli występuje w parametrach wywołania HTTP"""
    """testy --> get_pings"""
    id = request.args.get('id')
    if id is not None:
        q = q.filter(PingResult.id==id)
    return q

def query_add_args_time(q):
    """dodanie do zapytania SQLAlchemy warunków czasowych jeśli występują w parametrach wywołania HTTP"""
    """testy --> get_pings"""
    start = request.args.get('start')
    if start is not None:
        q = q.filter(PingResult.time>=start)
    end = request.args.get('end')
    if end is not None:
        q = q.filter(PingResult.time<end)
    prefix = request.args.get('time_prefix')
    if prefix is not None:
        q = q.filter(PingResult.time.like(prefix+'%'))
    return q

def query_add_args_hosts(q):
    """dodanie do zapytania SQLAlchemy warunków dotyczących hostów jeśli występują w parametrach wywołania HTTP"""
    """testy --> get_pings"""
    origin = request.args.get('origin')
    if origin is not None:
        q = q.filter(PingResult.origin==origin)
    target = request.args.get('target')
    if target is not None:
        q = q.filter(PingResult.target==target)
    return q

def query_add_args_window(q):
    """dodanie do zapytania SQLAlchemy warunków ograniczająych liczbę wyników jeśli występują w parametrach wywołania HTTP"""
    """testy limit --> get_pings"""
    """test: offset??? jak to zrobić bez gwarantowanej kolejności?"""
    limit = request.args.get('limit')
    if limit is not None:
        q = q.limit(limit)
    offset = request.args.get('offset')
    if offset is not None:
        q = q.offset(offset)
    return q

def get_pings2():
    # a powinien zwracać obiekty czy już słowniki?
    """zwrócenie listy wyników ping ograniczonych parametrami wywołania HTTP"""
    """test: dorobic jeszcze offset, ale najpierw sortowanie?"""
    q = db.session.query(PingResult)
    q = query_add_args_id(q)
    q = query_add_args_time(q)
    q = query_add_args_hosts(q)
    q = query_add_args_window(q)
    # jakies sortowanie?
    return q.all()
    # return [i.to_dict() for i in q]

def get_pings():
    return [i.to_dict() for i in get_pings2()]

@app.route('/pings')
def get_pings_view():
    return jsonify(get_pings()), 200

def get_pings_id(id):
    """zwrócenie pojedynczego wyniku wg id"""
    q = db.session.query(PingResult).filter(PingResult.id==id)
    return q.first()

@app.route('/pings/<int:id>')
def get_pings_id_view(id):
    """pojedynczy wyniku wg id w ścieżce"""
    r = get_pings_id(id)
    if r is None:
        return 'Not found', 404
    return jsonify(r.to_dict()), 200

def pings_post_generic(args):
    """wstawienie pojedynczego pinga do bazy danych"""
    """test: pusta baza, wstawienie, w bazie dokładnie ten jeden"""
    """test: dwukrotne wstawione z tym samym id -> błąd"""
    """test: pusta baza, wstawienie, ponowne wstawienie (dokładnie taki sam czy zmieniony?), w bazie dokładnie jeden"""
    """test: różne wersje niepoprawnych argumentów z listy przykładowych"""
    # args powinno być neutralnym słownikiem, a nie dopasowane do request!
    # a może nie słownik, tylko zwykłe parametry wywołania?
    # dodać testy na sprawdzenia parametrów
    # jak już jeden, to nazwa generic średnia

    id = args.get('id')
	# dozwolony tutaj?
	# kontrole
	# błąd przy podaniu istniejącego?

    time = args.get('time')
    # kontrola czy jest
    # kontrola czy poprawny
    # kontrola czy nie odrzucić z powodu starości

    origin = args.get('origin')
    # kontrole ...

    target = args.get('target')
    # kontrole ...

    success = args.get('success')
    # kontrole ...

    rtt = args.get('rtt')
    # kontrole

    p = PingResult(id=id, time=time, origin=origin, target=target, \
        success=success, rtt=rtt)
    db.session.add(p)
    db.session.commit()
    # czy nie powinno być zabezpieczenia przed podwójnym wstawieniem tego samego?
    # np. wg klucza na origin+target+time?
    # cel: idempotentność przy ponowieniu wstawiania

    # wydzielić fragment ustalający scheme albo Location do oddzielnej procedury
    # i wtedy własne testy jednostkowe
    scheme = request.headers.get('X-Forwarded-Proto')       # metoda specyficzna na heroku, czy będzie dobrze działać w innych układach?
    if scheme is None:
        scheme = request.scheme

    return app.make_response((jsonify(p.to_dict()), 201, \
        {'Location':  url_for('get_pings_id_view', id=p.id, _scheme=scheme, _external=True)}))

@app.route('/pings', methods=['POST'])
def pings_post():
    """wstawienie pojedynczego pinga metodą POST"""
    """test: sprawdzenie, że parametry dobrze przechodzą przez treść POSTa???"""
    return pings_post_generic(request.json)

@app.route('/pings-post')    # do testów, !!! ping-probe umie nma razie tylko GET
def pings_post_pseudo():
    # zmienić nazwę na pseude_post_pings
    args = {k:request.args.get(k) for k in request.args}
    succ_arg = args.get('success')
    success = succ_arg is not None and succ_arg.upper() not in ['FALSE', '0']
    args['success'] = success
    return pings_post_generic(args)

@app.route('/pings', methods=['DELETE'])
def pings_delete():
    # zmienić nazwę na delete_pings
    """usuwanie wpisów wg zadanych kryteriów"""
    """test: przykładowa baza, kilka ręcznie przygotowanych warunków, sprawdzanie liczności wyniku po usunięciu"""
    """test: j.w. tylko z warunkami"""
    q = db.session.query(PingResult)
    q = query_add_args_id(q)
    q = query_add_args_time(q)
    q = query_add_args_hosts(q)
    q.delete(synchronize_session=False)
    db.session.commit()
    return 'deleted!', 204

@app.route('/origins')
def get_origins():
    """listuje wszystkie origins do wyboru"""
    """test: pusta baza, kilka wstawień, sprawdzenie wyniku na zgodność"""
    """test: j.w. tylko z warunkami"""
    q = db.session.query(PingResult.origin).distinct()
    # jakieś sortowanie?
    q = query_add_args_time(q)
    q = query_add_args_hosts(q)
    q = query_add_args_window(q)
    l = []
    for i in q:
        origin = i[0]     # i.origin?
        links = [{'rel':'targets', 'href':url_for('get_targets', origin=origin, _external=True)}]
            # url_for nie potrzebuje zabazy w scheme?
        l.append({'origin':origin, 'links':links})
    return jsonify(l), 200

@app.route('/targets')      # zmienić nazwę, bo jednak inna funkcja? routes? paths?
def get_targets():
    """listuje możliwe przejścia od origin do target"""
    """test: pusta baza, kilka wstawień, sprawdzenie wyniku na zgodność"""
    """test: j.w. tylko z warunkami"""
    q = db.session.query(PingResult.origin, PingResult.target).distinct() # tak na sztywno czy wg argumentów?
    q = query_add_args_time(q)
    q = query_add_args_hosts(q)
    q = query_add_args_window(q)
    l = []
    for i in q:
        origin = i[0]       # i.origin?
        target = i[1]       # i.target?
        links = []
        links.append({'rel':'pings', 'href':url_for('get_pings_view', origin=origin, target=target, _external=True)})
        links.append({'rel':'minutes', 'href':url_for('get_minutes', origin=origin, target=target, _external=True)})
        links.append({'rel':'hours', 'href':url_for('get_hours', origin=origin, target=target, _external=True)})
        l.append({'target':target, 'links':links})
    return jsonify(l), 200

@app.route('/minutes')
def get_minutes():
    """..."""
    """test: ..."""
    return get_periods('minute', 12)

@app.route('/hours')
def get_hours():
    """..."""
    """test: ..."""
    return get_periods('hour', 10)

def get_periods( period_name, prefix_len ):
    """wyciąga zagregowane wyniki dla wybranego okresu (leksykograficznie)"""
    """test:..."""
    q = db.session.query(PingResult.origin, PingResult.target, \
        func.substr(PingResult.time,1,prefix_len),
        func.min(PingResult.rtt), func.avg(PingResult.rtt), func.max(PingResult.rtt))
    q = query_add_args_time(q)
    q = query_add_args_hosts(q)
    q = q.group_by( PingResult.origin, PingResult.target, \
        func.substr(PingResult.time,1,prefix_len))
    # czy powinno być offset/limit? czy to ma zastosowanie do GROUP BY?
    l = []
    for i in q:
        origin = i[0]   # może da się ładniej .label?   albo i.origin
        target = i[1]
        prefix = i[2]
        min_rtt = i[3]
        avg_rtt = i[4]
        max_rtt = i[5]
        count1 = query_add_args_hosts(query_add_args_time( \
            db.session.query(PingResult.origin))).\
            filter(PingResult.time.like(prefix+'%'))
        count_all = count1.count()
        count_success = count1.filter(PingResult.success == True).count()
        # może po zmianie z distinct na group by w głównym zapytaniu da się zrezygnować z zapytań zagnieżdżonych?
        l.append({'origin':origin, 'target':target, period_name:prefix, \
            'count':count_all, 'count_success':count_success, \
            'avg_rtt': avg_rtt, 'min_rtt': min_rtt, 'max_rtt': max_rtt, \
            'links':[{'rel':'pings', 'href':url_for('get_pings_view', origin=origin, \
                target=target, time_prefix=prefix, _external=True)}]})
    return jsonify(l), 200

@app.route('/')
def root():
    """strona pomocnicza"""
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.getenv("PORT"))
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=port)
