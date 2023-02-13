import unittest
from unittest import TestCase, IsolatedAsyncioTestCase

from klab.klab import Klab
from klab.geometry import KlabGeometry, GeometryBuilder
from klab.observable import Observable, Range
import klab
import logging
import asyncio

TESTSLOGGER = logging.getLogger("klab-client-py-tests")

# run with python3 -m unittest discover tests/


class TestKlabConnection(IsolatedAsyncioTestCase):
    logging.basicConfig(format = '%(asctime)s|%(module)s|%(levelname)s: %(message)s',
                    datefmt = '%Y-%m-%d %H:%M:%S', level = logging.DEBUG)


    ruaha = "EPSG:4326 POLYGON((33.796 -7.086, 35.946 -7.086, 35.946 -9.41, 33.796 -9.41, 33.796 -7.086))"
    """A square piece of Tanzania"""

    geometryEncoding = "τ0(1){ttype=LOGICAL,period=[{TIME_PERIOD}],tscope=1.0,tunit=YEAR}S2({GRID_RESOLUTION_XY}){bbox=[{BOUNDING_BOX}],shape={WKB_SHAPE},proj=EPSG:4326}"
    """
    String with template variables; I assume a span of one year is OK and everything is in
    lat/lon projection (EPSG:4326)
    """

    timePeriod = "1640995200000 1672531200000"
    gridResolutionXY = "520,297"
    boundingBox = "-7.256596802202454 -4.408874148363334 38.39721372248553 40.02677860935444"
    wkbShape = "00000000030000000100000007C01D06C14FE6DEF24043B5F39D8BB550C0160A7B8B2DC6224044036D7B41B470C011A2AFE79D99FB4043B5C0443B5A7CC014D2EFCFADC624404355FA189A597CC0199C599EE6C5B8404332D7E635CC84C01C3D49F12A6BC440437995016B4E6CC01D06C14FE6DEF24043B5F39D8BB550"

    def setUp(self):
        self.klab = Klab.create()

    def tearDown(self) -> None:
        if self.klab:
            self.assertTrue(self.klab.close())

    def test_local_connection(self):
        self.assertIsNotNone(self.klab)
        self.assertTrue(self.klab.isOnline())

    def test_geometry_template(self):
        asyncio.run(self._test_geometry_template())
    
    async def _test_geometry_template(self):
        geometrySpecs = self.geometryEncoding.replace("{BOUNDING_BOX}", self.boundingBox).replace(
            "{TIME_PERIOD}", self.timePeriod).replace("{GRID_RESOLUTION_XY}", self.gridResolutionXY).replace("{WKB_SHAPE}", self.wkbShape)
        geometry = KlabGeometry.create(geometrySpecs)
        obs = Observable.create("earth:Region")
        
        contextTask = await self.klab.submit(obs, geometry)
        context = await contextTask.get()
        self.assertIsNotNone(context)

    def test_context_observation(self):
        asyncio.run(self._test_context_observation())

    async def _test_context_observation(self):
        # pass a semantic type and a geometry

        obs = Observable.create("earth:Region")
        grid = GeometryBuilder().grid(urn= self.ruaha, resolution= "1 km").years(2010).build()

        contextTask = await self.klab.submit(obs, grid)
        context = await contextTask.get()
        self.assertIsNotNone(context)

    def test_direct_observation(self):
        asyncio.run(self._test_direct_observation())

    async def _test_direct_observation(self):
        # pass a semantic type and a geometry + a quality to observe. The quality will be available
        # with the (obvious) name in the context
        obs = Observable.create("earth:Region")
        grid = GeometryBuilder().grid(urn= self.ruaha, resolution= "1 km").years(2010).build()
        obsElev = Observable.create("geography:Elevation")
        contextTask = await self.klab.submit(obs, grid, obsElev)
        context = await contextTask.get()

        self.assertIsNotNone(context)

        elevation = context.getObservation("elevation")
        self.assertIsNotNone(elevation)
        
        dataRange = elevation.getDataRange()
        r1 = Range(0, 3000)
        r2 = Range(500, 2500)

        self.assertTrue(r1.contains(dataRange))
        self.assertTrue(dataRange.contains(r2))

    def test_aggregated_results(self):
        asyncio.run(self._test_aggregated_results())

    async def _test_aggregated_results(self):
        obs = Observable.create("earth:Region")
        grid = GeometryBuilder().grid(urn= self.ruaha, resolution= "1 km").years(2010).build()
        obsElev = Observable.create("geography:Elevation")
        contextTask = await self.klab.submit(obs, grid, obsElev)
        context = await contextTask.get()

        self.assertIsNotNone(context)

        elevation = context.getObservation("elevation")
        self.assertIsNotNone(elevation)

        dataRange = elevation.getDataRange()
        r1 = Range(0, 3000)
        r2 = Range(500, 2500)

        self.assertTrue(r1.contains(dataRange))
        self.assertTrue(dataRange.contains(r2))

        aggregated = elevation.getAggregatedValue()
        scalar = elevation.getScalarValue()

        self.assertTrue(isinstance(aggregated, float))
        self.assertTrue(aggregated > 0)
        self.assertIsNone(scalar)

if __name__ == "__main__":
    unittest.main()
