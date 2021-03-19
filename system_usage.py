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


def yesterday_midnight_init_start_date_time():
    # ensure each call starts at midnight the previous day
    dt                       = date.today()
    midnight                 = datetime.combine(dt, datetime.min.time())
    yesterday_midnight       = midnight - timedelta(days=1, seconds=7200)
    yesterday_epoch_midnight = datetime.timestamp(yesterday_midnight)
    return int(yesterday_epoch_midnight)


def calculate_time_intervals(time_block, init_start, init_end):
    interval       = 3600 - (3600 * time_block)
    init_starttime = int(init_start) + int(interval)
    init_endtime   = int(init_end) + int(interval)
    return init_starttime, init_endtime


def run_curl_command(entity_id, init_starttime, init_endtime, query_key, account_id):
    NRQL_ALL = f'SELECT average(cpuPercent), average(memoryUsedPercent), average(diskUsedPercent) FROM SystemSample FACET hostname WHERE entityId = {entity_id} SINCE {init_starttime} UNTIL {init_endtime} TIMESERIES'.replace(" ", "%20")
    command  = f"curl -H 'Accept: application/json' -H 'X-Query-Key: {query_key}' 'https://insights-api.newrelic.com/v1/accounts/{account_id}/query?nrql={NRQL_ALL}'"
    print()
    return command 


def main():
    num_hrs       = 24  #  1 day
    query_key     = config.query_key
    account_id    = config.account_id
    entity_ids    = (
        ("AZUPWTABGW01", 8634054696753406258), 
        ("AZUPWTABWRK06", 7674407372321415153), 
        ("AZUPWTABWRK07", 7003032567755051516), 
        ("AZUPWTABWRK08", 5256329454637754366)
    )

    init_start = int(yesterday_midnight_init_start_date_time())
    init_end   = str(int(init_start) + 3600) # Sunday, January 31, 2021 7:00:00 PM GMT-05:00
    now        = f"{datetime.now():%Y-%m-%d-%H%M}"

    for hostname, entity_id in entity_ids:
        csv_filename = f"cpu_avg_{now}_{hostname}.csv"
        csv_file     = open(csv_filename, "w")
        csv_file.write(f'hostname, epoch_start_time, epoch_end_time, start_date_time, end_date_time, cpu_avg, mem_avg, disk_avg\n')

        for time_block in range(num_hrs):
            init_starttime, init_endtime = calculate_time_intervals(time_block, init_start, init_end)
            json_object_with_content     = run_curl_command(entity_id, init_starttime, init_endtime, query_key, account_id)
            content                      = parse_json_object(json_object_with_content)
            push_data_to_csv_file(csv_file, content)
            
        csv_file.close()


if __name__ == "__main__":
    main()
