#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Module to generate experiments for BEST operator (incremental algorithms)
'''

import csv
import os
import random


# Experiment parameters
ATT = 'att'
TUP = 'tup'
DEL = 'del'
INS = 'ins'
RUL = 'rul'
LEV = 'lev'
IND = 'ind'
ALGORITHM = 'algorithm'

# Result fields
RUNTIME = 'runtime'
MEMORY = 'memory'
FIRST = 'first'
OTHERS = 'others'

# System attributes for StremPref tables
TS_ATT = '_TS'
OP_ATT = '_FL'

# Parameter values related to generation of table data
# Max value for attributes
MAX_VALUE = 63
# List of attributes number
ATTRIBUTE_LIST = [8, 16, 32, 64]
# Default attributes number
ATTRIBUTE_DEFAULT = 8
# List of tuples number
TUPLE_LIST = [500, 1000, 2000, 4000, 8000]
# Default tuples number
TUPLE_DEFAULT = 1000
# Maximum tuple number
TUPLE_MAX = TUPLE_LIST[-1]
# List of deletions
DELETION_LIST = [50, 100, 200, 400]
# Default deletions
DELETION_DEFAULT = 50
# List of insertions
INSERTION_LIST = [50, 100, 200, 400]
# Default insertions
INSERTION_DEFAULT = 50

# Default iteration number
ITERATION_DEFAULT = 100

# Parameter values related to preference queries
# List of rules number
RULES_LIST = [2, 4, 8, 16, 32]
# Default rules number
RULES_DEFAULT = 8
# List of levels
LEVEL_LIST = [1, 2, 4, 8]
# Default level
LEVEL_DEFAULT = 2
# Indifferent attributes list
INDIFF_LIST = [0, 1, 2, 4]
# Default indifferent attributes
INDIFF_DEFAULT = 4

# List of algorithms
ALGORITHM_LIST = ['inc_ancestors', 'inc_graph', 'inc_partition', 'partition']

# Number of experiment runs
RUN_COUNT = 5

# Preference rules format
RULE_STRING = 'IF A1 = {c1} AND A2 = {c2} THEN A3 = {b} BETTER A3 = {w} {i}'

# Query
QUERY = '''SELECT * FROM r
ACCORDING TO PREFERENCES
{p};'''

# Directories
MAIN_DIR = 'pref'
DETAILS_DIR = MAIN_DIR + os.sep + 'details'
RUNTIME_SUMMARY_DIR = MAIN_DIR + os.sep + 'runtime_summary'
MEMORY_SUMMARY_DIR = MAIN_DIR + os.sep + 'memory_summary'
RUNTIME_RESULT_DIR = MAIN_DIR + os.sep + 'runtime_result'
MEMORY_RESULT_DIR = MAIN_DIR + os.sep + 'memory_result'
QUERIES_DIR = MAIN_DIR + os.sep + 'queries'
DATA_DIR = MAIN_DIR + os.sep + 'data'
ENV_DIR = MAIN_DIR + os.sep + 'env'

# Command for experiment run
RUN_COMMAND = \
    "streampref -p {alg} -e " + ENV_DIR + os.sep + "{id}.env -d {det} -m {max}"
# Command for calculation of confidence interval
CONFINTERVAL_COMMAND = \
    "confinterval.py -i {inf} -o {outf} -k {keyf}"


def gen_insert_records(tup_number, att_number):
    '''
    Generate record to insert
    '''
    # List of records
    rec_list = []
    # Loop to count the tuples number
    for _ in range(tup_number):
        # new tuple record
        new_record = {}
        # List of attributes
        att_list = ['A' + str(number + 1) for number in range(att_number)]
        # Generate each attribute value
        for att in att_list:
            new_record[att] = random.randint(0, MAX_VALUE)
        # Append record into list of records
        rec_list.append(new_record)
    # Return built record list
    return rec_list


def gen_delete_records(record_list, tup_number):
    '''
    Generate record to be deleted from a given list of records
    '''
    # Shuffle record list
    random.shuffle(record_list)
    # Copy last 'tup_number" records to deleted list
    deleted_list = record_list[:tup_number]
    # Delete copied records
    del record_list[:tup_number]
    return deleted_list


def store_records(filename, record_list, att_number, timestamp, operation='+'):
    '''
    Store a record list in file table using StremPref format
    '''
    # Check if record list is empty
    if not len(record_list):
        return
    # Build attribute list including timestamp and operation
    att_list = [TS_ATT, OP_ATT] + \
        ['A' + str(number + 1) for number in range(att_number)]
    # Open file
    out_file = open(filename, 'a')
    out_write = csv.DictWriter(out_file, att_list)
    # Write file header (if file is empty)
    if out_file.tell() == 0:
        out_write.writeheader()
    # Write records to file
    for rec in record_list:
        # Copy to preserve original record in the list
        copy_rec = rec.copy()
        # Add attributes _FL ant _TS
        copy_rec[TS_ATT] = timestamp
        copy_rec[OP_ATT] = operation
        out_write.writerow(copy_rec)
    out_file.close()


def get_table_id(exp_conf):
    '''
    Return a table ID for given parameters
    '''
    return ATT + str(exp_conf[ATT]) + \
        TUP + str(exp_conf[TUP]) + \
        DEL + str(exp_conf[DEL]) + \
        INS + str(exp_conf[INS])


def get_query_id(exp_conf):
    '''
    Return a query ID for given parameters
    '''
    return RUL + str(exp_conf[RUL]) + \
        LEV + str(exp_conf[LEV]) + \
        IND + str(exp_conf[IND])


def get_experiment_id(exp_conf):
    '''
    Return the ID of an experiment
    '''
    return get_table_id(exp_conf) + get_query_id(exp_conf)


def gen_table(exp_conf):
    '''
    Generate table
    '''
    table_id = get_table_id(exp_conf)
    filename = DATA_DIR + os.sep + table_id + '.csv'
    if os.path.isfile(filename):
        return
    # Clear file
    out_file = open(filename, 'w')
    out_file.close()
    # Generate initial list of tuples
    current_list = gen_insert_records(exp_conf[TUP], exp_conf[ATT])
    # Store initial list on file
    store_records(filename, current_list, exp_conf[ATT], 0)
    # Generate record for each iteration
    for timestamp in range(1, ITERATION_DEFAULT):
        delete_list = gen_delete_records(current_list, exp_conf[DEL])
        store_records(filename, delete_list, exp_conf[ATT], timestamp,
                      '-')
        insert_list = gen_insert_records(exp_conf[INS],
                                         exp_conf[ATT])
        current_list += insert_list
        store_records(filename, insert_list, exp_conf[ATT], timestamp)


def gen_all_tables(experiment_list):
    '''
    Generate all tables
    '''
    for exp_rec in experiment_list:
        gen_table(exp_rec)


def gen_rule(rule_dict):
    '''
    Convert rule dictionary into rule in string format
    '''
    return RULE_STRING.format(c1=rule_dict['COND1'],
                              c2=rule_dict['COND2'],
                              b=rule_dict['BEST'],
                              w=rule_dict['WORST'],
                              i=rule_dict['INDIFF'])


def gen_rules(exp_conf):
    '''
    Generate preference rules
    '''
    # Preference level
    current_level = 0
    # Values for attributes of rule condition
    cond1 = 1
    cond2 = 1
    # Preferred value
    pref_value = 1
    # Indifferent attributes
    indiff_list = []
    # Build list of indifferent attributes
    indiff_str = ''
    if exp_conf[IND] > 0:
        # Indifferent attributes start in A4
        for att_cont in range(exp_conf[IND]):
            indiff_list.append('A' + str(att_cont + 4))
        indiff_str = '[' + ', '.join(indiff_list) + ']'
    # Build rules list
    rules_list = []
    for _ in range(exp_conf[RUL]):
        rule_dict = {}
        rule_dict['COND1'] = cond1
        rule_dict['COND2'] = cond2
        rule_dict['BEST'] = pref_value
        pref_value += 1
        rule_dict['WORST'] = pref_value
        current_level += 1
        # Check if maximum level have been reached
        if current_level == exp_conf[LEV]:
            current_level = 0
            pref_value = 1
            cond2 += 1
        # Check if maximum values have been reached
        if cond2 > MAX_VALUE:
            cond1 += 1
            if cond1 > MAX_VALUE:
                cond1 = 1
            cond2 = 1
        rule_dict['INDIFF'] = indiff_str
        rules_list.append(gen_rule(rule_dict))
    return rules_list


def gen_query(exp_conf):
    '''
    Generate a preference query
    '''
    query_id = get_query_id(exp_conf)
    filename = QUERIES_DIR + os.sep + query_id + '.cql'
    rules_list = gen_rules(exp_conf)
    pref = '\nAND\n'.join(rules_list)
    query = QUERY.format(p=pref)
    out_file = open(filename, 'w')
    out_file.write(query)
    out_file.close()


def gen_all_queries(experiment_list):
    '''
    Generate all queries
    '''
    for exp_rec in experiment_list:
        gen_query(exp_rec)


def gen_env_file(exp_conf):
    '''
    Generate environment files for StremPref
    '''
    table_id = get_table_id(exp_conf)
    query_id = get_query_id(exp_conf)
    att_list = ['a' + str(number + 1) + ' INTEGER'
                for number in range(exp_conf[ATT])]
    att_str = ', '.join(att_list)
    text = "REGISTER TABLE r ({att}) \nINPUT '{ddir}/{tab}.csv';"\
        .format(att=att_str, ddir=DATA_DIR, tab=table_id)
    text += '\n\n' + '#' * 80 + '\n\n'
    text += "REGISTER QUERY q \nINPUT '{qdir}/{que}.cql';"\
        .format(qdir=QUERIES_DIR, que=query_id)
    filename = table_id + query_id + '.env'
    out_file = open(ENV_DIR + os.sep + filename, 'w')
    out_file.write(text)
    out_file.close()


def add_experiment(experiment_list, experiment):
    '''
    Add an experimento into experiment list
    '''
    if experiment not in experiment_list:
        experiment_list.append(experiment.copy())


def gen_experiment_list():  # IGNORE:too-many-statements
    '''
    Generate the list of experiments
    '''
    exp_list = []
    # Default parameters
    def_rec = {ATT: ATTRIBUTE_DEFAULT, TUP: TUPLE_DEFAULT,
               DEL: DELETION_DEFAULT, INS: INSERTION_DEFAULT,
               RUL: RULES_DEFAULT, LEV: LEVEL_DEFAULT, IND: INDIFF_DEFAULT}
    # Attributes number variation (no deletions)
    for att_number in ATTRIBUTE_LIST:
        rec = def_rec.copy()
        rec[ATT] = att_number
        add_experiment(exp_list, rec)
        rec[DEL] = 0
        add_experiment(exp_list, rec)
        rec[DEL] = DELETION_DEFAULT
        rec[INS] = 0
        add_experiment(exp_list, rec)

    # Tuples number variation (no deletions)
    for tup_number in TUPLE_LIST:
        rec = def_rec.copy()
        rec[TUP] = tup_number
        add_experiment(exp_list, rec)
        rec[DEL] = 0
        add_experiment(exp_list, rec)
        rec[DEL] = DELETION_DEFAULT
        rec[INS] = 0
        add_experiment(exp_list, rec)

    # Deletions number variation (no insertions)
    for deletions in DELETION_LIST:
        rec = def_rec.copy()
        rec[TUP] = TUPLE_MAX
        rec[DEL] = deletions
        add_experiment(exp_list, rec)
        rec[INS] = 0
        add_experiment(exp_list, rec)

    # Insertions number variation (no deletions)
    for insertions in INSERTION_LIST:
        rec = def_rec.copy()
        rec[INS] = insertions
        add_experiment(exp_list, rec)
        rec[DEL] = 0
        add_experiment(exp_list, rec)

    # Rules number variation
    for rules_number in RULES_LIST:
        rec = def_rec.copy()
        rec[RUL] = rules_number
        add_experiment(exp_list, rec)
        rec[DEL] = 0
        add_experiment(exp_list, rec)
        rec[DEL] = DELETION_DEFAULT
        rec[INS] = 0
        add_experiment(exp_list, rec)

    # Level variation
    for level in LEVEL_LIST:
        rec = def_rec.copy()
        rec[LEV] = level
        add_experiment(exp_list, rec)
        rec[DEL] = 0
        add_experiment(exp_list, rec)
        rec[DEL] = DELETION_DEFAULT
        rec[INS] = 0
        add_experiment(exp_list, rec)

    # indifferent attributes variation
    for indif_number in INDIFF_LIST:
        rec = def_rec.copy()
        rec[IND] = indif_number
        add_experiment(exp_list, rec)
        rec[DEL] = 0
        add_experiment(exp_list, rec)
        rec[DEL] = DELETION_DEFAULT
        rec[INS] = 0
        add_experiment(exp_list, rec)
    return exp_list


def gen_all_env_files(experiment_list):
    '''
    Generate all environment files
    '''
    for exp_rec in experiment_list:
        gen_env_file(exp_rec)


def create_directories():
    '''
    Create directories
    '''
    if not os.path.exists(MAIN_DIR):
        os.mkdir(MAIN_DIR)
    if not os.path.exists(DETAILS_DIR):
        os.mkdir(DETAILS_DIR)
    if not os.path.exists(RUNTIME_SUMMARY_DIR):
        os.mkdir(RUNTIME_SUMMARY_DIR)
    if not os.path.exists(MEMORY_SUMMARY_DIR):
        os.mkdir(MEMORY_SUMMARY_DIR)
    if not os.path.exists(RUNTIME_RESULT_DIR):
        os.mkdir(RUNTIME_RESULT_DIR)
    if not os.path.exists(MEMORY_RESULT_DIR):
        os.mkdir(MEMORY_RESULT_DIR)
    if not os.path.exists(QUERIES_DIR):
        os.mkdir(QUERIES_DIR)
    if not os.path.exists(DATA_DIR):
        os.mkdir(DATA_DIR)
    if not os.path.exists(ENV_DIR):
        os.mkdir(ENV_DIR)


def get_detail_file(algorithm, experiment_id, count):
    '''
    Get filename for experiment details
    '''
    return DETAILS_DIR + os.sep + algorithm + '-' + \
        experiment_id + '.' + str(count) + '.csv'


def run(algorithm, experiment_id, count):
    '''
    Run experiment for range and slide
    '''
    detail_file = get_detail_file(algorithm, experiment_id, count)
    if not os.path.isfile(detail_file):
        command = RUN_COMMAND.format(alg=algorithm, id=experiment_id,
                                     det=detail_file, max=ITERATION_DEFAULT)
        print command
        os.system(command)
        if not os.path.isfile(detail_file):
            print 'Detail results file not found: ' + detail_file
            print "Check if 'streampref' is in path"


def run_experiments(experiment_list):
    '''
    Run all experiments
    '''
    for count in range(RUN_COUNT):
        for alg in ALGORITHM_LIST:
            for exp_rec in experiment_list:
                exp_id = get_experiment_id(exp_rec)
                run(alg, exp_id, count + 1)


def get_summaries(detail_file):
    '''
    Import a result file to database
    '''
    if not os.path.isfile(detail_file):
        print 'File does not exists: ' + detail_file
        return (float('NaN'), float('NaN'))
    in_file = open(detail_file, 'r')
    reader = csv.DictReader(in_file, skipinitialspace=True)
    sum_time = 0.0
    sum_memory = 0.0
    count = 0
    for rec in reader:
        sum_time += float(rec[RUNTIME])
        sum_memory += float(rec[MEMORY])
        count += 1
    in_file.close()
    return (sum_time, sum_memory / count)


def get_average(detail_file, only_first):
    '''
    Get average for first iteration or other iterations
    '''
    if not os.path.isfile(detail_file):
        print 'File does not exists: ' + detail_file
        return (float('NaN'), float('NaN'))
    in_file = open(detail_file, 'r')
    reader = csv.DictReader(in_file, skipinitialspace=True)
    sum_time = 0.0
    sum_memory = 0.0
    first_rec = reader.next()
    if only_first:
        sum_time = float(first_rec[RUNTIME])
        sum_memory = float(first_rec[MEMORY])
        return (sum_time, sum_memory)
    count = 0
    for rec in reader:
        sum_time += float(rec[RUNTIME])
        sum_memory += float(rec[MEMORY])
        count += 1
    in_file.close()
    return (sum_time / count, sum_memory / count)


def get_basename(key, experiment):
    '''
    Get a base name for key and experiment
    '''
    basename = key
    if key != DEL and experiment[DEL] == 0:
        basename += '_no_del'
    if key != INS and experiment[INS] == 0:
        basename += '_no_ins'
    return basename


def summarize_details(key, value_list, default_experiment):
    '''
    Summarize experiments details
    '''
    time_list = []
    mem_list = []
    exp_rec = default_experiment.copy()
    for value in value_list:
        exp_rec[key] = value
        for rcount in range(RUN_COUNT):
            time_rec = {key: value}
            mem_rec = {key: value}
            for alg in ALGORITHM_LIST:
                dfile = get_detail_file(alg, get_experiment_id(exp_rec),
                                        rcount + 1)
                runtime, memory = get_summaries(dfile)
                time_rec[alg] = runtime
                mem_rec[alg] = memory
            time_list.append(time_rec)
            mem_list.append(mem_rec)
    fname = RUNTIME_SUMMARY_DIR + os.sep + get_basename(key, exp_rec) + '.csv'
    write_file(fname, key, time_list)
    fname = MEMORY_SUMMARY_DIR + os.sep + get_basename(key, exp_rec) + '.csv'
    write_file(fname, key, mem_list)


def summarize_iterations():
    '''
    Summarize experiments details
    '''
    exp_rec = {ATT: ATTRIBUTE_DEFAULT, TUP: TUPLE_DEFAULT,
               DEL: DELETION_DEFAULT, INS: INSERTION_DEFAULT,
               RUL: RULES_DEFAULT, LEV: LEVEL_DEFAULT, IND: INDIFF_DEFAULT}
    time_list = []
    mem_list = []
    for rcount in range(RUN_COUNT):
        for alg in ALGORITHM_LIST:
            time_rec = {ALGORITHM: alg}
            mem_rec = {ALGORITHM: alg}
            dfile = get_detail_file(alg, get_experiment_id(exp_rec),
                                    rcount + 1)
            runtime, memory = get_average(dfile, only_first=True)
            time_rec[FIRST] = runtime
            mem_rec[FIRST] = memory
            runtime, memory = get_average(dfile, only_first=False)
            time_rec[OTHERS] = runtime
            mem_rec[OTHERS] = memory
            time_list.append(time_rec)
            mem_list.append(mem_rec)
    fname = RUNTIME_SUMMARY_DIR + os.sep + 'iterations.csv'
    write_file(fname, ALGORITHM, time_list)
    fname = MEMORY_SUMMARY_DIR + os.sep + 'iterations.csv'
    write_file(fname, ALGORITHM, mem_list)


def summarize_all():
    '''
    Summarize all results
    '''
    exp = {}
    exp[ATT] = ATTRIBUTE_LIST
    exp[TUP] = TUPLE_LIST
    exp[INS] = INSERTION_LIST
    exp[RUL] = RULES_LIST
    exp[LEV] = LEVEL_LIST
    exp[IND] = INDIFF_LIST
    def_rec = {ATT: ATTRIBUTE_DEFAULT, TUP: TUPLE_DEFAULT,
               DEL: DELETION_DEFAULT, INS: INSERTION_DEFAULT,
               RUL: RULES_DEFAULT, LEV: LEVEL_DEFAULT, IND: INDIFF_DEFAULT}
    # Insertions and deletions
    for key in exp:
        summarize_details(key, exp[key], def_rec)
    # No deletions
    def_rec = {ATT: ATTRIBUTE_DEFAULT, TUP: TUPLE_DEFAULT,
               DEL: 0, INS: INSERTION_DEFAULT,
               RUL: RULES_DEFAULT, LEV: LEVEL_DEFAULT, IND: INDIFF_DEFAULT}
    for key in exp:
        summarize_details(key, exp[key], def_rec)
    # No insertions
    def_rec = {ATT: ATTRIBUTE_DEFAULT, TUP: TUPLE_DEFAULT,
               DEL: DELETION_DEFAULT, INS: 0,
               RUL: RULES_DEFAULT, LEV: LEVEL_DEFAULT, IND: INDIFF_DEFAULT}
    for key in exp:
        if key != INS:
            summarize_details(key, exp[key], def_rec)
    # Deletions (with maximum number of tuples)
    def_rec = {ATT: ATTRIBUTE_DEFAULT, TUP: TUPLE_MAX,
               DEL: DELETION_DEFAULT, INS: INSERTION_DEFAULT,
               RUL: RULES_DEFAULT, LEV: LEVEL_DEFAULT, IND: INDIFF_DEFAULT}
    summarize_details(DEL, DELETION_LIST, def_rec)
    def_rec[INS] = 0
    summarize_details(DEL, DELETION_LIST, def_rec)
    summarize_iterations()


def confidence_interval(key, in_file, out_file):
    '''
    Calculate final result with confidence interval
    '''
    if not os.path.isfile(in_file):
        print 'File does not exists: ' + in_file
        return
    command = CONFINTERVAL_COMMAND.format(inf=in_file, outf=out_file, keyf=key)
    print command
    os.system(command)
    if not os.path.isfile(out_file):
        print 'Output file not found: ' + out_file
        print "Check if 'confinterval.py' is in path"


def confidence_interval_all():
    '''
    Calculate confidence interval for all results
    '''
    # Deletions and insertions
    key_list = [ATT, TUP, DEL, INS, RUL, LEV, IND]
    for key in key_list:
        in_file = RUNTIME_SUMMARY_DIR + os.sep + key + '.csv'
        out_file = RUNTIME_RESULT_DIR + os.sep + key + '.csv'
        confidence_interval(key, in_file, out_file)
        in_file = MEMORY_SUMMARY_DIR + os.sep + key + '.csv'
        out_file = MEMORY_RESULT_DIR + os.sep + key + '.csv'
        confidence_interval(key, in_file, out_file)
    # No deletions
    key_list = [ATT, TUP, INS, RUL, LEV, IND]
    for key in key_list:
        in_file = RUNTIME_SUMMARY_DIR + os.sep + key + '_no_del.csv'
        out_file = RUNTIME_RESULT_DIR + os.sep + key + '_no_del.csv'
        confidence_interval(key, in_file, out_file)
        in_file = MEMORY_SUMMARY_DIR + os.sep + key + '_no_del.csv'
        out_file = MEMORY_RESULT_DIR + os.sep + key + '_no_del.csv'
        confidence_interval(key, in_file, out_file)
    # No insertions
    key_list = [ATT, TUP, DEL, RUL, LEV, IND]
    for key in key_list:
        in_file = RUNTIME_SUMMARY_DIR + os.sep + key + '_no_ins.csv'
        out_file = RUNTIME_RESULT_DIR + os.sep + key + '_no_ins.csv'
        confidence_interval(key, in_file, out_file)
        in_file = MEMORY_SUMMARY_DIR + os.sep + key + '_no_ins.csv'
        out_file = MEMORY_RESULT_DIR + os.sep + key + '_no_ins.csv'
        confidence_interval(key, in_file, out_file)
    # Iterations
    in_file = RUNTIME_SUMMARY_DIR + os.sep + 'iterations.csv'
    out_file = RUNTIME_RESULT_DIR + os.sep + 'iterations.csv'
    confidence_interval(ALGORITHM, in_file, out_file)
    in_file = MEMORY_SUMMARY_DIR + os.sep + 'iterations.csv'
    out_file = MEMORY_RESULT_DIR + os.sep + 'iterations.csv'
    confidence_interval(ALGORITHM, in_file, out_file)


def write_file(fname, id_field, record_list):
    '''
    Write record_list to file
    '''
    # Check if list of records is not empty
    if len(record_list):
        # Build field list without identifier field
        field_list = [field for field in record_list[0].keys()
                      if field != id_field]
        # Sort field list
        field_list.sort()
        # Insert identifier field in the beginning of the list
        field_list.insert(0, id_field)
        output_file = open(fname, 'w')
        writer = csv.DictWriter(output_file, field_list,
                                delimiter=',')
        header = {field: field for field in field_list}
        writer.writerow(header)
        for rec in record_list:
            writer.writerow(rec)
        output_file.close()


def get_arguments(print_help=False):
    '''
    Get arguments
    '''
    import argparse
    parser = argparse.ArgumentParser('IncSimpleGen')
    parser.add_argument('-g', '--gen', action="store_true",
                        default=False,
                        help='Generate files')
    parser.add_argument('-r', '--run', action="store_true",
                        default=False,
                        help='Run experiments')
    parser.add_argument('-s', '--summarize', action="store_true",
                        default=False,
                        help='Summarize results')
    parser.add_argument('-c', '--confinterval', action="store_true",
                        default=False,
                        help='Calculate confidence interval over results')

    args = parser.parse_args()
    if print_help:
        parser.print_help()
    return args


def main():
    '''
    Main routine
    '''
    create_directories()
    exp_list = gen_experiment_list()
    args = get_arguments()
    if args.gen:
        print 'Generating table data'
        gen_all_tables(exp_list)
        print 'Generating queries'
        gen_all_queries(exp_list)
        print 'Generating environments'
        gen_all_env_files(exp_list)
    elif args.run:
        print 'Running experiments'
        run_experiments(exp_list)
    elif args.summarize:
        print 'Summarizing results'
        summarize_all()
    elif args.confinterval:
        confidence_interval_all()
    else:
        get_arguments(True)


if __name__ == '__main__':
    main()
