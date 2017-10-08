import ps1
import unittest
import datetime
import copy

from ps1 import PingResult
# from ps1 import db    #
from ps1 import session

class make_database_testing(unittest.TestCase):

    def setUp(self):
        print('\n\n   --- setup')

    def tearDown(self):
        print('\n\n   --- teardown')
        session.rollback()

    def xtest_operation_works(self):
        print('hello1')
        # ps1.make_database()
        print('hello2')

    def test_get_pings(self):
        print('\n\n   --- get pings')
        q = session.query(PingResult).all()
        print(q)

    def test__get_pings__get_by_existing_id(self):
        print('\n\n   --- by existing id')
        time=datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        p = PingResult(time=time, origin='o-1', target='t-a', \
            success=True, rtt=10)
        session.add(copy.copy(p))
        r = session.query(PingResult).one()
        print('p: ', p)
        print('q: ', r)
        print(p is r)

if __name__ == '__main__':
    unittest.main()
