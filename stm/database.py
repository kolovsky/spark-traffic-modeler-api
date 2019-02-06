from psycopg2.pool import SimpleConnectionPool
import settings as s
import json

pool = SimpleConnectionPool(1, s.max_connection, host=s.host, database=s.db, user=s.user, password=s.password)


def get_features(schema, table, order_by):
    """
    Return GeoJSON of spatial table
    :param string schema: database schema name
    :param string table:
    :return:
    """
    conn = pool.getconn()
    cur = conn.cursor()
    sql = "SELECT *, ST_asgeojson(ST_transform(%s, 3857)) as geojson FROM %s.%s ORDER BY %s"
    cur.execute(sql %(s.geometry_column, schema, table, order_by))
    columns = list([desc[0] for desc in cur.description])

    out = {"type": "FeatureCollection", "features": []}
    for r in cur:
        out["features"].append(__row(columns, r))

    pool.putconn(conn)
    return json.dumps(out)


def __row(column, data):
    prop = {}
    r = {"type": "Feature"}
    for i in range(0, len(column)):
        if column[i] != s.geometry_column and column[i] != "geojson":
            prop[column[i]] = data[i]

        if column[i] == "geojson":
            r["geometry"] = json.loads(data[i])

    r["properties"] = prop
    return r


def add_node(p):
    conn = pool.getconn()
    cur = conn.cursor()
    sql_id = "SELECT max(node_id) FROM %s.node;" % p["model"]
    cur.execute(sql_id)
    res = cur.fetchall()
    if res[0][0] is None:
        node_id = 1
    else:
        node_id = res[0][0] + 1

    xy = p["geometry"]["coordinates"]
    sql = "INSERT INTO "+p["model"]+".node(node_id, geometry) VALUES (%s, ST_setsrid(ST_Point(%s, %s), 4326));"
    cur.execute(sql, (node_id, xy[0], xy[1]))
    conn.commit()
    pool.putconn(conn)
    return json.dumps({"node_id": node_id})


def add_edge(p):
    conn = pool.getconn()
    cur = conn.cursor()

    sql_id = "SELECT max(edge_id) FROM %s.edge;" % p["model"]
    cur.execute(sql_id)
    res = cur.fetchall()
    if res[0][0] is None:
        edge_id = 1
    else:
        edge_id = res[0][0] + 1

    prop = p["properties"]

    sql = "INSERT INTO "+p["model"]+".edge(edge_id, source, target, capacity, cost, isvalid, turn_restriction, geometry)" \
          " VALUES (%s, %s, %s, %s, %s, %s, %s, st_setsrid(ST_GeomFromGeoJSON(%s), 4326));"

    if "source" not in prop:
        return json.dumps({"details": "source property missing"})
    if "target" not in prop:
        return json.dumps({"details": "target property missing"})
    if "capacity" not in prop:
        return json.dumps({"details": "capacity property missing"})
    if "cost" not in prop:
        return json.dumps({"details": "source property missing"})

    if "turn_restriction" in prop:
        turn_restriction = prop["turn_restriction"]
    else:
        turn_restriction = ""

    cur.execute(sql, (edge_id, prop["source"], prop["target"],
                      prop["capacity"], prop["cost"], False, turn_restriction, json.dumps(p["geometry"])))
    conn.commit()
    pool.putconn(conn)
    return json.dumps({"edge_id": edge_id})


def exists_model(model_name):
    sql = "SELECT count(*) FROM information_schema.schemata WHERE schema_name = '%s'" % model_name
    conn = pool.getconn()
    cur = conn.cursor()
    cur.execute(sql)
    count = cur.fetchall()[0][0]
    pool.putconn(conn)
    return count == 1


def get_traffic(cache_name, model_name):
    sql = "SELECT \"name\", time_stamp, config, result FROM %s.cache WHERE name = '%s'" % (model_name, cache_name)
    conn = pool.getconn()
    cur = conn.cursor()
    cur.execute(sql)
    data = cur.fetchall()
    if len(data) != 0:
        x = data[0]
        out = {"cache_name": x[0], "timestamp": str(x[1]), "config": x[2], "result": x[3]}
    else:
        out = {"details": "cache result with name '%s' do not exist" % cache_name}
    pool.putconn(conn)
    return json.dumps(out)


def list_traffic(model_name):
    """
    Return a list of cached results
    :param string model_name: model name
    :return:
    """
    sql = "SELECT \"name\", time_stamp FROM %s.cache;" % model_name
    conn = pool.getconn()
    cur = conn.cursor()
    cur.execute(sql)
    data = cur.fetchall()
    out = map(lambda x: {"cache_name": x[0], "timestamp": str(x[1])}, data)
    pool.putconn(conn)
    return json.dumps(out)


