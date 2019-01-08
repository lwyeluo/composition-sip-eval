#!/usr/bin/env python
from __future__ import print_function
import numpy as np
import matplotlib.pyplot as plt
from pprint import pprint
import json
import argparse


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

        overhead[program['coverage']]['cpu_means'].append(program['cputime_mean'])
        overhead[program['coverage']]['cpu_stds'].append(program['cputime_std'])
        overhead[program['coverage']]['programs'].append(program['program'])

    return overhead[0]['programs'], overhead


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
        overheads[overhead_key]['perc_cpu_means'] = []
        overheads[overhead_key]['perc_cpu_stds'] = []
        i = 0
        scale = []
        for cpu_mean in overheads[overhead_key]['cpu_means']:
            cpu_scale = 0
            perc_cpu_mean = 0
            if baseline['cpu_means'][i] != 0:
                cpu_scale = (cpu_mean - baseline['cpu_means'][i]) / baseline['cpu_means'][i]
                perc_cpu_mean = cpu_scale * 100
            scale.append(cpu_scale)
            overheads[overhead_key]['perc_cpu_means'].append(perc_cpu_mean)
            i += 1
        i = 0
        for cpu_std in overheads[overhead_key]['cpu_stds']:
            perc_cpu_std = 0
            if overheads[overhead_key]['cpu_means'][i] != 0:
                # (cpu_std - baseline['cpu_stds'][i]) / cpu_std *100
                perc_cpu_std = scale[i] * cpu_std / overheads[overhead_key]['cpu_means'][i] * 100
            overheads[overhead_key]['perc_cpu_stds'].append(perc_cpu_std)
            i += 1

    return overheads


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', action='store', dest='percentage', help='Display overhead in percentage, default is ms',
                        required=False, type=bool, default=False)
    parser.add_argument('-n', action='store', dest='name',
                        help='Output filename, default is perfromance-evaluation-[percentage]', required=False,
                        type=str, default=None)
    parser.add_argument('-m', action='store', dest='measuresfile', help='measures file', required=False, type=str,
                        default='binaries/measurements-1.json')
    parser.add_argument('-w', action='store', dest='width',
                        help='Output filename, default is perfromance-evaluation-[percentage]', required=False,
                        type=float, default=0.35)

    results = parser.parse_args()

    OVERHEAD_IN_PERCENTAGE = results.percentage
    programs, overheads = read(results.measuresfile)
    print('OVERHEADS')

    overhead_in_percentage(overheads)

    print(overheads[0]['programs'])
    program_count = len(overheads[0]['programs'])
    coverage_color = {0: 'w', 10: '#dce1ea', 50: '#a4a7ad', 100: '#83868c', 25: 'w'}

    means_dic_name = 'cpu_means'
    stds_dic_name = 'cpu_stds'

    if OVERHEAD_IN_PERCENTAGE:
        means_dic_name = 'perc_cpu_means'
        stds_dic_name = 'perc_cpu_stds'
        del overheads[0]
        del coverage_color[0]

    E = 1  # number of empty gaps between programs
    N = program_count  # Number of programs in the dataset len(overheads)
    M = len(overheads)  # number of different coverages
    fig, ax = plt.subplots()
    width = results.width
    # ind_width=0.00
    print('program count:', N, ' coverage count:', M)
    ind = np.arange(0, program_count * (M + E) * width,
                    width)  # Number of bars we need is in total N (programs) times M (coverages)
    print('total columns:', len(ind))

    coverage_keys = overheads.keys()
    coverage_keys.sort()

    i = 0
    rects = []
    coverage_labels = []
    for coverage in coverage_keys:
        coverage_labels.append('')
        ax_color = coverage_color[coverage]
        print('coverage {} mean:{} std: {} median:{}'.format(coverage, np.mean(overheads[coverage][means_dic_name]),
                                                             np.std(overheads[coverage][means_dic_name]),
                                                             np.median(overheads[coverage][means_dic_name])))
        pprint(zip(programs, overheads[coverage][means_dic_name]))

        columns = ind[i:len(ind) - 1:M + E]

        rects1 = ax.bar(columns, overheads[coverage][means_dic_name], width, color=ax_color, edgecolor='black',
                        capsize=4, error_kw={'ecolor': 'red'}, yerr=overheads[coverage][stds_dic_name],
                        label=str(coverage) + '%')

        i += 1
        rects.append(rects1)
    ax.set_ylabel('Overhead in percentage')

    ax.set_xticks(np.arange(np.min(ind), np.max(ind) + 1, width))
    ax.set_xticklabels(prepare_xtick_labels(coverage_labels, programs, E, N, M))
    ax.set_yscale('log', basey=2)

    plt.xticks(rotation=60)
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='upper right', ncol=M, mode="expand", borderaxespad=0.)

    plt.subplots_adjust(bottom=0.30)
    fig_name = 'performance-evaluation'
    if OVERHEAD_IN_PERCENTAGE:
        fig_name += '-percentage.pdf'
    else:
        fig_name += '.pdf'

    if results.name:
        fig_name = results.name

    plt.ion()
    fig.set_size_inches(8.7, 4.0)
    fig.savefig(fig_name, bbox_inches='tight')
    plt.show()
    print('showing')


if __name__ == "__main__":
    main()
