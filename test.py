import ps1
import unittest

from ps1 import db    #  tak???
from ps1 import PingResult

class make_database_testing(unittest.TestCase):

    def xtest_operation_works(self):
        print('hello1')
        ps1.make_database()
        print('hello2')

    def test_get_pings(self):
        print('aaa')
        q = db.session.query(PingResult).all()
        print(q)

if __name__ == '__main__':
    unittest.main()
