import datetime
import logging
import os
import shutil

import yaml


def load_from_file(filename: str):
    with open(filename, 'r') as file:
        workload = list(yaml.safe_load_all(file))
        logging.info(f'Workload {filename} loaded, with {len(workload)} jobs')
        return workload


def do_until_no_error(func):
    def wrapper(*args, **kwargs):
        while True:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logging.exception(e)
    return wrapper


def now_str():
    return datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')


def now_str_millisecond():
    return datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S.%f')


def makeup_results_dir():
    results_dir_exists = os.path.exists('results')
    os.makedirs('results', exist_ok=True)
    if results_dir_exists:
        os.makedirs('old-results', exist_ok=True)
        shutil.move('results', 'old-results')
        os.rename('old-results/results', f'old-results/{now_str()}')
        os.makedirs('results', exist_ok=True)
