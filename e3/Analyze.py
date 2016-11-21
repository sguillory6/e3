#!/usr/bin/env python
import logging.config

import click
from analysis.rrdtool.Analyze import graph_experiment
from analysis.rrdtool.Report import experiment_report

from common.E3 import e3


def run_gnuplot_analysis(run_name):
    logging.debug("Analysing run '%s' using Gnuplot based analysis", run_name)
    # Do not remove import below, it begins the execution of the analysis
    import analysis.gnuplot.Analyze


def run_rrd_analysis(run_name):
    graph_experiment(run_name)
    experiment_report(run_name)


@click.command()
@click.option('-r', '--run', required=True, help='The experiment run you want to execute',
              type=click.Choice(e3.get_runs()), default=e3.get_single_run())
def command(run):
    logging.config.fileConfig(e3.get_logging_conf())
    run_rrd_analysis(run)
    run_gnuplot_analysis(run)

if __name__ == "__main__":
    command()
