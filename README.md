# Monitor-GitLab-Pipelines-Using-Prometheus-and-Grafana
### Step #1:Setting Up the Ubuntu Instance
First Update the package list.
``` sudo apt update ```
Install Docker and pip if it’s not already installed.
``` sudo apt install -y docker.io python3-pip ```
Install Docker-Compose to manage multiple containers.
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
````
Change its permissions.

``` sudo chmod +x /usr/local/bin/docker-compose ```

Install the Virtual environment.

```sudo apt install python3.12-venv ```

Create a new virtual environment named venv.


``` python3 -m venv venv ```

Activate the virtual environment.

``` source venv/bin/activate ```

### Step #2:Create Project Structure and Files
Create a folder for your project and navigate into it.


```bash
mkdir Gitlab-monitoring
cd Gitlab-monitoring
```
Inside this folder, create subfolder for Prometheus and navigate to it.
```bash
mkdir Prometheus
cd Prometheus
```

create a prometheus configuration file

```bash
nano prometheus.yml
```
add the following code into it.
```bash
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: monitoring

    static_configs:
      - targets: ['<EC2-Public-IP>:8080']

  - job_name: monitoring_manual

    static_configs:
      - targets: ['<EC2-Public-IP>:8500']
  ```

Back to project directory.


``` cd .. ```

Create Dockerfile.

``` nano Dockerfile ```

add the following code into it.
```bash
FROM python:3.12

WORKDIR /code

COPY requirement.txt .

RUN pip install -r requirement.txt

COPY . .

CMD [ "python", "gcexporter.py" ]
```
Create a docker-compose.yml file.


``` nano docker-compose.yml ```

add following code into it.
```bash
version: '3.8'
services:
  grafana:
    image: docker.io/grafana/grafana:latest
    ports:
      - 3000:3000
    environment:
       GF_INSTALL_PLUGINS: grafana-polystat-panel,yesoreyeram-boomtable-panel
    links:
      - prometheus

  prometheus:
      image: docker.io/prom/prometheus:v2.28.1
      ports:
       - 9090:9090
      links:
       - gitlab-ci-pipelines-exporter
      volumes:
       - ./Prometheus/prometheus.yml:/etc/prometheus/prometheus.yml

  gitlab-ci-pipelines-exporter:
    image: docker.io/mvisonneau/gitlab-ci-pipelines-exporter:v0.5.2
    ports:
      - 8080:8080
    environment:
      GCPE_CONFIG: /etc/gitlab-ci-pipelines-exporter.yml
    volumes:
      - type: bind
        source: ./gitlab-ci-pipelines-exporter.yml
        target: /etc/gitlab-ci-pipelines-exporter.yml

  customized_exporter:
        build: .
        ports:
            - "8500:8500"
```
Create a configuration file for the GitLab CI Pipelines Exporter.

```xnano gitlab-ci-pipelines-exporter.yml ```

add the following code into it. Get the token from gitlab and project id from your project setting.
```bash
log:
  level: info

gitlab:
  url: https://gitlab.com
  token: '<gitlab_token>'

# Example public projects to monitor
projects:
  - name: demo/test_pipeline
    # Pull environments related metrics prefixed with 'stable' for this project
    pull:
      environments:
        enabled: true
      refs:
        branches:
          # Monitor pipelines related to project branches
          # (optional, default: true)
          enabled: true

          # Filter for branches to include
          # (optional, default: "^main|master$" -- main/master branches)
          regexp: ".*"
        merge_requests:
          # Monitor pipelines related to project merge requests
          # (optional, default: false)
          enabled: true
```

Create a gcexporter.py. This is a customized exporter to retrieve total branch count in the project.

``` nano gcexporter.py ```

add the following code into it.
```bash
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
```

Create a requirement.txt file.

``` nano requirement.txt ```

add the following code into it.
```bash 
python-gitlab==3.1.1
prometheus-client==0.13.1
```
### Step #3:Install Python Dependencies
The requirement.txt file contains the dependencies for the custom exporter. So lets run the following command.

``` pip3 install -r requirement.txt ```

### Step #4:Build and Start the Services
Build the Docker containers.

``` docker-compose build ```

Start the services.

``` docker-compose up -d ```

Check running containers.

``` docker ps -a ```

### Step #5:Access the Services
Visit http://<EC2-Public-IP>:9090 to verify data collection. Below you can see the Prometheus UI.
