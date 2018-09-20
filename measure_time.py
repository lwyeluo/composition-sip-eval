#!/usr/bin/env python
# coding: utf-8

# In[1]:


from __future__ import print_function
import os
import json
import numpy as np
import pandas as pd
from pandas.io.json import json_normalize
import re


# In[2]:


def get_immediate_subdirectories(d):
    return filter(os.path.isdir, [os.path.join(d, f) for f in os.listdir(d)])


# In[3]:


def process_files(directory):
    all_df = pd.DataFrame()
    for program_dir in get_immediate_subdirectories(directory):
        program = os.path.basename(program_dir)
        for coverage_dir in sorted(get_immediate_subdirectories(program_dir)):
            coverage = os.path.basename(coverage_dir)
            if coverage == "0":
                continue

            for combination_dir in get_immediate_subdirectories(coverage_dir):
                combination = os.path.basename(combination_dir)

                for attempt_dir in get_immediate_subdirectories(combination_dir):
                    result_path = attempt_dir
                    attempt = os.path.basename(attempt_dir)

                    results = grab_results(result_path)

                    df = json_normalize(data=results)
                    df.insert(0, 'attempt', int(attempt))
                    df.insert(0, 'combination', int(combination))
                    df.insert(0, 'coverage', int(coverage))
                    df.insert(0, 'program', replace_name(program))
                    all_df = all_df.append(df, sort=False)

    return all_df


# In[11]:


def grab_results(result_directory):
    patchTimeRegex = re.compile(r"totaltime: (\d+\.\d+)\s(\d+\.\d+)\s(\d+\.\d+)")
    totalTimeRegex = re.compile(r"Total Execution Time: (\d+\.\d+)")
    optRegex = re.compile(r"(?:(\d+\.\d+)\s+.*?)+(\b[a-zA-Z ]+\b)")

    patch_time_txt = os.path.join(result_directory, "patchTime.txt")
    transform_console = os.path.join(result_directory, "transform.console")

    patch_time = 0
    if os.path.isfile(patch_time_txt):
        with open(patch_time_txt, 'r') as f:
            data = f.read()
            m = re.match(patchTimeRegex, data)
            patch_time = m.group(1)

    passes = {}
    total_time = 0
    if os.path.isfile(transform_console):
        with open(transform_console, 'r') as f:
            data = f.read()

            for m in re.finditer(totalTimeRegex, data):
                total_time = float(m.group(1))
                break

            cf_time = 0
            for m in re.finditer(optRegex, data):
                name = m.group(2).strip()
                value = float(m.group(1))
                if name == "Instruments bitcode with hashing and logging functions":
                    passes["oh"] = value
                elif name == "Marks functions to be mobilized":
                    passes["cm"] = value
                elif name == "Control Flow Integrity Pass":
                    passes["cfi"] = value
                elif name == "Instruments bitcode with guards":
                    passes["sc"] = value
                elif name == "Constraint Protection Pass":
                    cf_time += value
                elif name == "Constraint Graph Pass":
                    cf_time += value
                elif name == "Constraint Analysis Pass":
                    cf_time += value

            passes["cf"] = float(cf_time)
            passes["protections_total"] = float(passes["oh"] + passes["sc"] + passes["cfi"] + passes["cm"])
    composition_stats = os.path.join(result_directory, "composition.stats")
    if os.path.exists(composition_stats):
        data = json.load(open(composition_stats))
        data['patch_time'] = patch_time
        data['total_time'] = total_time
        data['pass_times'] = passes
        return data
    return {'total_time': 0, 'patch_time': 0, 'pass_times': {}}


# In[12]:


def replace_name(p):
    return p.replace('.bc', '').         replace('.x', '').         replace('_testapp', '').         replace('_game', '').         replace('_large', '-l').         replace('_small', '-s').         replace('raw', '').         replace('search', 'srch').         replace('sort', 'srt').         replace('basicmath', 'bm').         replace('dijkstra', 'dkstra')


# In[13]:


def process_results(df):
    grouped = df.groupby([df['program'], df['coverage'], df['attempt']])
    return grouped.agg([np.median, np.mean, np.std])


# In[14]:


df = process_files("/home/sip/eval/binaries")
df = df.fillna(0)
df = df.drop(columns=['combination'])
df = df[['program', 'attempt', 'coverage', 'actualManifests', 'proposedManifests', 'cycles', 'conflicts',
         'timeConflictDetection', 'timeConflictResolving', 'timeGraphConstruction', 'total_time',
         'pass_times.protections_total', 'patch_time', 'pass_times.cf', 'pass_times.cm', 'pass_times.cfi',
         'pass_times.sc', 'pass_times.oh']]
df = process_results(df).sort_values(['program', 'coverage'])


# In[15]:


df = df.fillna(0)
df.columns = df.columns.map('_'.join)
df = df.reset_index()


# In[16]:


for attempt in df['attempt'].unique():
    for coverage in df['coverage'].unique():
        cdf = df[df['coverage'] == coverage]
        cdf.to_csv(os.path.join("/home/sip/eval/binaries", "time-{}-{}.csv".format(attempt, coverage)), index=False)


# In[17]:


df.to_csv(os.path.join("/home/sip/eval/binaries", "time.csv"), index=False)


# In[ ]:




