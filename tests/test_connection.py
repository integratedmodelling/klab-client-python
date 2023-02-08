import unittest

from klab.klab import *

# run with python3 -m unittest discover tests/

class TestKlabConnection(unittest.TestCase):
    
    def setUp(self):
        self.klab = Klab.create()

    def tearDown(self) -> None:
        if self.klab:
            self.assertTrue(self.klab.close())

    def test_local_connection(self):
        self.assertIsNotNone(self.klab)
        self.assertTrue(self.klab.isOnline())




if __name__ == "__main__":
    unittest.main()