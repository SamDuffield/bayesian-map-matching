# bmm: Bayesian Map-Matching

[![DOI](https://joss.theoj.org/papers/10.21105/joss.03651/status.svg)](https://doi.org/10.21105/joss.03651)

Map-matching using particle smoothing methods.

[Docs](https://bmm.readthedocs.io/en/latest/) and [methodology](https://arxiv.org/abs/2012.04602).

Contributing guidelines can be found in the repo's `CONTRIBUTING.md` file.

## Install
```
pip install bmm
```

## Load graph and convert to UTM
UTM (Universal Transverse Mercator) is a commonly used projection of spherical longitude-latitude
coordinates into square x-y coordinates.
```python
import numpy as np
import pandas as pd
import osmnx as ox
import json

import bmm

graph = ox.graph_from_place('Porto, Portugal')
graph = ox.project_graph(graph)
```

## Load polyline and convert to UTM
```python
data_path = 'simulations/porto/test_route.csv'
polyline_longlat = json.loads(pd.read_csv(data_path)['POLYLINE'][0])
polyline_utm = bmm.long_lat_to_utm(polyline_longlat, graph)
```
or generate fake data
```python
fake_route, fake_polyline_utm = bmm.sample_route(graph, timestamps=15, num_obs=25)
```

## Offline map-matching
```python
matched_particles = bmm.offline_map_match(graph, polyline=polyline_utm, n_samps=100, timestamps=15)
```

## Online map-matching
```python
# Initiate with first observation
matched_particles = bmm.initiate_particles(graph, first_observation=polyline_utm[0], n_samps=100)

# Update when new observation comes in
matched_particles = bmm.update_particles(graph, matched_particles, new_observation=polyline_utm[1], time_interval=15)
```

## Plot
```python
bmm.plot(graph, particles=matched_particles, polyline=polyline_utm)
```
![porto_mm](simulations/porto/test_route.png?raw=true "Map-matched route - Porto")

## Cite
```
@article{Duffield2022,
  doi = {10.21105/joss.03651},
  url = {https://doi.org/10.21105/joss.03651},
  year = {2022},
  publisher = {The Open Journal},
  volume = {7},
  number = {70},
  pages = {3651},
  author = {Samuel Duffield},
  title = {bmm: Bayesian Map-matching},
  journal = {Journal of Open Source Software}
}
```
