import ps1
import unittest
import datetime
import copy

from ps1 import *
# from ps1 import db    #
#from ps1 import session

def pseudo_jsonify(x):
    return x

class make_database_testing(unittest.TestCase):

    def setUp(self):
        print('\n\n   --- setup')
        # Flask.jsonify = pseudo_jsonify

    def tearDown(self):
        print('\n\n   --- teardown')
        session.rollback()

    def xtest_operation_works(self):
        print('hello1')
        # ps1.make_database()
        print('hello2')

    def xtest_get_pings(self):
        print('\n\n   --- get pings')
        q = session.query(PingResult).all()
        print(q)

    def test__get_pings_id__xxx(self):
        print('\n\n   --- by existing id')
        time=datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        p1 = PingResult(id=101, time=time, origin='o-101', target='t-101', \
            success=True, rtt=101)
        p1d = p1.to_dict()
        p2 = PingResult(id=102, time=time, origin='o-102', target='t-102', \
            success=True, rtt=102)
        p2d = p2.to_dict()
        session.add(p1)
        session.add(p2)
        r1 = get_pings_id(101)
        r2 = get_pings_id(102)
        r3 = get_pings_id(103)
        self.assertEqual(r1, (p1d, 200))
        self.assertEqual(r2, (p2d, 200))
        self.assertEqual(r3, ('Not found', 404))

if __name__ == '__main__':
    unittest.main()
