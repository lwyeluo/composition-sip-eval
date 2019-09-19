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
from enum import Enum
from measure import replace_name
import sys
# In[33]:


class Objective(Enum):
    EXPLICIT=1
    IMPLICIT=2
    OVERHEAD=3
    MANIFEST=4

def get_immediate_subdirectories(d):
    return filter(os.path.isdir, [os.path.join(d, f) for f in os.listdir(d)])


# In[34]:

def read_measurements(path):
    with open(path) as f:
      return json.load(f)
def process_files(directory,objective):
    all_df = pd.DataFrame()
    performance_baseline_path = os.path.join(directory,'measurements-0.json')
    performance_100_path = os.path.join(directory,'measurements-1.json')
    perf_base=perf_100 = []
    if os.path.exists(performance_baseline_path):
      perf_base = read_measurements(performance_baseline_path)
    if os.path.exists(performance_100_path):
      perf_100 = read_measurements(performance_100_path)
    for program_dir in get_immediate_subdirectories(directory):
        program = os.path.basename(program_dir)
        for coverage_dir in sorted(get_immediate_subdirectories(program_dir)):
            coverage = os.path.basename(coverage_dir)
            #no ilp results to extract from coverage 0
            if int(coverage)==0:
                continue
            for combination_dir in get_immediate_subdirectories(coverage_dir):
                print(combination_dir)
                combination = os.path.basename(combination_dir)
                for attempt_dir in get_immediate_subdirectories(combination_dir):
                    result_path = attempt_dir
     #               print (result_path)
                    attempt = os.path.basename(attempt_dir)

                    ilp_results,state_results = grab_results(result_path,objective)
                    if ilp_results == None:
                        ilp_results = {'manifest':state_results['manifest'], 'explicit':state_results['explicit'], 'implicit':state_results['implicit'], 'overhead':0}
                    #get perf numbers if available
                    cpu_base_median = get_cpu_median_from_perf(perf_base,program,0)
                    cpu_100_median = get_cpu_median_from_perf(perf_100,program,100)
                    overhead = (cpu_100_median - cpu_base_median)/cpu_base_median*100
                    print(cpu_base_median,cpu_100_median) 
                    df = json_normalize(data={'coverage':int(coverage),'combination':int(combination),'ilp_result':ilp_results,'stats_result':state_results,'overhead_median_percentage':overhead})
                    df.insert(0, 'program', program)
    #                print(df)
                    all_df = all_df.append(df, sort=False)

    
    all_df.columns+=objective.name
    all_df = all_df.rename(columns={'program'+objective.name:'program'})
    return all_df

def get_cpu_median_from_perf(perf,program,coverage):
  if len(perf)!=0:
    hit = list(filter(lambda p: p['program'] == replace_name(program) and int(p['coverage'])==int(coverage), perf))
    if len(hit)!=0:
      return hit[0]['cputime_median']
    else:
      print('Not FOUND', replace_name(program), coverage)
      print(perf)
      exit(1)
  return 0.0


# In[35]:


def grab_results(result_directory,objective):
    stats_path = os.path.join(result_directory, "composition.stats")
    ilp_solution_path = os.path.join(result_directory, "solution_readable.txt")
    ilp_result = None 
    # {'explicit':0, 'implicit':0, 'overhead':0}
    stats_result = {'explicit':0, 'implicit':0}
    if os.path.exists(ilp_solution_path):
        manifest, explicit, implicit, overhead = read_solution_file(ilp_solution_path,objective)
        ilp_result = {'manifest':manifest,'explicit':explicit, 'implicit':implicit, 'overhead':overhead}
    if os.path.exists(stats_path):    
        manifest, explicit, implicit = read_stats_file(stats_path)
        stats_result = {'manifest':manifest, 'explicit':explicit, 'implicit':implicit}
    return ilp_result, stats_result

def read_stats_file(path):
    stats = json.load(open(path))['stats']
    manifest = int(stats['numberOfManifests'])
    explicit = int(stats['numberOfProtectedDistinctInstructions'])
    implicit = int(stats['numberOfDistinctImplicitlyProtectedInstructions'])
    return manifest, explicit, implicit
def read_solution_file(path,objective):
    with open(path) as f:
       lines = list(islice(f, 12))
    if objective == Objective.MANIFEST:
        manifest = int(lines[5].replace('(MAXimum)','').replace('Objective:','').strip())
        explicit = get_value(lines[9])
        implicit = get_value(lines[10])
        overhead = get_value(lines[11])
        return manifest, explicit, implicit, overhead
    if objective == Objective.EXPLICIT:
        explicit = int(lines[5].replace('(MAXimum)','').replace('Objective:','').strip())
        implicit = get_value(lines[9])
        overhead = get_value(lines[10])
        manifest = get_value(lines[11])
        return manifest, explicit, implicit, overhead
    if objective == Objective.IMPLICIT:
        implicit = int(lines[5].replace('(MAXimum)','').replace('Objective:','').strip())
        explicit = get_value(lines[9])
        overhead = get_value(lines[10])
        manifest = get_value(lines[11])
        return manifest, explicit, implicit, overhead
    if objective == Objective.OVERHEAD:
        overhead = float(lines[5].replace('(MINimum)','').replace('Objective:','').strip())
        explicit = get_value(lines[9])
        implicit = get_value(lines[10])
        manifest = get_value(lines[11])
        return manifest, explicit, implicit, overhead
 
def get_value(line):
    a=line.strip()[1:].replace('explicit','').replace('implicit','').replace('manifest','').replace('overhead','').strip()[:9].strip()
    print(a)
    return float(a)

# In[36]:



# In[37]:


def replace_name(p):
    return p.replace('.bc', '').         replace('.x', '').         replace('_testapp', '').         replace('_game', '').         replace('_large', '-l').         replace('_small', '-s').         replace('raw', '').         replace('search', 'srch').         replace('sort', 'srt').         replace('basicmath', 'bm').         replace('dijkstra', 'dkstra')


# In[38]:

def dump_constraints(df,obj,dirName):
    pp = pprint.PrettyPrinter(indent=4)
    if os.path.exists(dirName):
        shutil.rmtree(dirName)
    os.mkdir(dirName)
    for index,prog in df.iterrows():
        pp.pprint(prog)
        constraint = "-cf-ilp-explicit-bound={0} -cf-ilp-implicit-bound={1} -cf-ilp-overhead-bound={2} ".format(int(prog['ilp_result.explicitMANIFEST']),int(prog['ilp_result.implicitMANIFEST']),prog['ilp_result.overheadMANIFEST'])
#        constraint = "-cf-ilp-implicit-bound={0}  ".format(int(prog['ilp_result.implicitMANIFEST']))
        #constraint = "-cf-ilp-explicit-bound={0} -cf-ilp-overhead-bound={1} ".format(int(prog['ilp_result.explicitMANIFEST']),prog['ilp_result.overheadMANIFEST'])
        filePath = os.path.join(dirName,prog['program'],str(prog['coverage'+obj.name]))
        if not os.path.exists(filePath):
            os.makedirs(filePath) 
        fname =  os.path.join(filePath, str(prog['combination'+obj.name]))
        print(fname)
        f = open(fname, "w") 
        f.write(constraint) 
        f.close() 

def main():
    if len(sys.argv) <2:
      print('The path for constraint extraction need to be specified')
      exit(1)
    path = sys.argv[1]
    print('Reading constraints from ', path)
    df = process_files(path,Objective.MANIFEST)
    df = df.reset_index()
    df = df.drop(columns=['index'])
#    df = df.drop(columns=['Name'])
    out = df.to_json(orient='records')
    outDir = 'constraints'
    if len(sys.argv)==3:
        outDir = sys.argv[2]
    dump_constraints(df,Objective.MANIFEST,outDir)    
    with open('extracted-constraints.json', 'w') as f:
         f.write(out)
if __name__ == '__main__':
    main()
