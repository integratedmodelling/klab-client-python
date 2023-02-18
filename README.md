## k.LAB CLient Python

A Python client library to interact with a running (local or remote) k.LAB Engine.

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


**For more examples have a look at the testcases in the repository.**