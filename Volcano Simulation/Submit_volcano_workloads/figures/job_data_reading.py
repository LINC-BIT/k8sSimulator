import datetime
import logging
import os
import re
from typing import Tuple, List

import pandas as pd


def read_data_from_directory(directory: str) -> Tuple[float, float, float, float, pd.DataFrame]:
    csv_filename = os.path.join(directory, 'coutJCT.csv')
    data = pd.read_csv(csv_filename)
    job_complete_times = data['Job Completed Time(s)']

    markdown_filename = os.path.join(directory, 'coutJCT.md')
    with open(markdown_filename) as f:
        md = f.read()
    makespan = re.findall(r'\d+\.\d\d', md)[-1]
    return job_complete_times.mean(), job_complete_times.min(), job_complete_times.max(), float(makespan), data


# returns summary and jobs
def read_data_from_directories(directories: List[str]):
    mean_jct_list, min_jct_list, max_jct_list, makespans, names = [], [], [], [], []
    df = None
    for directory in directories:
        mean_jct, min_jct, max_jct, makespan, data = read_data_from_directory(directory)
        name = directory.split('-')[-1].upper()
        mean_jct_list.append(mean_jct)
        min_jct_list.append(min_jct)
        max_jct_list.append(max_jct)
        makespans.append(makespan)
        names.append(name)
        data['name'] = name
        if df is None:
            df = data
        else:
            df = pd.concat([df, data])

    return pd.DataFrame({
        'mean(jct)': mean_jct_list,
        'min(jct)': min_jct_list,
        'max(jct)': max_jct_list,
        'makespan': makespans,
        'name': names
    }).sort_values(by='name'), df


def save_csv(data_frame: pd.DataFrame):
    now = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    save_dir = 'results/csv'
    os.makedirs(save_dir, exist_ok=True)
    save_filename = os.path.join(save_dir, f'{now}.xlsx')
    logging.info(f'save filename {save_filename}')
    with pd.ExcelWriter(save_filename) as writer:
        data_frame.to_excel(writer)
