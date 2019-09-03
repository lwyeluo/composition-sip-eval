#!/usr/bin/env python
# coding: utf-8

# In[32]:


from __future__ import print_function
import os
import json
import numpy as np
import pandas as pd
from pandas.io.json import json_normalize
from itertools import islice
import pprint
import shutil
from constraint_extractor import *

def print_dataframes(df):
    for index,prog in df.iterrows():
         pprint.pprint(prog)
def main():
    df_manifest = process_files("/home/sip/eval/binaries-manifest",Objective.MANIFEST)
    #df = df.reset_index()
    #df = df.drop(columns=['index'])
    #out = df.to_json(orient='records')
    #dump_constraints(df)    
    #with open('extracted-constraints.json', 'w') as f:
    #     f.write(out)
    
    #df_explicit = process_files("/home/sip/eval/binaries-explicit",Objective.EXPLICIT)
    #df_implicit = process_files("/home/sip/eval/binaries-implicit",Objective.IMPLICIT)
    df_overhead = process_files("/home/sip/eval/binaries-overhead",Objective.OVERHEAD)
    
    #df_manifest = df_manifest.fillna(0)
    #df_explicit = df_explicit.fillna(0)
    #df_implicit = df_implicit.fillna(0)
    #df_overhead = df_overhead.fillna(0)
   # print_dataframes(df_explicit)
    #print_dataframes(df_implicit)
    #print_dataframes(df_overhead)
    #re = pd.concat([df_manifest,df_explicit,df_implicit,df_overhead],keys=['program'])    
    re = df_manifest.merge(df_overhead, left_on='program', right_on='program')
    #re = df_manifest.merge(df_explicit, left_on='program', right_on='program')
    #re = re.merge(df_implicit, left_on='program', right_on='program')
    #re = re.merge(df_overhead, left_on='program', right_on='program')
    #df_manifest.to_csv('ilp_optimization_results_manifest.csv')
    #df_implicit.to_csv('ilp_optimization_results_implicit.csv')
    #df_explicit.to_csv('ilp_optimization_results_explicit.csv')
    #df_overhead.to_csv('ilp_optimization_results_overhead.csv')
    re.to_csv('ilp_optimization_results.csv')
    

if __name__ == '__main__':
    main()
