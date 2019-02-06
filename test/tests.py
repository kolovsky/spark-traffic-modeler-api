import requests
import json
import time
import sys
import datetime
import hashlib

main_url = "http://localhost:5000/%s"
#main_url = "http://doprava.plan4all.eu/%s"
headers = {'Content-Type': 'application/json'}

# load model
r = requests.post(url=main_url % "load_model", data='{"model": "tm_pilsen"}', headers=headers)
print r.json()

# number jobs
r = requests.post(url=main_url % "number_jobs", data='{}', headers=headers)
print r.json()

# traffic
cache_name = hashlib.sha1(datetime.datetime.now().isoformat()).hexdigest()
data = {"model": "tm_pilsen", "update": [
    {"index": 8302, "capacity": 1000, "cost": 9999999},
    {"index": 3497, "capacity": 1000, "cost": 9999999},
    {"index": 3834, "capacity": 1000, "cost": 9999999},
    {"index": 3845, "capacity": 1000, "cost": 9999999}
  ], "cache_name": cache_name}
r = requests.post(url=main_url % "traffic", data=json.dumps(data), headers=headers)
print r.json()
job_id = r.json()["job_id"]

# get_traffic
data = {"model": "tm_pilsen", "job_id": job_id}
traffic_type = ""
while traffic_type != "FINAL":
    time.sleep(0.5)
    r = requests.post(url=main_url % "get_traffic", data=json.dumps(data), headers=headers)
    if r.status_code == 200:
        traffic_type = r.json()["type"]
        sys.stdout.write("=")
    else:
        print r.status_code
print ""
print traffic_type

# cache
r = requests.get(url=main_url % "cache/tm_pilsen")
if r.status_code != 200:
    raise Exception("cache list problem")
r = requests.get(url=main_url % "cache/tm_pilsen/"+cache_name)
if r.status_code != 200:
    raise Exception("cache problem")
print "Cache test done"

# test for multiuser usage
data = {"model": "tm_pilsen", "update": [
    {"index": 8302, "capacity": 1000, "cost": 9999999},
    {"index": 3497, "capacity": 1000, "cost": 9999999},
    {"index": 3834, "capacity": 1000, "cost": 9999999},
    {"index": 3845, "capacity": 1000, "cost": 9999999}
  ]}
job_ids = []
for i in range(0, 20):
    r = requests.post(url=main_url % "traffic", data=json.dumps(data), headers=headers)
    if r.json()["status"] == 1:
        job_ids.append(r.json()["job_id"])
    else:
        print r.json()["details"]


pp = True
while pp:
    time.sleep(0.5)
    pp = False
    for job_id in job_ids:
        data = {"model": "tm_pilsen", "job_id": job_id}
        r = requests.post(url=main_url % "get_traffic", data=json.dumps(data), headers=headers)
        if r.status_code == 200:
            if r.json()["type"] == "TEMP":
                pp = True

print "Multiuser test done"





