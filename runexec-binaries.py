#!/usr/bin/env python
# Run benchmarks pseudo code

from __future__ import print_function
import os
import json
from pprint import pprint
import numpy as np
import argparse
from shutil import copyfile
from benchexec.runexecutor import RunExecutor

REPEAT_NUMBER = 1
BASE_REPEAT_NUMBER = 1
RUNS_PROCESSED = "runs_processed.json"
CMDLINE_ARGS = "cmdline-args"
EXIT_CODES = {
    'patricia.x.bc': 256,
    'bf.x.bc': 256,
}
FAULTY_BINARY = "faulty_binary.txt"
LD_PRELOAD = ['/home/dennis/Desktop/self-checksumming/hook/build/libminm.so']


def get_immediate_subdirectories(d):
    return filter(os.path.isdir, [os.path.join(d, f) for f in os.listdir(d)])


def repeats_for_directory(coverage_dir):
    if coverage_dir == '0' or coverage_dir == '100':
        return BASE_REPEAT_NUMBER
    return REPEAT_NUMBER


def read_args(program):
    filename = os.path.join(CMDLINE_ARGS, program + '.runexec')
    if not os.path.isfile(filename):
        filename = os.path.join(CMDLINE_ARGS, program)
        if not os.path.isfile(filename):
            return ''

    with open(filename, 'r') as f:
        return f.read()


def log_faulty_binary(args, program, result):
    with open(FAULTY_BINARY, 'a') as f:
        f.write("{} failed with {} args: {}\n".format(program, result['exitcode'], " ".join(args)))


def measure_overhead(result_directory, program, repeat):
    results = []

    # Check if program exists
    program_path = os.path.join(result_directory, program)
    if not os.path.isfile(program_path):
        print("Did not find binary in path: %s" % program_path)
        return

    # Load CMD args from file
    cmd_args = read_args(program).splitlines()

    # Run loop
    # run runexec repeat times and calculate avg and std
    for i in range(repeat):
        cmd = ''

        # TODO: find a better way to pass args to toast, Dirty hack to get toast working
        if program == 'toast.x.bc':
            output_file = 'cmdline-args/toast_input_small.au.gsm'
            if os.path.isfile(output_file):
                os.remove(output_file)

        # Prepare cmd
        # if program == "rawdaudio.x.bc" or program == "rawcaudio.x.bc":
        #    cmd_file = open("cmd.sh", 'w')
        #    cmd_file.write(program_path)
        #    cmd_file.write(cmd_args)
        #    cmd_file.close()
        #    cmd = 'runexec --container -- sh {}'.format(cmd_file.name)
        # else:
        # cmd = 'runexec --container -- {} {}'.format(program_path, cmd_args)
        # call(["sosylib_measure.sh",program_path])
        # --container throws a suspicious warning, I'm not sure it the measurements are good
        # cmd = 'runexec {} {} --container'.format(program_path,cmd_args)

        # CFI needs to have graph.txt in CWD
        graph_file = os.path.join(result_directory, "graph.txt")
        if os.path.isfile(graph_file):
            copyfile(graph_file, "./graph.txt")

        print(str(i), " trying to run:", program_path)
        env = os.environ
        preload = LD_PRELOAD
        preload.append(os.path.join(result_directory, "librtlib.so"))
        env["LD_PRELOAD"] = ":".join(preload)

        output_log = os.path.join(result_directory, 'output_' + str(i) + '.log')
        args = [program_path]
        args.extend(cmd_args)

        executor = RunExecutor()
        result = executor.execute_run(args=args, output_filename=output_log, environments=env)
        program_exit_code = result['exitcode']

        print("program_exit code:", program_exit_code)
        if int(program_exit_code) != 0 and (program not in EXIT_CODES or EXIT_CODES[program] != program_exit_code):
            print(program, ' Exit code:', program_exit_code,
                  ' faulty program execution!... Check output.log for more info...')

            log_faulty_binary(args, program, result)
            return

        results.append(result)

    # write results to the directory
    if len(results) != 0:
        runs_path = os.path.join(result_directory, 'runs.json')
        with open(runs_path, 'wb') as outfile:
            json.dump(results, outfile)
    else:
        print('Failed to run {} and thus no overhead results were captured'.format(program))
    return results


def process_results(result_path, results):
    # TODO do whatever and add outcome(s) to the results file
    if results is None:
        return
    print("process me", len(results))
    cpu_reads = [float(d['cputime']) for d in results if 'cputime' in d]
    mem_reads = [float(d['memory']) for d in results if 'memory' in d]
    process_result = {}
    print(cpu_reads)

    process_result['cpu_mean'] = np.mean(cpu_reads)
    process_result['cpu_std'] = np.std(cpu_reads)
    process_result['mem_mean'] = np.mean(mem_reads)
    process_result['mem_std'] = np.std(mem_reads)
    pprint(process_result)
    process_result_path = os.path.join(result_path, RUNS_PROCESSED)
    with open(process_result_path, 'wb') as outfile:
        json.dump(process_result, outfile)
    return process_result


def process_files(directory):
    for program_dir in get_immediate_subdirectories(directory):
        for coverage_dir in get_immediate_subdirectories(program_dir):
            for combination_dir in get_immediate_subdirectories(coverage_dir):
                for attempt_dir in get_immediate_subdirectories(combination_dir):
                    result_path = attempt_dir

                    # if processed file already exists, do not run the program again
                    processed_runs_file = os.path.join(result_path, RUNS_PROCESSED)
                    if os.path.exists(processed_runs_file):
                        continue

                    repeat = repeats_for_directory(coverage_dir)
                    results = measure_overhead(result_path, os.path.basename(program_dir), repeat)
                    process_results(result_path, results)


def main():
    parser = argparse.ArgumentParser(description='Run all generated binaries and measure performance overhead.')
    parser.add_argument('dir', metavar='DIR', type=str, help='Directory of the binaries to run.')
    args = parser.parse_args()

    binary_dir = os.path.abspath(args.dir)
    if not os.path.isdir(os.path.abspath(args.dir)):
        parser.print_help()
        return

    process_files(binary_dir)


if __name__ == "__main__":
    main()
