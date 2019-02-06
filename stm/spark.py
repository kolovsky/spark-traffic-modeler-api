from sjsclient import client
from sjsclient import exceptions
from stm import settings as s
import json
import time
import temp_traffic_utils
sjs = client.Client(s.job_server_url)
ttu = temp_traffic_utils.TempTrafficUtils()


def load_model(model_name):
    app = sjs.apps.get(s.app_name)
    context = sjs.contexts.get(s.context)
    job = sjs.jobs.create(app, s.class_path, ctx=context, conf=json.dumps({"task": "load_model", "model": model_name}))
    while job.status != "FINISHED":
        time.sleep(1)
        job = sjs.jobs.get(job.jobId)
        if job.status == "ERROR":
            return json.dumps({"status": 0, "error": "Job Fail -> see to JobServer interface for more details"})

    return json.dumps({"status": 1})


def traffic(p):
    if number_of_running_job() > s.max_num_traf_comp:
        return json.dumps({"status": 0, "details": "too many running jobs, please wait or kill some job"})
    p["task"] = "traffic"
    comp_id = ttu.get_comp_id(p["model"])
    p["comp_id"] = comp_id
    app = sjs.apps.get(s.app_name)
    context = sjs.contexts.get(s.context)
    try:
        job = sjs.jobs.create(app, s.class_path, ctx=context, conf=json.dumps(p))
    except exceptions.HttpException as e:
        return json.dumps({"status": 0, "details": str(e)})
    ttu.set_job_id(comp_id, job.jobId)
    return json.dumps({"status": 1, "job_id": job.jobId})


def job_status(job_id):
    job = sjs.jobs.get(job_id)
    if job.status == "FINISHED":
        ttu.remove(job_id)
    return json.dumps({"status": job.status})


def job_kill(job_id):
    job = sjs.jobs.get(job_id)
    job.delete()
    return json.dumps({"status": 1})


def temp_traffic(model_name, job_id):
    job = sjs.jobs.get(job_id)
    if job.status == "FINISHED":
        ttu.remove(job_id)
        return json.dumps({"traffic": job.result, "type": "FINAL", "status": 1})

    app = sjs.apps.get(s.app_name)
    context = sjs.contexts.get(s.context)
    try:
        job = sjs.jobs.create(app, s.class_path, ctx=context,
                              conf=json.dumps({"task": "temp_traffic", "model": model_name, "comp_id": ttu.job_id_to_comp_id(job_id)}),
                              sync=True)
    except exceptions.HttpException as e:
        return json.dumps({"status": 0, "details": str(e)})
    return json.dumps({"traffic": job.result, "type": "TEMP", "status": 1})


def number_of_running_job(limit=30):
    return len(list(sjs.jobs.list(limit=limit, status="RUNNING")))
