IncSimpleGen
===

**Table of Contents**

- [Introduction](#introduction)
- [Command Line Usage](#command-line-usage)
- [Experiment Parameters](#experiment-parameters)
- [File Structure](#file-structure)

# Introduction
IncSimpleGen is a synthetic data generator for evaluation of algorithms of preference operators of StreamPref DSMS

# Command Line Usage

The command line parameters of IncSimpleGen are:
- -h/--help: Show help message
- -g/--gen: Generate files
- -r/--run: Run exempriments
- -s/--summarize: Summarize experiment results
- -c/-confinterval: Calculate final result with confidence intervals

# Experiment Parameters

The IncSimpleGen generates the datasets and preference queries with parameter variation.

The parameters related to dataset are:
- Number of attributes
  - Variation: 8, 16, 32, 64
  - Default: 8
- Initial number of  tuples (number of tuples at first iteration):
  - Variation: 500, 1000, 2000, 4000, 8000
  - Default: 1000
- Number of deletions (per iteration)
  - Variation: 50, 100, 200, 400
  - Default: 50
- Number of insertions (per iteration)
  - Variation: 50, 100, 200, 400
  - Default: 50

The parameters related to preference queries are:
- Number of preference rules
  - Variation: 2, 4, 8, 16, 32
  - Default: 8
- Maximum preference level
  - Variation: 1, 2, 4, 8
  - Default: 2
- Number of indifferent attributes
  - Variation: 0, 1, 2, 4
  - Default: 4

# File Structure

The IncSimpleGen creates the following file structure:
- pref
  - data (datasets)
  - details (detailed results genereted by experiments)
  - env (environment files used in the experiments)
  - memory_result (final results with confidence interval of memory usage)
  - memory_summary (summarized results of memory usage)
  - runtime_result (final results with confidence interval of runtime)
  - runtime_summary (summarized results of runtime)

