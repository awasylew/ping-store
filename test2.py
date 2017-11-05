import datetime
import requests
import json
import unittest

from store import *

# ta konfiguracja też ze środowiska?
# base = 'https://ping-store.herokuapp.com'
base = 'http://localhost:5000'

class test1(unittest.TestCase):

    def prep0(self):
        """przygotowanie: pusta baza danych"""
        test_session.query(PingResult).delete()
        test_session.commit()

    def prep1(self):
        """przygotowanie: baza danych z dwoma wpisami testowymi"""
        test_session.query(PingResult).delete()
        test_session.commit()
        self.time=datetime.datetime.now().strftime('%Y%m%d%H')
        p1 = PingResult(id=101, time=self.time+'0101', origin='o-101', \
            target='t-101', success=True, rtt=101.01)
        p2 = PingResult(id=102, time=self.time+'0202', origin='o-102', \
            target='t-102', success=True, rtt=102.02)
        test_session.add(p1)
        test_session.add(p2)
        test_session.commit()
        self.p1 = p1.to_dict()
        self.p2 = p2.to_dict()

    def test__get_pings_id__existing(self):
        """test: przykładowa baza danych, wywołanie z id istniejącym, zwrócony wynik wg id"""
        self.prep1()

        r = requests.get(base+'/pings/101')
        # czy używać tu url_for?

        p = r.json()
        self.assertEqual(p, self.p1)
        r = requests.get(base+'/pings/102')
        p = r.json()
        self.assertEqual(p, self.p2)
        print('OK')

    def test__get_pings_id__nonexistent(self):
        """test: przykładowa baza danych, wywołanie z id nieistniejących, zwrócony wynik pusty"""
        self.prep1()
        r = requests.get(base+'/pings/103')
        self.assertEqual(r.status_code, 404)
        print('OK')

    def test__get_pings__id_existing(self):
        """test: przykładowa baza danych, wywołanie z id istniejącym, zwrócony wynik wg id"""
        self.prep1()
        r = requests.get(base+'/pings?id=101')
        self.assertEqual(r.json(), [self.p1])
        print('OK')

    def test__get_pings__no_id(self):
        """test: przykładowa baza danych, wywołanie bez id, zwrócony wynik pełny"""
        self.prep1()
        # request.args = {}
        # r = get_pings()
        r = requests.get(base+'/pings')
        self.assertIn(self.p1, r.json())
        self.assertIn(self.p2, r.json())
        print('OK')

    def test__git_pings__start(self):
        """test: sprawdzenie stosowania warunku start"""
        self.prep1()
        r = requests.get(base+'/pings?start='+self.time+'02')
        self.assertEqual(r.json(), [self.p2])
        print('OK')

    def test__git_pings__end(self):
        """test: sprawdzenie stosowania warunku end"""
        self.prep1()
        r = requests.get(base+'/pings?end='+self.time+'02')
        self.assertEqual(r.json(), [self.p1])
        print('OK')

    def test__git_pings__time_prefix(self):
        """test: sprawdzenie stosowania warunku time_prefix"""
        self.prep1()
        r = requests.get(base+'/pings?time_prefix='+self.time+'02')
        self.assertEqual(r.json(), [self.p2])
        print('OK')

    def test__get_pings__origin_existing(self):
        """test: przykładowa baza danych, wywołanie z origin istniejącym, zwrócony wynik wg origin"""
        self.prep1()
        r = requests.get(base+'/pings?origin=o-101')
        self.assertEqual(r.json(), [self.p1])
        print('OK')

    def test__get_pings__origin_non_existent(self):
        """test: przykładowa baza danych, wywołanie z origin nieistniejącym, zwrócony wynik pusty"""
        self.prep1()
        r = requests.get(base+'/pings?origin=o-bla')
        self.assertEqual(r.json(), [])
        print('OK')

    def test__get_pings__target_existing(self):
        """test: przykładowa baza danych, wywołanie z target istniejącym, zwrócony wynik wg tagret"""
        self.prep1()
        r = requests.get(base+'/pings?target=t-102')
        self.assertEqual(r.json(), [self.p2])
        print('OK')

    def test__get_pings__tagret_non_existent(self):
        """test: przykładowa baza danych, wywołanie z taget nieistniejącym, zwrócony wynik pusty"""
        self.prep1()
        r = requests.get(base+'/pings?target=t-bla')
        self.assertEqual(r.json(), [])
        print('OK')

    def limit_helper(self, n):
        self.prep1()
        r = requests.get(base+'/pings?limit='+str(n))
        self.assertEqual(len(r.json()), n)
        print('OK')

    def test__get_pings__limit_0(self):
        """test: limit = 0"""
        self.limit_helper(0)

    def test__get_pings__limit_1(self):
        """test: limit = 1"""
        self.limit_helper(1)

    def test__get_pings__limit_2(self):
        """test: limit = 2"""
        self.limit_helper(2)

    def test__post_pings__time_now(self):
        """test: time=now"""
        self.prep0()
        time = datetime.datetime.now()
        payload = json.dumps({'origin':'o-p1', 'target':'t-p1', 'success':True, 'rtt':34.56, 'time':'now'})
        h = {'Content-type': 'application/json'}
        r = requests.post(base+'/pings', data=payload, headers=h)
        pr = test_session.query(PingResult).one()
        print(pr)
        print(pr.to_dict())
        print(time)
        time2 = time + datetime.timedelta(minutes=1)
        print(time2)
        times = time.strftime('%Y%m%d%H%M%S')
        time2s = time2.strftime('%Y%m%d%H%M%S')
        print(times)
        print(time2s)
        print(pr.time)
        self.assertLessEqual(times, pr.time)
        self.assertLessEqual(pr.time, time2s)

print('Starting testing session...')
t = test1()

""" chwilowo wyłączone
t.test__get_pings_id__existing()
t.test__get_pings_id__nonexistent()
t.test__get_pings__id_existing()
t.test__get_pings__no_id()
t.test__git_pings__start()
t.test__git_pings__end()
t.test__git_pings__time_prefix()
t.test__get_pings__origin_existing()
t.test__get_pings__origin_non_existent()
t.test__get_pings__target_existing()
t.test__get_pings__tagret_non_existent()
t.test__get_pings__limit_0()
t.test__get_pings__limit_1()
t.test__get_pings__limit_2()
"""
t.test__post_pings__time_now()

# wywołanie wszystkich testów z unittest zamiast ręcznego? (ale długo będzie trwać)
