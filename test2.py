import datetime
import requests

base = 'https://ping-store.herokuapp.com'

def prep1():
    d = requests.delete(base+'/pings')
    print(d)

    time=datetime.datetime.now().strftime('%Y%m%d%H')
    # self.p1 = PingResult(id=101, time=self.time+'0101', origin='o-101', target='t-101', success=True, rtt=101)
    global p1
    p1 = { 'id':101, 'time':f'{time}', 'origin':'o-101', 'target':'t-101', 'success':'true', 'rtt':101.01}
    print(p1)
    p = requests.post(base+'/pings', data=p1, headers={'Content-type':'application/json'})
    print(p)

    # self.p1d = self.p1.to_dict()
    # self.p2 = PingResult(id=102, time=self.time+'0202', origin='o-102', target='t-102', success=True, rtt=102)
    # self.p2d = self.p2.to_dict()
    # test_session.add(self.p1)
    # test_session.add(self.p2)

def test__get_pings_id__existing():
    """test: przykładowa baza danych, wywołanie z id istniejącym, zwrócony wynik wg id"""
    # self.prep1()
    prep1()

    # r1 = get_pings_id(101)
    r = requests.get(base+'/pings/101')
    # self.assertEqual(r1, self.p1)
    print(r.text)
    p = r.json()
    print(p)
    global p1
    assert(p==p1)

    # r2 = get_pings_id(102)
    # self.assertEqual(r2, self.p2)

print('hello!')
test__get_pings_id__existing()
