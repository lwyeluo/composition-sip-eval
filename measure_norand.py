#!/usr/bin/env python
# coding: utf-8

# In[2]:


from __future__ import print_function
import os
import json
import numpy as np
import pandas as pd
from pandas.io.json import json_normalize
import re
from flatten_json import flatten_json
import itertools

FOLDER = "/home/sip/eval/binaries_norand_ohsc"


# In[3]:


def get_immediate_subdirectories(d):
    return filter(os.path.isdir, [os.path.join(d, f) for f in os.listdir(d)])


# In[4]:


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
                    results = flatten_json(results)
                    df = json_normalize(data=results)

                    percent_columns = {'stats_numberOfProtectedInstructions': 'instructions_protected_percent',
                                       'stats_numberOfProtectedDistinctInstructions': 'distinct_instructions_protected_percent',
                                       'stats_numberOfDistinctImplicitlyProtectedInstructions': 'distinct_implicit_instructions_protected_percent',
                                       'stats_numberOfImplicitlyProtectedInstructions': 'implicit_instructions_protected_percent',
                                       'stats_numberOfProtectedInstructionsByType_oh_assert': 'instructions_oh_assert_percent',
                                       'stats_numberOfProtectedInstructionsByType_oh_hash': 'instructions_oh_hash_percent',
                                       'stats_numberOfProtectedInstructionsByType_sroh_assert': 'instructions_sroh_assert_percent',
                                       'stats_numberOfProtectedInstructionsByType_sroh_hash': 'instructions_sroh_hash_percent',
                                       'stats_numberOfProtectedInstructionsByType_sc': 'instructions_sc_percent',
                                       'stats_numberOfProtectedInstructionsByType_cfi': 'instructions_cfi_percent',
                                       'stats_numberOfProtectedInstructionsByType_cm': 'instructions_cm_percent'}

                    for col, newName in percent_columns.iteritems():
                        if col in df:
                            df[newName] = df[col] / df['stats_numberOfAllInstructions']
                        else:
                            df[newName] = 0

                    df.insert(0, 'attempt', int(attempt))
                    df.insert(0, 'combination', int(combination))
                    df.insert(0, 'coverage', int(coverage))
                    df.insert(0, 'program', replace_name(program))
                    all_df = all_df.append(df, sort=False)
    return all_df


# In[5]:


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
                elif name == "Instruments bitcode with guards":
                    passes["sc"] = value
                elif name == "Constraint Protection Pass":
                    cf_time += value
                elif name == "Constraint Graph Pass":
                    cf_time += value
                elif name == "Constraint Analysis Pass":
                    cf_time += value

            passes["protections_total"] = sum(passes.values())
            passes["cf"] = float(cf_time)
    composition_stats = os.path.join(result_directory, "composition.stats")
    if os.path.exists(composition_stats):
        data = json.load(open(composition_stats))
        data['patch_time'] = patch_time
        data['total_time'] = total_time
        data['pass_times'] = passes
        return data
    return {'total_time': 0, 'patch_time': 0, 'pass_times': {}}


# In[6]:


def replace_name(p):
    return p.replace('.bc', '').         replace('.x', '').         replace('_testapp', '').         replace('_game', '').         replace('_large', '-l').         replace('_small', '-s').         replace('raw', '').         replace('search', 'srch').         replace('sort', 'srt').         replace('basicmath', 'bm').         replace('dijkstra', 'dkstra')


# In[7]:


df = process_files(FOLDER)

columns = {'actualManifests': 'manifests',
           'proposedManifests': 'manifests_proposed',

           'pass_times_protections_total': 'time_protection',
           'pass_times_cf': 'time_cf',
           'pass_times_oh': 'time_oh',
           'pass_times_sroh': 'time_sroh',
           'pass_times_sc': 'time_sc',
           'pass_times_cfi': 'time_cfi',
           'pass_times_cm': 'time_cm',

           'stats_functionConnectivity_avg': 'function_connectivity_avg',
           'stats_functionConnectivity_std': 'function_connectivity_std',
           'stats_functionConnectivity_variance': 'function_connectivity_variance',

           'stats_instructionConnectivity_avg': 'instruction_connectivity_avg',
           'stats_instructionConnectivity_std': 'instruction_connectivity_std',
           'stats_instructionConnectivity_variance': 'instruction_connectivity_variance',

           'stats_numberOfAllInstructions': 'instructions',
           'stats_numberOfDistinctImplicitlyProtectedInstructions': 'distinct_implicit_instructions_protected',
           'stats_numberOfImplicitlyProtectedInstructions': 'implicit_instructions_protected',

           'stats_numberOfManifests': 'drop',
           'stats_numberOfProtectedInstructions': 'instructions_protected',
           'stats_numberOfProtectedDistinctInstructions': 'distinct_instructions_protected',
           'stats_numberOfProtectedFunctions': 'functions_protected',

           'stats_numberOfProtectedFunctionsByType_oh_assert': 'functions_oh_assert',
           'stats_numberOfProtectedFunctionsByType_oh_hash': 'functions_oh_hash',
           'stats_numberOfProtectedFunctionsByType_sroh_assert': 'functions_sroh_assert',
           'stats_numberOfProtectedFunctionsByType_sroh_hash': 'functions_sroh_hash',
           'stats_numberOfProtectedFunctionsByType_sc': 'functions_sc',
           'stats_numberOfProtectedFunctionsByType_cfi': 'functions_cfi',
           'stats_numberOfProtectedFunctionsByType_cm': 'functions_cm',

           'stats_numberOfProtectedInstructionsByType_oh_assert': 'instructions_oh_assert',
           'stats_numberOfProtectedInstructionsByType_oh_hash': 'instructions_oh_hash',
           'stats_numberOfProtectedInstructionsByType_sroh_assert': 'instructions_sroh_assert',
           'stats_numberOfProtectedInstructionsByType_sroh_hash': 'instructions_sroh_hash',
           'stats_numberOfProtectedInstructionsByType_sc': 'instructions_sc',
           'stats_numberOfProtectedInstructionsByType_cfi': 'instructions_cfi',
           'stats_numberOfProtectedInstructionsByType_cm': 'instructions_cm',

           'stats_protectionConnectivity_oh_hash_0_avg': 'function_connectivity_oh_hash_avg',
           'stats_protectionConnectivity_oh_hash_0_std': 'function_connectivity_oh_hash_std',
           'stats_protectionConnectivity_oh_hash_0_variance': 'function_connectivity_oh_hash_variance',
           'stats_protectionConnectivity_oh_hash_1_avg': 'instruction_connectivity_oh_hash_avg',
           'stats_protectionConnectivity_oh_hash_1_std': 'instruction_connectivity_oh_hash_std',
           'stats_protectionConnectivity_oh_hash_1_variance': 'instruction_connectivity_oh_hash_variance',

           'stats_protectionConnectivity_oh_assert_0_avg': 'function_connectivity_oh_assert_avg',
           'stats_protectionConnectivity_oh_assert_0_std': 'function_connectivity_oh_assert_std',
           'stats_protectionConnectivity_oh_assert_0_variance': 'function_connectivity_oh_assert_variance',
           'stats_protectionConnectivity_oh_assert_1_avg': 'instruction_connectivity_oh_assert_avg',
           'stats_protectionConnectivity_oh_assert_1_std': 'instruction_connectivity_oh_assert_std',
           'stats_protectionConnectivity_oh_assert_1_variance': 'instruction_connectivity_oh_assert_variance',

           'stats_protectionConnectivity_sroh_hash_0_avg': 'function_connectivity_sroh_hash_avg',
           'stats_protectionConnectivity_sroh_hash_0_std': 'function_connectivity_sroh_hash_std',
           'stats_protectionConnectivity_sroh_hash_0_variance': 'function_connectivity_sroh_hash_variance',
           'stats_protectionConnectivity_sroh_hash_1_avg': 'instruction_connectivity_sroh_hash_avg',
           'stats_protectionConnectivity_sroh_hash_1_std': 'instruction_connectivity_sroh_hash_std',
           'stats_protectionConnectivity_sroh_hash_1_variance': 'instruction_connectivity_sroh_hash_variance',

           'stats_protectionConnectivity_sroh_assert_0_avg': 'function_connectivity_sroh_assert_avg',
           'stats_protectionConnectivity_sroh_assert_0_std': 'function_connectivity_sroh_assert_std',
           'stats_protectionConnectivity_sroh_assert_0_variance': 'function_connectivity_sroh_assert_variance',
           'stats_protectionConnectivity_sroh_assert_1_avg': 'instruction_connectivity_sroh_assert_avg',
           'stats_protectionConnectivity_sroh_assert_1_std': 'instruction_connectivity_sroh_assert_std',
           'stats_protectionConnectivity_sroh_assert_1_variance': 'instruction_connectivity_sroh_assert_variance',

           'stats_protectionConnectivity_sc_0_avg': 'function_connectivity_sc_avg',
           'stats_protectionConnectivity_sc_0_std': 'function_connectivity_sc_std',
           'stats_protectionConnectivity_sc_0_variance': 'function_connectivity_sc_variance',
           'stats_protectionConnectivity_sc_1_avg': 'instruction_connectivity_sc_avg',
           'stats_protectionConnectivity_sc_1_std': 'instruction_connectivity_sc_std',
           'stats_protectionConnectivity_sc_1_variance': 'instruction_connectivity_sc_variance',

           'stats_protectionConnectivity_cfi_0_avg': 'function_connectivity_cfi_avg',
           'stats_protectionConnectivity_cfi_0_std': 'function_connectivity_cfi_std',
           'stats_protectionConnectivity_cfi_0_variance': 'function_connectivity_cfi_variance',
           'stats_protectionConnectivity_cfi_1_avg': 'instruction_connectivity_cfi_avg',
           'stats_protectionConnectivity_cfi_1_std': 'instruction_connectivity_cfi_std',
           'stats_protectionConnectivity_cfi_1_variance': 'instruction_connectivity_cfi_variance',

           'stats_protectionConnectivity_cm_0_avg': 'function_connectivity_cm_avg',
           'stats_protectionConnectivity_cm_0_std': 'function_connectivity_cm_std',
           'stats_protectionConnectivity_cm_0_variance': 'function_connectivity_cm_variance',
           'stats_protectionConnectivity_cm_1_avg': 'instruction_connectivity_cm_avg',
           'stats_protectionConnectivity_cm_1_std': 'instruction_connectivity_cm_std',
           'stats_protectionConnectivity_cm_1_variance': 'instruction_connectivity_cm_variance',
           }

df.rename(columns=columns, inplace=True)
for col in columns.values():
    if col not in df:
        df.insert(len(df.columns), col, 0)
df = df.drop(columns=['drop'])
df.to_csv("/tmp/tmp_data.pandas", sep=',', encoding='utf-8', index=False)


# In[ ]:


df = pd.read_csv("/tmp/tmp_data.pandas", sep=',', encoding='utf-8')

df = df.fillna(0)
df = df.drop(columns=['combination'])


# In[ ]:


grouped = df.groupby([df['program'], df['coverage'], df['attempt']])


# In[ ]:


target_cols = ['conflicts', 'cycles', 'vertices', 'edges', 'patch_time', 'total_time', 'manifests',
               'manifests_proposed', 'instructions',
               'distinct_implicit_instructions_protected', 'implicit_instructions_protected',
               'distinct_instructions_protected',
               'instructions_protected', 'functions_protected', 'functions_oh_assert', 'functions_oh_hash',
               'functions_sroh_assert', 'functions_sroh_assert', 'functions_sroh_hash', 'functions_sc',
               'functions_cfi', 'functions_cm', 'instructions_oh_assert', 'instructions_oh_hash',
               'instructions_sroh_assert', 'instructions_sroh_hash', 'instructions_sc',
               'instructions_cfi', 'instructions_cm', 'time_protection', 'time_cf', 'time_sc', 'time_oh', 'time_sroh',
               'time_cm', 'time_cfi',
               'timeConflictDetection', 'timeConflictResolving', 'timeGraphConstruction',

               'instructions_protected_percent', 'distinct_instructions_protected_percent',
               'distinct_implicit_instructions_protected_percent', 'implicit_instructions_protected_percent',
               'instructions_oh_assert_percent', 'instructions_oh_hash_percent',
               'instructions_sroh_assert_percent', 'instructions_sroh_hash_percent', 'instructions_sc_percent',
               'instructions_cfi_percent', 'instructions_cm_percent',
               ]

avg_columns = ['function_connectivity_avg', 'instruction_connectivity_avg',
               'function_connectivity_oh_hash_avg', 'instruction_connectivity_oh_hash_avg',
               'function_connectivity_oh_assert_avg', 'instruction_connectivity_oh_assert_avg',
               'function_connectivity_sroh_hash_avg', 'instruction_connectivity_sroh_hash_avg',
               'function_connectivity_sroh_assert_avg', 'instruction_connectivity_sroh_assert_avg',
               'function_connectivity_sc_avg', 'instruction_connectivity_sc_avg',
               'function_connectivity_cfi_avg', 'instruction_connectivity_cfi_avg',
               'function_connectivity_cm_avg', 'instruction_connectivity_cm_avg']

variance_columns = ['function_connectivity_variance', 'instruction_connectivity_variance',
                    'function_connectivity_oh_hash_variance', 'instruction_connectivity_oh_hash_variance',
                    'function_connectivity_cm_variance', 'instruction_connectivity_oh_assert_variance',
                    'function_connectivity_sroh_hash_variance', 'instruction_connectivity_sroh_hash_variance',
                    'instruction_connectivity_sroh_assert_variance', 'function_connectivity_sroh_assert_variance',
                    'function_connectivity_sc_variance', 'instruction_connectivity_sc_variance',
                    'function_connectivity_cfi_variance', 'instruction_connectivity_cfi_variance',
                    'function_connectivity_oh_assert_variance', 'instruction_connectivity_cm_variance']

standard_agg = {col: [np.median, np.mean, np.std] for col in target_cols}
avg_agg = {col: [np.mean] for col in avg_columns}
var_agg = {col: {"std": lambda x: np.sqrt(x.mean())} for col in variance_columns}

aggs = dict(itertools.chain(standard_agg.iteritems(), avg_agg.iteritems()))
aggs = dict(itertools.chain(aggs.iteritems(), var_agg.iteritems()))

result = grouped.agg(aggs)
result = result.fillna(0)

result = result.sort_values(['program', 'coverage'])
df = result.round(2)


# In[ ]:


df = df.fillna(0)
df.columns = df.columns.map('_'.join)
df = df.reset_index()


# In[ ]:


for attempt in df['attempt'].unique():
    for coverage in df['coverage'].unique():
        cdf = df[(df['coverage'] == coverage) & (df['attempt'] == attempt)]
        cdf.to_csv(os.path.join(FOLDER, "time-{}-{}.csv".format(attempt, coverage)), index=False)


# In[ ]:


df.to_csv(os.path.join(FOLDER, "time.csv"), index=False)

