from flask import Flask, Response, request
import json
from stm import database as db
import spark

app = Flask(__name__)


def XHRResponse(data, status=200):
    return Response(data, status=status,
                    headers={"Access-Control-Allow-Origin": "*", "Content-Type": "application/json"})


@app.route("/")
def info():
    return "Spark traffic modeler" \
           "<br>(c) Frantisek Kolovsky"


@app.route("/edges/<model>")
def edges(model):
    if db.exists_model(model):
        return XHRResponse(db.get_features(model, "edge", "edge_id"))
    else:
        return XHRResponse('{"details": "model does not exist"}', status=404)


@app.route("/nodes/<model>")
def nodes(model):
    if db.exists_model(model):
        return XHRResponse(db.get_features(model, "node", "node_id"))
    else:
        return XHRResponse('{"details": "model does not exist"}', status=404)


@app.route("/traffic", methods=['GET', 'POST'])
def traffic():
    if request.method == "POST":
        data = spark.traffic(json.loads(request.data))
        return XHRResponse(data)
    return "/traffic POST"


@app.route("/get_traffic", methods=['GET', 'POST'])
def get_traffic():
    if request.method == "POST":
        query = json.loads(request.data)
        data = spark.temp_traffic(query["model"], query["job_id"])
        return XHRResponse(data)
    return "/get_traffic POST"


@app.route("/job_status", methods=['GET', 'POST'])
def job_status():
    if request.method == "POST":
        data = spark.job_status(json.loads(request.data)["job_id"])
        return XHRResponse(data)
    return "/job_status POST"


@app.route("/job_kill", methods=['GET', 'POST'])
def job_kill():
    if request.method == "POST":
        data = spark.job_kill(json.loads(request.data)["job_id"])
        return XHRResponse(data)
    return "/job_kill POST"


@app.route("/add_edge", methods=['GET', 'POST'])
def add_edge():
    if request.method == "POST":
        in_data = json.loads(request.data)
        if "model" in in_data:
            if db.exists_model(in_data["model"]):
                data = db.add_edge(in_data)
                if "details" in data:
                    return XHRResponse(data, status=404)
                else:
                    return XHRResponse(data)
            else:
                return XHRResponse('{"details": "model does not exist"}', status=404)
        else:
            return XHRResponse('{"details": "model property is not set"}', status=404)
    return "/add_edge POST"


@app.route("/add_node", methods=['GET', 'POST'])
def add_node():
    if request.method == "POST":
        in_data = json.loads(request.data)
        if "model" in in_data:
            if db.exists_model(in_data["model"]):
                data = db.add_node(in_data)
                return XHRResponse(data)
            else:
                return XHRResponse('{"details": "model does not exist"}', status=404)
        else:
            return XHRResponse('{"details": "model property is not set"}', status=404)
    return "/add_node POST"


@app.route("/load_model", methods=['GET', 'POST'])
def load_model():
    if request.method == "POST":
        data = spark.load_model(json.loads(request.data)["model"])
        return XHRResponse(data)
    return "/load_model POST"


@app.route("/number_jobs",  methods=['GET', 'POST'])
def number_jobs():
    if request.method == "POST":
        i = spark.number_of_running_job()
        return XHRResponse(json.dumps({"num": i}))
    return "/number_jobs POST"


@app.route("/cache/<model>",  methods=['GET'])
def cache_list(model):
    # return list of cached traffic
    if db.exists_model(model):
        return XHRResponse(db.list_traffic(model))
    else:
        return XHRResponse('{"details": "model does not exist"}', status=404)


@app.route("/cache/<model>/<cache_name>",  methods=['GET'])
def cache(cache_name, model):
    # return traffic with ID
    if db.exists_model(model):
        data = db.get_traffic(cache_name, model)
        if "details" in data:
            return XHRResponse(data, status=404)
        else:
            return XHRResponse(data)
    else:
        return XHRResponse('{"details": "model does not exist"}', status=404)


if __name__ == "__main__":
    app.debug = True
    app.run()
