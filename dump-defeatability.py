import os
import json
import numpy as np
import pandas as pd
from pandas.io.json import json_normalize
from itertools import islice
import pprint
import shutil
import sys

def get_immediate_subdirectories(d):
    return filter(os.path.isdir, [os.path.join(d, f) for f in os.listdir(d)])


def process_files(directory):
    all_df = pd.DataFrame()
    directory_name=os.path.basename(directory)
    print(directory)
    for program_dir in get_immediate_subdirectories(directory):
        program = os.path.basename(program_dir)
        for coverage_dir in sorted(get_immediate_subdirectories(program_dir)):
            coverage = os.path.basename(coverage_dir)
            #no defeatability results to extract from coverage 0
            if int(coverage)==0:
                continue
            for combination_dir in get_immediate_subdirectories(coverage_dir):
                print(combination_dir)
                combination = os.path.basename(combination_dir)
                for attempt_dir in get_immediate_subdirectories(combination_dir):
                    result_path = os.path.join(attempt_dir,'defeatability.json')
                    print (result_path)
                    attempt = os.path.basename(attempt_dir)

                    mean, median, std = grab_results(result_path)

                    df = json_normalize(data={'coverage':int(coverage),'combination':int(combination),'mean':mean, 'median':median,'std':std})
                    df.insert(0, 'program', program)
                    #print(df)
                    all_df = all_df.append(df, sort=False)

    #all_df.columns+=directory_name
    #all_df = all_df.rename(columns={'program'+directory_name:'program'})
    #print(all_df)
    return all_df


def grab_results(path):
    stats = json.load(open(path))
    
    mean = float(stats['mean'])
    median = float(stats['median'])
    std = float(stats['std'])
    return mean, median, std


def main():
    if len(sys.argv) <2:
      print('At least one path need to be specified')
      exit(1)
    for path in sys.argv[1:]:
      print('Reading constraints from ', path)
      df = process_files(path)
      df = df.reset_index()
#    df = df.drop(columns=['Name'])
      out = df.to_csv(index=False)
      with open('{}-extracted-defeatability.csv'.format(path.replace('/','')), 'w') as f:
        f.write(out)
if __name__ == '__main__':
    main()
