import datetime
import requests
import json
import unittest

# ta konfiguracja też ze środowiska?
# base = 'https://ping-store.herokuapp.com'
base = 'http://localhost:5000'

class test1(unittest.TestCase):
    def prep1(self):
        print('prep1()')
        d = requests.delete(base+'/pings')
        time=datetime.datetime.now().strftime('%Y%m%d%H')
        self.p1 = { 'id':101, 'time':time+'0101', 'origin':'o-101', 'target':'t-101', 'success':True, 'rtt':101.01}
        p = requests.post(base+'/pings', data=json.dumps(self.p1), headers={'Content-type':'application/json'})
        self.p2 = { 'id':102, 'time':time+'0202', 'origin':'o-102', 'target':'t-102', 'success':True, 'rtt':102.02}
        p = requests.post(base+'/pings', data=json.dumps(self.p2), headers={'Content-type':'application/json'})

    def test__get_pings_id__existing(self):
        """test: przykładowa baza danych, wywołanie z id istniejącym, zwrócony wynik wg id"""
        self.prep1()

        r = requests.get(base+'/pings/101')
        p = r.json()
        self.assertEqual(p, self.p1)

        r = requests.get(base+'/pings/102')
        p = r.json()
        self.assertEqual(p, self.p2)

        print('OK test__get_pings_id__existing')

print('hello!')
t = test1()
t.test__get_pings_id__existing()
t.test__get_pings_id__existing()
# wywołanie wszystkich testów z unittest zamiast ręcznego? (ale długo będzie trwać)
