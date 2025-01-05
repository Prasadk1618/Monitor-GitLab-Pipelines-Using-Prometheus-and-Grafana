import random
import time
import re
import gitlab
import requests
from requests.auth import HTTPBasicAuth
import json
import time
import random
from prometheus_client import start_http_server, Gauge

group_name='demo'
gitlab_server='https://gitlab.com/'
auth_token= '<gitlab _token>'

gl = gitlab.Gitlab(url=gitlab_server, private_token=auth_token)
group = gl.groups.get(group_name)
project_id= <project_id>
project = gl.projects.get(project_id)
gitlab_branch_count = Gauge('gitlab_branch_count', "Number of Branch Count")
def get_metrics():
   gitlab_branch_count.set(len(project.branches.list()))

if __name__ == '__main__':
    start_http_server(8500)
    while True:
        get_metrics()
        time.sleep(43200)
