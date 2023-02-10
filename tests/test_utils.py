import unittest

from klab.utils import ExportFormat, Export

# run with python3 -m unittest discover tests/


class TestUtilsAndMinors(unittest.TestCase):

    def test_exports(self):
       self.assertEqual(ExportFormat.PNG_IMAGE.getMediaType(), "image/png")
       self.assertTrue(ExportFormat.PNG_IMAGE.isExportAllowed(Export.LEGEND))
       self.assertFalse(ExportFormat.PNG_IMAGE.isExportAllowed(Export.STRUCTURE))
       self.assertFalse(ExportFormat.PNG_IMAGE.isText())
       self.assertTrue(ExportFormat.JSON_CODE.isText())