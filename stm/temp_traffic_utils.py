import hashlib
import time


class TempTrafficUtils:
    def __init__(self):
        # key: job_id, value: comp_id
        self.hm = {}

    def job_id_to_comp_id(self, job_id):
        if job_id not in self.hm:
            raise Exception("job id is not in Map")
        return self.hm[job_id]

    def get_comp_id(self, model_name):
        string = model_name + str(time.time())
        return hashlib.sha1(string).hexdigest()

    def set_job_id(self, comp_id, job_id):
        self.hm[job_id] = comp_id

    def remove(self, job_id):
        if job_id in self.hm:
            del self.hm[job_id]
