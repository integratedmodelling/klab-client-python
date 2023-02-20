# k.LAB CLient Python

A Python client library to interact with a running (local or remote) k.LAB Engine.

This package is a python client for [k.LAB](https://github.com/integratedmodelling/klab). It allows registered users of k.LAB to make observations on the k.LAB semantic web from a Java program using the REST API. After creating a spatial/temporal context root observation as a context, you can submit concepts to be observed in it and the relative observations will be made at the server side and returned. Depending on the semantics submitted, the results will consists of different scientific artifacts that can be exported or inspected as needed through the API.

While the API (both k.LAB's public REST API and the interfaces in this package) should be stable, this code is young - features are still missing and bugs certainly remain. Please submit Github issues as needed.

This README assumes knowledge of k.LAB and semantic modeling. An introduction to both is available as a [technical note](https://docs.integratedmodelling.org/technote/index.html) while more extensive documentation is developed.


## Installation

The module can be installed through pip as:

```
pip install klab-client-py
```

## Usage

Usage example: observe elevation on a given region

Note that asyncio is used to handle async elaborations.

1. add necessary imports and create a new client instance
```
from klab.klab import Klab
from klab.geometry import GeometryBuilder
from klab.observable import Observable
from klab.observation import Observation
from klab.utils import Export, ExportFormat
import asyncio

klab = Klab.create()
```

2. define a geometry to use as context through its WKT definition

```
ruaha = "EPSG:4326 POLYGON((33.796 -7.086, 35.946 -7.086, 35.946 -9.41, 33.796 -9.41, 33.796 -7.086))"
```

3. create a semantic type and a geometry

```
obs = Observable.create("earth:Region")
grid = GeometryBuilder().grid(urn= ruaha, resolution= "1 km").years(2010).build()
```

4. submit them to the engine and obtain the context

```
ticketHandler = self.klab.submit(obs, grid)
context = await ticketHandler.get()
```

5. create the elevation observable and submit it to the context

```
obsElev = Observable.create("geography:Elevation")
ticketHandler = context.submit(obsElev)
elevation = await ticketHandler.get()
```

6. export the observation to a geotiff

```
path = "your path here"
elevation.exportToFile(Export.DATA, ExportFormat.GEOTIFF_RASTER, path)
```


**For more examples have a look at [the testcases in the repository](https://github.com/integratedmodelling/klab-client-python/tree/main/tests).**