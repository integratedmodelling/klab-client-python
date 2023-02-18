import unittest
from unittest import TestCase, IsolatedAsyncioTestCase

from klab.klab import Klab
from klab.geometry import KlabGeometry, GeometryBuilder
from klab.observable import Observable, Range
from klab.observation import Observation
from klab.exceptions import *
from klab.utils import Export, ExportFormat
import klab
import logging
import asyncio
import tempfile
import os
from zipfile import ZipFile

TESTSLOGGER = logging.getLogger("klab-client-py-tests")

# run with python3 -m unittest discover tests/



class BaseTestClass():
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
        
        ticketHandler = self.klab.submit(obs, geometry)
        context = await ticketHandler.get()
        self.assertIsNotNone(context)

    def test_context_observation(self):
        asyncio.run(self._test_context_observation())

    async def _test_context_observation(self):
        # pass a semantic type and a geometry

        obs = Observable.create("earth:Region")
        grid = GeometryBuilder().grid(urn= self.ruaha, resolution= "1 km").years(2010).build()

        ticketHandler = self.klab.submit(obs, grid)
        context = await ticketHandler.get()
        self.assertIsNotNone(context)

    def test_direct_observation(self):
        asyncio.run(self._test_direct_observation())

    async def _test_direct_observation(self):
        # pass a semantic type and a geometry + a quality to observe. The quality will be available
        # with the (obvious) name in the context
        obs = Observable.create("earth:Region")
        grid = GeometryBuilder().grid(urn= self.ruaha, resolution= "1 km").years(2010).build()
        obsElev = Observable.create("geography:Elevation")
        ticketHandler = self.klab.submit(obs, grid, obsElev)
        context = await ticketHandler.get()

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
        ticketHandler = self.klab.submit(obs, grid, obsElev)
        context = await ticketHandler.get()

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

    def test_categories(self):
        asyncio.run(self._test_categories())

    async def _test_categories(self):
        obs = Observable.create("earth:Region")
        grid = GeometryBuilder().grid(urn= self.ruaha, resolution= "1 km").years(2010).build()
        obsElev = Observable.create("landcover:LandCoverType").named("landcover")
  
        ticketHandler = self.klab.submit(obs, grid, obsElev)
        context = await ticketHandler.get()
        self.assertIsNotNone(context)

        landcover = context.getObservation("landcover")
        self.assertIsNotNone(landcover)

    def test_spatial_vector_objects(self):
        asyncio.run(self._test_spatial_vector_objects())

    async def _test_spatial_vector_objects(self):
        obs = Observable.create("earth:Region")
        grid = GeometryBuilder().grid(urn= self.ruaha, resolution= "1 km").years(2010).build()
        ticketHandler = self.klab.submit(obs, grid)
        context = await ticketHandler.get()
        self.assertIsNotNone(context)

        ticketHandler = context.submit(Observable.create("infrastructure:Town"))
        towns = await ticketHandler.get()
        self.assertTrue(isinstance(towns, Observation))

        didit = towns.exportToString(Export.DATA, ExportFormat.GEOJSON_FEATURES)
        self.assertTrue(didit)

    def test_spatial_raster_objects(self):
        asyncio.run(self._test_spatial_raster_objects())

    async def _test_spatial_raster_objects(self):
        obs = Observable.create("earth:Region")
        grid = GeometryBuilder().grid(urn= self.ruaha, resolution= "1 km").years(2010).build()
        ticketHandler = self.klab.submit(obs, grid)
        context = await ticketHandler.get()

        self.assertIsNotNone(context)

        obsElev = Observable.create("geography:Elevation")
        ticketHandler = context.submit(obsElev)
        elevation = await ticketHandler.get()
        self.assertIsNotNone(elevation)

        # download as zip file with qgis style
        f = tempfile.NamedTemporaryFile(mode = "w", prefix="klab_test", suffix=".zip" )
        path = f.name
        f.close()
        didit = elevation.exportToFile(Export.DATA, ExportFormat.GEOTIFF_RASTER, path)
        self.assertTrue(didit)
        self.assertTrue(os.path.exists(path))
        self.assertTrue(os.path.getsize(path) > 10000)
        with ZipFile(path, 'r') as zipFile:
            filesCount = len(zipFile.filelist)
        self.assertTrue(filesCount == 2)

        # download as single tiff file
        f = tempfile.NamedTemporaryFile(mode = "w", prefix="klab_test", suffix=".tiff" )
        path = f.name
        f.close()
        didit = elevation.exportToFile(Export.DATA, ExportFormat.BYTESTREAM, path)
        self.assertTrue(didit)
        self.assertTrue(os.path.exists(path))
        self.assertTrue(os.path.getsize(path) > 10000)


    
    def test_spatial_objects_in_catalog(self):
        asyncio.run(self._test_spatial_objects_in_catalog())

    async def _test_spatial_objects_in_catalog(self):
        obsRegion = Observable.create("earth:Region")
        grid = GeometryBuilder().grid(urn= self.ruaha, resolution= "1 km").years(2010).build()
        obsTown = Observable.create("infrastructure:Town")
        ticketHandler = self.klab.submit(obsRegion, grid, obsTown)
        context = await ticketHandler.get()
        self.assertIsNotNone(context)

        obs = context.getObservation("town")
        self.assertIsNotNone(obs)

    # TODO fix and re-enable
    # def test_direct_named_observation(self):
    #     asyncio.run(self._test_direct_named_observation())

    # async def _test_direct_named_observation(self):
    #     obsRegion = Observable.create("earth:Region")
    #     grid = GeometryBuilder().grid(urn= self.ruaha, resolution= "1 km").years(2010).build()
    #     obsElev = Observable.create("geography:Elevation").unit("ft").named("zurba")
    #     ticketHandler = self.klab.submit(obsRegion, grid, obsElev)
    #     context = await ticketHandler.get()
    #     self.assertIsNotNone(context)

    #     self.assertIsNone(context.getObservation("elevation"))
    #     self.assertIsNotNone(context.getObservation("zurba"))


    #     dataRange = context.getObservation("zurba").getDataRange()
    #     range = Range(0, 3000)
    #     self.assertFalse(range.contains(dataRange))

    def test_estimate_observation(self):
        asyncio.run(self._test_estimate_observation())

    async def _test_estimate_observation(self):
        obsRegion = Observable.create("earth:Region")
        grid = GeometryBuilder().grid(urn= self.ruaha, resolution= "1 km").years(2010).build()
        obsElev = Observable.create("geography:Elevation")
        ticketHandler = self.klab.estimate(obsRegion, grid, obsElev)
        estimate = await ticketHandler.get()
        self.assertIsNotNone(estimate)
        self.assertIsNotNone(estimate.estimateId)

        if estimate.cost >= 0:
            ticketHandler = self.klab.submitEstimate(estimate)
            context = await ticketHandler.get()

            self.assertIsNotNone(context)
            self.assertIsNotNone(context.getObservation("elevation"))

            dataflow = context.getDataflow(ExportFormat.KDL_CODE);
            self.assertIsNotNone(dataflow)
            self.assertTrue(len(dataflow) > 0)
            
            provenance = context.getProvenance(True, ExportFormat.ELK_GRAPH_JSON);
            self.assertIsNotNone(provenance)
            self.assertTrue(len(provenance) > 0)
        
    def test_contextual_observation(self):
        asyncio.run(self._test_contextual_observation())

    async def _test_contextual_observation(self):
        obs = Observable.create("earth:Region")
        grid = GeometryBuilder().grid(urn= self.ruaha, resolution= "1 km").years(2010).build()
        ticketHandler = self.klab.submit(obs, grid)
        context = await ticketHandler.get()

        self.assertIsNotNone(context)

        obsElev = Observable.create("geography:Elevation")
        ticketHandler = context.submit(obsElev)
        elevation = await ticketHandler.get()
        self.assertIsNotNone(elevation)
        
        dataRange = elevation.getDataRange()
        range = Range(500, 2500)
        self.assertTrue(dataRange.contains(range))

        #  ensure the context has been updated with the new observation
        self.assertTrue(isinstance(context.getObservation("elevation"), Observation))
        dataflow = context.getDataflow(ExportFormat.KDL_CODE);
        self.assertIsNotNone(dataflow)
        self.assertTrue(len(dataflow) > 0)
            
        provenance = context.getProvenance(True, ExportFormat.ELK_GRAPH_JSON);
        self.assertIsNotNone(provenance)
        self.assertTrue(len(provenance) > 0)

    def test_image_export(self):
        asyncio.run(self._test_image_export())

    async def _test_image_export(self):
        obs = Observable.create("earth:Region")
        grid = GeometryBuilder().grid(urn= self.ruaha, resolution= "1 km").years(2010).build()
        ticketHandler = self.klab.submit(obs, grid)
        context = await ticketHandler.get()
        self.assertIsNotNone(context)

        obsElev = Observable.create("geography:Elevation")
        ticketHandler = context.submit(obsElev)
        elevation = await ticketHandler.get()
        self.assertIsNotNone(elevation)

        f = tempfile.NamedTemporaryFile(mode = "w", prefix="klab_test_ruaha", suffix=".png" )
        path = f.name
        f.close()

        elevation.exportToFile(Export.DATA, ExportFormat.PNG_IMAGE, path,["viewport", "900"])

        self.assertTrue(os.path.exists(path))
        self.assertTrue(os.path.getsize(path) > 10000)
        print(path)

        elevation.exportToString(Export.LEGEND, ExportFormat.JSON_CODE)

    # TODO fix and re-enable
    # def test_constant_observation(self):
    #     asyncio.run(self._test_constant_observation())

    # async def _test_constant_observation(self):
    #     obs = Observable.create("earth:Region")
    #     grid = GeometryBuilder().grid(urn= self.ruaha, resolution= "1 km").years(2010).build()
    #     ticketHandler = self.klab.submit(obs, grid)
    #     context = await ticketHandler.get()
    #     self.assertIsNotNone(context)

    #     obsElev = Observable.create("geography:Elevation").unit("m").value(100)
    #     ticketHandler = context.submit(obsElev)
    #     constantState = await ticketHandler.get()
    #     self.assertIsNotNone(constantState)

    #     value = constantState.getScalarValue()
    #     self.assertEqual(value, 100.0)


class TestLocalConnection(BaseTestClass, IsolatedAsyncioTestCase):

    def setUp(self):
        self.klab = Klab.create()

    def tearDown(self) -> None:
        if self.klab:
            self.assertTrue(self.klab.close())


class TestRemoteConnection(BaseTestClass, IsolatedAsyncioTestCase):
    
    def setUp(self):
        home = os.path.expanduser('~')
        credentialsFile = os.path.join(home, ".klab", "testcredentials.properties")
        username = None
        password = None
        testEngine = "https://developers.integratedmodelling.org/modeler"
        if os.path.exists(credentialsFile):
            with open(credentialsFile, 'r') as file:
                lines = file.readlines()
            for line in lines:
                line = line.strip().split("=")
                key = line[0].strip()
                value = line[1].strip()
                if key == "username":
                    username = value
                elif key == "password":
                    password = value
                elif key == "engine":
                    testEngine = value
        else:
            raise KlabResourceNotFoundException("Can't open ~/.klab/testcredentials.properties with username and passwords for test engine.")


        if username and password and testEngine:
            self.klab = Klab.create(remoteOrLocalEngineUrl=testEngine, username=username, password=password)
        else:
            raise KlabIllegalArgumentException("Credentials for remote mode testing not found.")

    def tearDown(self) -> None:
        if self.klab:
            self.assertTrue(self.klab.close())


if __name__ == "__main__":
    unittest.main()
