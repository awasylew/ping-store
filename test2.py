import datetime
import requests
import json
import unittest

from store import *

# ta konfiguracja też ze środowiska?
# base = 'https://ping-store.herokuapp.com'
base = 'http://localhost:5000'

class test1(unittest.TestCase):
    def prep1(self):
        self.time=datetime.datetime.now().strftime('%Y%m%d%H')
        self.p1 = { 'id':101, 'time':self.time+'0101', 'origin':'o-101', 'target':'t-101', 'success':True, 'rtt':101.01}
        self.p2 = { 'id':102, 'time':self.time+'0202', 'origin':'o-102', 'target':'t-102', 'success':True, 'rtt':102.02}
        self.prep2()
        return
        d = requests.delete(base+'/pings')
        self.time=datetime.datetime.now().strftime('%Y%m%d%H')
        self.p1 = { 'id':101, 'time':self.time+'0101', 'origin':'o-101', 'target':'t-101', 'success':True, 'rtt':101.01}
        p = requests.post(base+'/pings', data=json.dumps(self.p1), headers={'Content-type':'application/json'})
        self.p2 = { 'id':102, 'time':self.time+'0202', 'origin':'o-102', 'target':'t-102', 'success':True, 'rtt':102.02}
        p = requests.post(base+'/pings', data=json.dumps(self.p2), headers={'Content-type':'application/json'})

    def prep2(self):
        test_session.query(PingResult).delete()
        #self.time=datetime.datetime.now().strftime('%Y%m%d%H')
        p1 = PingResult(id=101, time=self.time+'0101', origin='o-101', \
            target='t-101', success=True, rtt=101)
        #self.p1d = self.p1.to_dict()
        p2 = PingResult(id=102, time=self.time+'0202', origin='o-102', \
            target='t-102', success=True, rtt=102)
        #self.p2d = self.p2.to_dict()
        test_session.add(p1)
        test_session.add(p2)
        # print(test_session.query(PingResult).all())


    def test__get_pings_id__existing(self):
        """test: przykładowa baza danych, wywołanie z id istniejącym, zwrócony wynik wg id"""
        self.prep1()
        r = requests.get(base+'/pings/101')
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



print('hello!')
t = test1()
t.test__get_pings_id__existing()
t.test__get_pings_id__nonexistent()
t.test__get_pings__id_existing()
t.test__get_pings__no_id()
t.test__git_pings__start()
t.test__git_pings__end()
t.test__git_pings__time_prefix()
# wywołanie wszystkich testów z unittest zamiast ręcznego? (ale długo będzie trwać)
