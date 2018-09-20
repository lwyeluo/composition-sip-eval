#!/usr/bin/env python
# coding: utf-8

# In[32]:


from __future__ import print_function
import os
import json
import numpy as np
import pandas as pd
from pandas.io.json import json_normalize


# In[33]:


def get_immediate_subdirectories(d):
    return filter(os.path.isdir, [os.path.join(d, f) for f in os.listdir(d)])


# In[34]:


def process_files(directory):
    all_df = pd.DataFrame()
    for program_dir in get_immediate_subdirectories(directory):
        program = os.path.basename(program_dir)
        for coverage_dir in sorted(get_immediate_subdirectories(program_dir)):
            coverage = os.path.basename(coverage_dir)

            for combination_dir in get_immediate_subdirectories(coverage_dir):
                combination = os.path.basename(combination_dir)

                for attempt_dir in get_immediate_subdirectories(combination_dir):
                    result_path = attempt_dir
                    attempt = os.path.basename(attempt_dir)

                    results = grab_results(result_path)

                    raw = json_normalize(data=results)
                    df = raw[['cputime', 'memory']]
                    df.insert(0, 'attempt', int(attempt))
                    df.insert(0, 'combination', int(combination))
                    df.insert(0, 'coverage', int(coverage))
                    df.insert(0, 'program', replace_name(program))
                    all_df = all_df.append(df, sort=False)

    return all_df


# In[35]:


def grab_results(result_directory):
    runs_path = os.path.join(result_directory, "runs.json")
    if os.path.exists(runs_path):
        return json.load(open(runs_path))
    return [{'cputime': 0, 'memory': 0}]


# In[36]:


def process_results(df):
    grouped = df.groupby([df['program'], df['coverage'], df['attempt']])
    return grouped.agg([np.min, np.max, np.median, np.mean, np.std])


# In[37]:


def replace_name(p):
    return p.replace('.bc', '').         replace('.x', '').         replace('_testapp', '').         replace('_game', '').         replace('_large', '-l').         replace('_small', '-s').         replace('raw', '').         replace('search', 'srch').         replace('sort', 'srt').         replace('basicmath', 'bm').         replace('dijkstra', 'dkstra')


# In[38]:


df = process_files("/home/sip/eval/binaries")
df = df.fillna(0)
df = df.drop(columns=['combination'])
df = process_results(df)
df = df.sort_values(['program', 'coverage'])
df.columns = df.columns.map('_'.join)
df = df.reset_index()
df = df.fillna(0)


# In[39]:


for attempt in df['attempt'].unique():
    adf = df[df['attempt'] == attempt]
    adf.to_csv(os.path.join("/home/sip/eval/binaries", "measurements-{}.csv".format(attempt)), index=False)
    adf.to_json(os.path.join("/home/sip/eval/binaries", "measurements-{}.json".format(attempt)), orient='records')


# In[ ]:




