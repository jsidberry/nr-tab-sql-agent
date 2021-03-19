#!/usr/bin/python3

import os
import json
import time
from datetime import datetime, timedelta, date
import subprocess
import pprint as pp
import logging
import pyodbc 
import config # add config.py to root directory to use

from newrelic_telemetry_sdk import GaugeMetric, MetricClient

import requests
import xml.etree.ElementTree as ET

