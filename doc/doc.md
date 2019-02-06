Documentation
=============
##API
### Geometry

    GET /edges/<model>          - return GeoJSON of edges
    GET /nodes/<model>          - return GeoJSON of nodes    

When model does not exist, the response is `{"details": "model does not exist"}` and status code is `404`

### Model computation
    
    POST /load_model    - load model to memory
    POST /traffic       - strat to assignee ODM to network, ASYNC
    POST /get_traffic   - return traffic, SYNC
    POST /job_status    - return job status, SYNC
    POST /job_kill      - kill job, SYNC

First the model must be loaded, after that the computation (assignment) can be started using `/traffic`. This method returns `job_id` and using this `job_id` the traffic can be received (`/get_traffic`).

##### load_model
`input`
```json
{
  "model": "model_name"
}
```
`output`
```json
{
  "status": 1 
}
```

##### traffic
`input`
```json
{
  "model": "",
  "update": [
    {
      "index": 1,
      "capacity": 300,
      "cost": 99999
    }
  ],
  "cache_name": "Gen_paton_bridge"
}
```
When 'cache_name' is set than the result are going to be cached at database. 'cache_name' is primary key. The cached results with same name will be overwritten.

`output`

    status
        1 - ok
        0 - fail
    job_id
    
```json
{
  "status": 1,
  "job_id": ""
}
```

##### get_traffic
`input`
```json
{
  "model": "model_name",
  "job_id": ""
}
```
`output`

    type      - type of computed traffic
        TEMP  - not final traffic
        FINAL - final version of traffic
    traffic   - array edge map traffic

```json
{
  "status": 1,
  "type": "TEMP",
  "traffic": [12.56, ...]
}
```

##### job_status
`input`
```json
{
  "job_id": ""
}
```
`output`

    status - status of the computation
        RUNNING
        ERROR
        FINISHED

```json
{
  "status": "ERROR"
}
```
##### job_kill
`input`
```json
{
  "job_id": ""
}
```
`output`

```json
{
  "status": 1
}
```

### Cache

    GET /cache/<model>                  - return list of cached results
    GET /cache/<model>/<cache_name>     - return cached result
    
`output`

```json
{
  "timestamp": "2019-01-29 12:20:34.312637",
  "config": {},
  "result": [12.56, ...],
  "cache_name": "Gen_paton_bridge"
}
```

'config' is job configuration. 'timestamp' is last update of record.

### Add geometry

    POST /add_edge  - add new edge to network and return edge_id
    POST /add_node  - add new node to network and return node_id
    
After adding new nodes and edges you have to **reload** the model using `/load_model`. The new edges are added as non valid 
edges and have cost equal to Infinity. Using `/traffic` you can update the cost and thus make the edges valid.
    
##### add_node

`input`
GeoJSON (EPSG: 4326) of node with 'model' property, e.g:
```json
{
  "type": "Feature",
  "geometry": {
    "type": "Point",
    "coordinates": [125.6, 10.1]
  },
  "properties": {},
  "model": "tm_pilsen_new"
}
```

`output`
'node_id' of new node
```json
{
  "node_id": 11110
}
```

##### add_edge
`input`
GeoJSON (EPSG: 4326) of edge with 'model' property, e.g:
```json
{
    "geometry": {
        "type": "LineString", 
        "coordinates": [[0, 0], [125.6, 10.1]]
    },
    "type": "Feature",
    "properties": {
        "capacity": 1000.0,
        "source": 4476,
        "target": 4465,
        "cost": 0.000832817
    },
    "model": "tm_pilsen_new"
}
```
'source' is node_id of source node and 'target' is node_id of target node of edge

`output`
edge_id of new edge
```json
{
  "edge_id": 11110
}
```

### Other

    POST /number_jobs   - returns number of running jobs (traffic computation)

##### number_jobs
`output`
```json
{
  "num": 0
}
```
    
    
