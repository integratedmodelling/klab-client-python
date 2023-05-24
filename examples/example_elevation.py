""" connection test to ARIES platform

    install client via pip
    pip install klab-client-py

    setup a YAML file with your credentials and place in your Home folder - filename: aries_access_credentials.yaml
    url: https://developers.integratedmodelling.org/modeler
    username: <your_data>
    pass: <your_data>

    Note: currently only file search for Windows implemented

"""

from klab.klab import Klab
from klab.geometry import GeometryBuilder
from klab.observable import Observable
from klab.observation import Observation
from klab.utils import Export, ExportFormat
import asyncio
import os



# create a function to retrieve the needed data --> needed to trigger asyncio
# TODO: we need convenience functions --> that is too complex
async def ARIES_request(klab, area_WKT: str, obs_res: str, obs_year: int, observable: str, export_format, export_path):
    # create the semantic type and geometry/time to init the CONTEXT
    obs = Observable.create("earth:Region")
    grid = GeometryBuilder().grid(urn=area_WKT, resolution=obs_res).years(obs_year).build()

    # now submit to the engine to generate the CONTEXT
    # in CONTEXT (space/time) we then can request a dataset or model
    ticketHandler = klab.submit(obs, grid)
    context = await ticketHandler.get()

    # define the observable (dataset or model) and submit to context
    obsData = Observable.create(observable)
    ticketHandler = context.submit(obsData)
    data = await ticketHandler.get()

    # retrieve the dataset and export to disk
    data.exportToFile(Export.DATA, export_format, export_path)

# ##############################################
# here starts the work
# create a new klab client instance
try:
    home = os.path.expanduser('~')
    credentialsFile = os.path.join(home, ".klab", "testcredentials.properties")

    klab = Klab.create(credentialsFile=credentialsFile)
    url = klab.url
except:
    # if no credentials are setup try to access a local klab engine
    klab = Klab.create()
    url = 'K.LAB local instance'

if klab.isOnline():
    print(f'* connection to {url} was successfully established. session: {klab.session}')
else:
    raise EnvironmentError('could not establish connection to the klab instance')

# setup the parameters for the data retrival
# area geometry here via a WKT
polygon_WKT = "EPSG:4326 POLYGON((33.796 -7.086, 35.946 -7.086, 35.946 -9.41, 33.796 -9.41, 33.796 -7.086))"
observable = "geography:Elevation"
observation_resolution = "1 km"
observation_time = 2010

export_format = ExportFormat.BYTESTREAM
out_path = os.path.normpath(r'./elevation_test.tif')

# now we can run the asyncio function and execute the data retrival
try:
    asyncio.run(ARIES_request(klab, area_WKT=polygon_WKT, observable=observable,
                              obs_res=observation_resolution, obs_year=observation_time,
                              export_format=export_format, export_path=out_path))
    print(f'{observable} dataset successfully retrieved. File saved: {out_path}')
except:
    raise RuntimeError('could not retrieve the data from ARIES')
finally:
    klab.close()