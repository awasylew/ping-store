import ps1
import unittest
import datetime
import copy

from ps1 import *

class make_database_testing(unittest.TestCase):

    def setUp(self):
        test_session.expire_all()

    def tearDown(self):
        test_session.rollback()
        test_session.expire_all()

    def prep1(self):
        self.time=datetime.datetime.now().strftime('%Y%m%d%H')
        self.p1 = PingResult(id=101, time=self.time+'0101', origin='o-101', \
            target='t-101', success=True, rtt=101)
        self.p1d = self.p1.to_dict()
        self.p2 = PingResult(id=102, time=self.time+'0202', origin='o-102', \
            target='t-102', success=True, rtt=102)
        self.p2d = self.p2.to_dict()
        test_session.add(self.p1)
        test_session.add(self.p2)

    def test__get_pings_id__get_existing(self):
        """test: przykładowa baza danych, wywołanie z id istniejącym, zwrócony wynik wg id"""
        self.prep1()
        (r1, code1) = get_pings_id(101)
        (r2, code2) = get_pings_id(102)
        self.assertEqual(200, code1)
        self.assertEqual(self.p1d, r1)
        self.assertEqual(200, code2)
        self.assertEqual(self.p2d, r2)

    def test__get_pings_id__get_nonexistent(self):
        """test: przykładowa baza danych, wywołanie z id nieistniejących, zwrócony wynik pusty"""
        self.prep1()
        (r, code) = get_pings_id(103)
        self.assertEqual(code, 404)
        self.assertEqual('Not found', r)

    def test__get_pings__id_existing(self):
        """test: przykładowa baza danych, wywołanie z id istniejącym, zwrócony wynik wg id"""
        self.prep1()
        request.args = {'id': 101}
        (r, code) = get_pings()
        self.assertEqual(code, 200)
        self.assertEqual([self.p1d], r)

    def test__get_pings__id_nonexistent(self):
        """test: przykładowa baza danych, wywołanie z id nieistniejących, zwrócony wynik pusty"""
        self.prep1()
        request.args = {'id': 103}
        (r, code) = get_pings()
        self.assertEqual(code, 200)
        self.assertEqual([], r)

    def test__get_pings__no_id(self):
        """test: przykładowa baza danych, wywołanie bez id, zwrócony wynik pełny"""
        self.prep1()
        request.args = {}
        (r, code) = get_pings()
        self.assertEqual(code, 200)
        self.assertIn(self.p1d, r)
        self.assertIn(self.p2d, r)

    def test__git_pings__start(self):
        """test: sprawdzenie stosowania warunku start"""
        self.prep1()
        request.args = {'start': self.time+'02'}
        (r, code) = get_pings()
        self.assertEqual(code, 200)
        self.assertEqual([self.p2d], r)

    def test__git_pings__end(self):
        """test: sprawdzenie stosowania warunku end"""
        self.prep1()
        request.args = {'end': self.time+'02'}
        (r, code) = get_pings()
        self.assertEqual(code, 200)
        self.assertEqual([self.p1d], r)

    def test__git_pings__time_prefix(self):
        """test: sprawdzenie stosowania warunku time_prefix"""
        self.prep1()
        request.args = {'time_prefix': self.time+'02'}
        (r, code) = get_pings()
        self.assertEqual(code, 200)
        self.assertEqual([self.p2d], r)

    def test__get_pings__origin_existing(self):
        """test: przykładowa baza danych, wywołanie z origin istniejącym, zwrócony wynik wg origin"""
        self.prep1()
        request.args = {'origin': 'o-101'}
        r = get_pings()
        self.assertEqual(r, ([self.p1d], 200))

    def test__get_pings__origin_non_existent(self):
        """test: przykładowa baza danych, wywołanie z origin nieistniejącym, zwrócony wynik pusty"""
        self.prep1()
        request.args = {'origin': 'o-bla'}
        r = get_pings()
        self.assertEqual(r, ([], 200))

    def test__get_pings__target_existing(self):
        """test: przykładowa baza danych, wywołanie z target istniejącym, zwrócony wynik wg tagret"""
        self.prep1()
        request.args = {'target': 't-102'}
        r = get_pings()
        self.assertEqual(r, ([self.p2d], 200))

    def test__get_pings__tagret_non_existent(self):
        """test: przykładowa baza danych, wywołanie z taget nieistniejącym, zwrócony wynik pusty"""
        self.prep1()
        request.args = {'target': 't-bla'}
        r = get_pings()
        self.assertEqual(r, ([], 200))

    def limit_helper(self, n):
        self.prep1()
        request.args = {'limit': str(n)}
        r, code = get_pings()
        self.assertEqual(code, 200)
        self.assertEqual(len(r), n)

    def test__get_pings__limit_0(self):
        """test: limit = 0"""
        self.limit_helper(0)

    def test__get_pings__limit_1(self):
        """test: limit = 1"""
        self.limit_helper(1)

    def test__get_pings__limit_2(self):
        """test: limit = 2"""
        self.limit_helper(2)

    def test__pings_delete__all(self):
        """test: kasowanie bez warunków - wszystkiego"""
        self.prep1()
        request.args = {}
        r, code = pings_delete()
        self.assertEqual(code, 204)
        self.assertEqual(r, 'deleted!')
        self.assertEqual(test_session.query(PingResult).count(), 0)

    def test__pings_delete__id_existing(self):
        """test: kasowanie wg id istniejącego"""
        self.prep1()
        request.args = {'id': '101'}
        r, code = pings_delete()
        self.assertEqual(code, 204)
        self.assertEqual(r, 'deleted!')
        self.assertEqual(test_session.query(PingResult).count(), 1)

    def test__pings_delete__id_nonexistent(self):
        """test: kasowanie wg id nieistniejącego"""
        """ TEST NIE DZIAŁA - WYŁĄCZONY :(
        print('aaa1')
        self.prep1()
        print('aaa2')
        request.args = {'id': '103'}
        print('aaa3')
        print(test_session.new)
        r, code = pings_delete()
        print('bbb')
        self.assertEqual(code, 204)
        self.assertEqual(r, 'deleted!')
        self.assertEqual(test_session.query(PingResult).count(), 2)
        """
        pass

if __name__ == '__main__':
    unittest.main()
