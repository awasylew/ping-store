import ps1
import unittest

class make_database_testing(unittest.TestCase):

    def test_operation_works(self):
        print('hello1')
        ps1.make_database()
        print('hello2')

if __name__ == '__main__':
    unittest.main()
