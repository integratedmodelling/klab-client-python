""" sample script how to use the klab-client-api

    First, install client via pip
    pip install klab-client-py

    Second, set up a properties file with your credentials and place in your Home folder -
        filename: aries_client_credentials.properties
        content:
                 # hash is comment
                 username=myuser
                 password=mypwd
                 engine=https://myurl.org/modeler

    Note: in this simple example we just request a DEM raster file and save it to disk
          nevertheless, the ARIES_request function can be use for universal requests
"""

from klab.klab import Klab
from klab.geometry import GeometryBuilder
from klab.observable import Observable
from klab.utils import Export, ExportFormat
import asyncio
import os

# standard path to the k.lab HUB credential file
STANDARD_PATH = os.path.join(os.path.expanduser('~'), ".klab", "testcredentials.properties")


async def ARIES_request(klab: Klab, area_WKT: str, obs_res: str, obs_year: int, observable: str,
                        export_format: ExportFormat, export_path: str):
    """to warp the ARIES request to trigger the asyncio ticket handling

    :param klab: active k.lab client instance
    :param area_WKT: geometry to use a context, here defined by WKT string
    :param obs_res: spatial resolution of the context
    :param obs_year: temporal domain (here only single years allowed)
    :param observable: observable - semantic syntax for requested dataset/model
    :param export_format: export format for the retrieved data
    :param export_path: absolute file path to save data to
    """
    # create the semantic type and geometry/time to init the CONTEXT
    obs = Observable.create("earth:Region")
    grid = GeometryBuilder().grid(urn=area_WKT, resolution=obs_res).years(obs_year).build()

    # submit to engine to generate the CONTEXT
    ticketHandler = klab.submit(obs, grid)
    context = await ticketHandler.get()

    # define the observable (dataset or model) and submit to context
    obsData = Observable.create(observable)
    ticketHandler = context.submit(obsData)
    data = await ticketHandler.get()

    # retrieve the dataset and export to disk
    data.exportToFile(Export.DATA, export_format, export_path)


def request_parameters() -> dict:
    """specification of the parameters for the ARIES data request

        Note: the parameters are here hardcoded

    :return: dict with the request parameters
    """
    request = {
        'polygon_WKT': "EPSG:4326 POLYGON((33.796 -7.086, 35.946 -7.086, 35.946 -9.41, 33.796 -9.41, 33.796 -7.086))",
        'observable': "geography:Elevation",  # symantic syntax
        'observation_resolution': "1 km",  # must be a string with unit definition
        'observation_time': 2010,
        'export_format': ExportFormat.BYTESTREAM,  # for single file return
        'out_path': os.path.normpath(r'./elevation_test.tif')
    }
    return request


def get_klab_instance(fpath: str = STANDARD_PATH) -> Klab:
    """initialization of the klab RemoteEngine object with fallback to LocalEngine

    :param fpath: absolute file path to the k.HUB credential properties file
    :return: active k.LAB client instance
    """
    try:
        print('- try Remote Engine connection ....')
        klab = Klab.create(credentialsFile=fpath)
    except:
        try:
            print('- try Local Engine connection ...')
            klab = Klab.create()
        except:
            raise RuntimeError('Could not establish connection to a k.lab engine')

    if klab and klab.isOnline():
        print(f'* connection to {klab.engine.url} was successfully established. session: {klab.engine.session}')
    else:
        raise EnvironmentError('could not establish connection to the klab instance')

    return klab


def main():
    # create a new klab client instance -> use own credential file
    klab = get_klab_instance(os.path.join(os.path.expanduser('~'), "aries_client_credentials.properties"))

    # set up the parameters for the data retrival -> here just from hardcoded values
    param = request_parameters()

    # now we can run the asyncio function and execute the data retrival
    try:
        asyncio.run(ARIES_request(klab,
                                  area_WKT=param['polygon_WKT'],
                                  observable=param['observable'],
                                  obs_res=param['observation_resolution'],
                                  obs_year=param['observation_time'],
                                  export_format=param['export_format'],
                                  export_path=param['out_path']))
        print(f'{param["observable"]} dataset successfully retrieved. File saved: {param["out_path"]}')
    except:
        raise RuntimeError('could not retrieve the data from ARIES')
    finally:
        klab.close()


if __name__ == "__main__":
    main()
