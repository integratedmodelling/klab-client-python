import unittest

from klab.klab import *

# run with python3 -m unittest discover tests/

class TestKlabConnection(unittest.TestCase):
    
    def setUp(self):
        self.klabLocalDefault = Klab.createLocalDefault()

    def tearDown(self) -> None:
        if self.klabLocalDefault:
            self.assertTrue(self.klabLocalDefault.close())

    def test_local_connection(self):
        self.assertIsNotNone(self.klabLocalDefault)
        self.assertTrue(self.klabLocalDefault.isOnline())




if __name__ == "__main__":
    unittest.main()