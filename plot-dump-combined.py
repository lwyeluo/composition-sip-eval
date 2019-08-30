import numpy as np
import matplotlib
#matplotlib.use("gtk")
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['hatch.color'] = 'b'
from pprint import pprint
import json
import os
import argparse
import matplotlib.ticker as ticker
PROGRAM_TO_SHOW=['dijkstra_large.x.bc']#'2048_game.bc','basicmath_large.x.bc','basicmath_small.x.bc','bf.x.bc','crc.x.bc','qsort_large.x.bc','qsort_small.x.bc','search_small.x.bc.','snake.bc','susan.bc','tetris.bc','','','','','','','','','sha.bc']

def read(file_path):
    data = json.load(open(file_path))
    data = sorted(data, key=lambda x: x['program'])

    overhead = {}
    for program in data:
        if program['coverage'] not in overhead:
            overhead[program['coverage']] = {}
            overhead[program['coverage']]['cpu_means'] = []
            overhead[program['coverage']]['cpu_stds'] = []
            overhead[program['coverage']]['programs'] = []

        if int(program['coverage'])==0:
            overhead[program['coverage']]['cpu_means'].append(program['cputime_mean'])
        else:
            overhead[program['coverage']]['cpu_means'].append(program['cputime_mean'])
        overhead[program['coverage']]['cpu_stds'].append(program['cputime_std'])
        overhead[program['coverage']]['programs'].append(program['program'])

    return overhead[0]['programs'], overhead

def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,'%d' % int(height),ha='center', va='bottom')

def prepare_xtick_labels(coverage_labels, programs, E, N, M):
    # add program name to the labels
    coverage_labels = (coverage_labels + ([''] * E)) * N
    # Append program name to labels
    i = 0
    for p in programs:
        # 2 is index of 25 in the labels, -1 because index starts from 0
        coverage_labels[i] = p
#        coverage_labels[i + 2] = p
        # print 'i:{},M:{}'.format(i, M)
        i += M + E
    return coverage_labels

def overhead_in_percentage(overheads):
    baseline = overheads[0]
    for overhead_key in overheads.keys():
        if overhead_key is 0:
            continue
        overheads[overhead_key]['perc_cpu_means'] =[]
        overheads[overhead_key]['perc_cpu_stds'] =[]
        i =0
        scale=[]
        for cpu_mean in overheads[overhead_key]['cpu_means']:
            cpu_scale = 0
            perc_cpu_mean = 0
            if baseline['cpu_means'][i] != 0:
                cpu_scale = (cpu_mean - baseline['cpu_means'][i]) / baseline['cpu_means'][i]
                perc_cpu_mean = (cpu_mean - baseline['cpu_means'][i]) / baseline['cpu_means'][i] *100  
            scale.append(cpu_scale)
            overheads[overhead_key]['perc_cpu_means'].append(perc_cpu_mean)
            i+=1
        i=0
        for cpu_std in overheads[overhead_key]['cpu_stds']:
            perc_cpu_std = 0
            if overheads[overhead_key]['cpu_means'][i] !=0:
                perc_cpu_std = scale[i] *cpu_std / overheads[overhead_key]['cpu_means'][i] *100#(cpu_std - baseline['cpu_stds'][i]) / cpu_std *100  
            overheads[overhead_key]['perc_cpu_stds'].append(perc_cpu_std)
            i+=1
    #pprint (overheads)
    return overheads
def reject_outliers(data, m = 100):
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d/mdev if mdev else 0.
    return data[s<m]
def main():
        parser = argparse.ArgumentParser()
        parser.add_argument('-p',action='store', dest='percentage', help='Display overhead in percentage, default is ms',required=False,type=bool,default=False)
        parser.add_argument('-n',action='store', dest='name',help='Output filename, default is perfromance-evaluation-[percentage]',required=False, type=str, default=None)
        parser.add_argument('-m',action='store', dest='measurefile',help='Path to measurements file',required=False, type=str, default='binaries/measurements.json')
        parser.add_argument('-w',action='store', dest='width',help='Output filename, default is perfromance-evaluation-[percentage]',required=False, type=float, default=0.35)
        results = parser.parse_args()
        OVERHEAD_IN_PERCENTAGE = results.percentage
        programs,overheads = read("binaries-acsac-overhead/measurements-0.json")
        _,overheads_manifest = read("binaries-acsac-manifest/measurements-0.json")
        print ('OVERHEADS')
        perc_overheads = overhead_in_percentage(overheads)
        perc_overheads_manifest = overhead_in_percentage(overheads_manifest)
        program_count=len(overheads[0]['programs'])
        coverage_labels=[]
        E = 1 # number of empty gaps between programs
        N = program_count #Number of programs in the dataset len(overheads)
        M = len(overheads) #number of different coverages
        if OVERHEAD_IN_PERCENTAGE:
            M=M-1
        fig, ax = plt.subplots()
        width=results.width
	#ind_width=0.00
        print ('program count:', N, ' coverage count:', M)
        ind = np.arange(0,program_count * (M+E) * width,width) #Number of bars we need is in total N (programs) times M (coverages)
        print ('total columns:',len(ind))
	#exit(1)
        rects = []
        coverage_color={}
        if not OVERHEAD_IN_PERCENTAGE:
            coverage_color[0] = 'w'
        coverage_color[10] = '#dce1ea'
        coverage_color[50] = '#a4a7ad'
        coverage_color[100] = '#83868c'
        coverage_color[25] = 'w'
        coverage_hatch={}
        if not OVERHEAD_IN_PERCENTAGE:
            coverage_hatch[0] = '//'
        coverage_hatch[10] = '0'
        coverage_hatch[50] = 'x'
        coverage_hatch[100] = 'o'
        coverage_hatch[25] = "."
        
        means_dic_name = 'cpu_means'
        stds_dic_name = 'cpu_stds'
        if OVERHEAD_IN_PERCENTAGE:
            means_dic_name = 'perc_cpu_means'
            stds_dic_name = 'perc_cpu_stds'

        coverage_keys = overheads.keys()
        coverage_keys = map(int,coverage_keys)
        coverage_keys.sort()
        coverage_keys = map(str,coverage_keys)
	#keys(1)
        i =0
        diffsum = []
        print "Overhead averages for combinations"
        for coverage in coverage_keys:
	    #cpu_means.append(overhead['cpu_mean'])
	    #cpu_stds.append(overhead['cpu_std'])
            if int(coverage) == 0 and OVERHEAD_IN_PERCENTAGE:
                continue
            coverage_labels.append('') 
            ax_color = coverage_color[int(coverage)]
            ax_hatch = coverage_hatch[int(coverage)]
            columns = ind[i:len(ind)-1:M+E]
             
            means_arr = np.pad(np.array(overheads[int(coverage)][means_dic_name]),(0,len(columns)-len(overheads[int(coverage)][means_dic_name])),'constant')
            means_arr_manifest = np.pad(np.array(overheads_manifest[int(coverage)][means_dic_name]),(0,len(columns)-len(overheads_manifest[int(coverage)][means_dic_name])),'constant')
            #print(zip(programs,means_arr))
            #print(means_arr_manifest)
            diff = np.subtract(means_arr_manifest, means_arr)
            #pprint(zip(programs,diff))
            if len(diffsum) ==0:
                diffsum = diff
            else:
                diffsum = np.add(diffsum, diff)
            stds_arr = np.pad(np.array(overheads[int(coverage)][stds_dic_name]),(0,len(columns)-len(overheads[int(coverage)][stds_dic_name])),'constant')
            stds_arr_sc = np.pad(np.array(overheads_manifest[int(coverage)][stds_dic_name]),(0,len(columns)-len(overheads_manifest[int(coverage)][stds_dic_name])),'constant')
            
            #means_arr = np.subtract(means_arr, means_arr_manifest)
            rects2 = ax.bar(columns,means_arr_manifest, width, color=ax_color,edgecolor='gray', capsize=3)#,tick_label=[coverage]*N)
            rects1 = ax.bar(columns,means_arr, width, color=ax_color, edgecolor='black', capsize=2, error_kw={'ecolor':'red','linewidth':00.1,'alpha':0.4}, yerr=stds_arr,label=coverage+'%')#,tick_label=[coverage]*N)
            i+=1
            rects.append(rects1)
            print coverage,"OPTIMIZED MEAN:",np.mean(means_arr), " STD:", np.std(means_arr)
            print coverage,"MANIFEST MEAN:",np.mean(means_arr_manifest), " STD:", np.std(means_arr_manifest)
        #print(diffsum)
        ax.set_ylabel('Overhead in percentage')
        t = np.arange(np.min(ind),np.max(ind)+1, width)
        ax.set_xticks(np.arange(np.min(ind),np.max(ind)+1, width))
        ax.set_xticklabels(prepare_xtick_labels(coverage_labels,programs,E,N,M))
        ax.set_yscale('log',basey=2)
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: '{:g}'.format(y)))
        plt.xticks(rotation=60)
        plt.legend(bbox_to_anchor=(0., 1.02, 1., .102),loc='upper right', ncol=4, mode="expand", borderaxespad=0.)
        plt.subplots_adjust(bottom=0.30)
        fig_name = 'performance-evaluation'
        if OVERHEAD_IN_PERCENTAGE:
            fig_name+='-combined-percentage.pdf'
        else:
            fig_name+='combined.pdf'
        if results.name:
            fig_name=results.name
        plt.ion()
        fig.set_size_inches(8.7,4.0)
        fig.savefig(fig_name,bbox_inches='tight')
        plt.show()


if __name__== "__main__":
	main()



