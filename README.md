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

* Current Version 0.3

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


## Release Notes

| Version | Features | Bugfixes |
| ----------- | ----------- | ----------- |
| 0.1     | MongoDB Integration and basic controllers | N/A |
| 0.2     | Implemented JWT Authentication for Boards and Dashboard users| N/A |
| 0.3     | Implemented User Configuration, and finalized authentication| N/A |

## Maintainers

* Aleksandar Aleksandrov - ava54@drexel.edu
* Tyler Ostinato
* Aleksandar Dunjic
* Brett Chow