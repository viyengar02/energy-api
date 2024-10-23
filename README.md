# Energy Management and Prediction System API #

This project is a FAST API Python based backend REST API for the Energy Management and Prediction System for Senior Design Group 06. The key responsibilities for this API act as an integration component of the different components of the system.

This document provides a quick overview of the system, how to set it up locally and major release notes.

## Overview

* Key Functionalities
    - Provides REST Endpoints for interfacing a MongoDB database
    - Incorporates basic board authentication 
    - WebCrawlers for recording energy data [FUTURE RELEASE]
    - Used by ESP32 microcontrollers to send and record measured data from ADE9000 chips
    - Used by Machine Learning algorithms to read recorded data
    - Used by the User Dashboard to pull energy data and Machine Learning Results

* Current Version 0.4

## Installation

* Create a Python3.11 Virtual Environment and Activate it

```bash
python3 -m venv /path/to/new/virtual/environment
source /path/to/new/virtual/environment/bin/activate
```
* Navigate to the root directory of the emps-api repository and install dependencies

```bash
pip3 install -r requirements.txt
```

* Start the development server locally on port 8000

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

* To confirm that the server is running successfully - http://localhost:8000/

## Deployment EC2

* SSH into an EC2 instance and make sure Python 3.11 is installed

* Check if a current API process is currently running and kill it:

```bash
ps xw
15726 ?        S      0:00 sshd: ec2-user@pts/0
15727 pts/0    Ss     0:00 -bash
15805 pts/0    S      0:01 /usr/bin/python3 /usr/local/bin/uvicorn main:app --reload --host 0.0.0.0 --port 8000
15806 pts/0    S      0:00 /usr/bin/python3 -c from multiprocessing.semaphore_tracker import main;main(4)
15807 pts/0    Sl     0:00 /usr/bin/python3 -c from multiprocessing.spawn import spawn_main; spawn_main(tracker_fd=5, pipe_handle=7) --multiprocessing-fork
15820 pts/0    R+     0:00 ps xw
kill 15805
```

* To start the API, navigate to the emps-api folder and run:

```bash
nohup uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
```

This command will ensure that the API instance will keep running after closing the SSH connections and will run it on the background. The "jobs" command can be used to ensure that the app is running.


## Release Notes

| Version | Features | Bugfixes |
| ----------- | ----------- | ----------- |
| 0.1     | MongoDB Integration and basic controllers | N/A |
| 0.2     | Implemented JWT Authentication for Boards and Dashboard users| N/A |
| 0.3     | Implemented User Configuration, and finalized authentication| N/A |
| 0.4     | Implemented an example XGBOOST model run| N/A |
| 0.5     | Implemented a Websocket for two way board communication | N/A |
| 0.6     | Implemented a Optimization Integrations with power threshold | N/A |
| 0.7     | Implemented a Websocket for the user which listens and send energy records | Fixed Async Task Cleanup |
| 0.8     | Implemented compund models | N/A |
| 0.9     | Implemented ML optimization | N/A |


## Original Creators

* Aleksandar Aleksandrov - ava54@drexel.edu
* Tyler Ostinato
* Aleksandar Dunjic
* Brett Chow

## Maintaners
* Varun Iyengar - viyengar02@gmail.com
* Harrison Muller
* Nate Judd
* Kaylie Ludwick
* Cassius Garcia
