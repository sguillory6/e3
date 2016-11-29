#!/usr/bin/env python
import glob
import logging
import os
import re
from datetime import datetime

import click

if __name__ == '__main__':
    import sys
    sys.path.append(os.path.realpath(os.path.join(__file__, '..', '..', '..')))

from analysis.rrdtool.types.BitbucketJMX import BitbucketJmx
from analysis.rrdtool.types.Cpu import Cpu
from analysis.rrdtool.types.Disk import Disk
from analysis.rrdtool.types.GenericJmx import GenericJmx
from analysis.rrdtool.types.HazelcastEventServiceJmx import HazelcastEventServiceJmx
from analysis.rrdtool.types.HazelcastOperationServiceJmx import HazelcastOperationServiceJmx
from analysis.rrdtool.types.HibernateJmx import HibernateJmx
from analysis.rrdtool.types.HikariJmx import HikariJmx
from analysis.rrdtool.types.Interface import Interface
from analysis.rrdtool.types.Load import Load
from analysis.rrdtool.types.Memory import Memory
from analysis.rrdtool.types.Processes import Processes
from analysis.rrdtool.types.Swap import Swap
from analysis.rrdtool.types.ThreadpoolJmx import ThreadpoolJmx
from analysis.rrdtool.types.TomcatJmx import TomcatJmx

from common.E3 import e3


def get_stage_timing(run):
    stage_start = {}
    stage_elapsed = {}
    run_root = e3.get_run_dir(run)
    threads = glob.glob1(run_root, 'thread-*')
    for thread in threads:
        thread_root = os.path.join(run_root, thread)
        workers = glob.glob1(thread_root, 'worker-node-*')
        for worker in workers:
            worker_root = os.path.join(thread_root, worker)
            stages = glob.glob1(worker_root, 'stage-*')
            for stage in stages:
                stage_root = os.path.join(worker_root, stage)
                logs = glob.glob1(stage_root, '*-0.log')
                for log in logs:
                    log_file = os.path.join(stage_root, log)
                    stage_timing_key = "%s,%s" % (thread, stage)
                    with open(log_file) as infile:
                        for line in infile:
                            m = re.match(r".*start time is ([0-9]*) ms since Epoch", line)
                            if m:
                                stage_start[stage_timing_key] = int(m.group(1))
                            m = re.match(r".*elapsed time is ([0-9]*) ms", line)
                            if m:
                                stage_elapsed[stage_timing_key] = int(m.group(1))
    return stage_start, stage_elapsed


def graph_experiment(run):
    stage_timing = get_stage_timing(run)
    run_json = e3.load_run(run)
    analysis_root = e3.get_analysis_dir(run)

    pre_post_buffer_time = 90

    threads = run_json['threads']
    for thread_index in range(0, len(threads)):
        thread_logical_name = 'thread-%03d' % (thread_index + 1)
        stages = threads[thread_index]['stages']

        cluster_nodes = threads[thread_index]['instance']['stack']['ClusterNodes']
        worker_nodes = threads[thread_index]['worker']['stack']['ClusterNodes']

        for stage_index in range(0, len(stages)):
            stage_logical_name = 'stage-%03d' % stage_index
            stage_timing_key = '%s,%s' % (thread_logical_name, stage_logical_name)

            if stage_timing_key in stage_timing[0]:
                stage_start_long = stage_timing[0][stage_timing_key] / 1000.0
                stage_start = datetime.fromtimestamp(stage_start_long - pre_post_buffer_time).strftime('%Y%m%d %H:%M')
                stage_end = 'now'
                if stage_timing_key in stage_timing[1].keys():
                    stage_end_long = stage_start_long + (stage_timing[1][stage_timing_key] / 1000.0)
                    stage_end = datetime.fromtimestamp(stage_end_long + pre_post_buffer_time).strftime('%Y%m%d %H:%M')

                for cluster_node_index in range(0, len(cluster_nodes)):
                    cn_name = 'cluster-node-%03d' % (cluster_node_index + 1)
                    graph_node(analysis_root, cn_name, run, stage_end, stage_logical_name, stage_start,
                               thread_logical_name)

                for worker_node_index in range(0, len(worker_nodes)):
                    wrk_name = 'worker-node-%03d' % (worker_node_index + 1)
                    graph_node(analysis_root, wrk_name, run, stage_end, stage_logical_name, stage_start,
                               thread_logical_name)

                graph_node(analysis_root, 'file-server-001', run, stage_end, stage_logical_name, stage_start,
                           thread_logical_name)


def graph_node(analysis_root, node, run, stage_end, stage_logical_name, stage_start, thread):
    logging.info("Graphing node '%s' for stage '%s' of thread '%s' of run '%s'" %
                 (node, stage_logical_name, thread, run))
    graph_directory = os.path.join(analysis_root, thread, stage_logical_name, node)
    if not os.path.exists(graph_directory):
        os.makedirs(graph_directory)
    rrd_data_directory = os.path.join(e3.get_run_dir(run), thread, node, 'collectd-rrd', 'localhost')
    if os.path.exists(rrd_data_directory):
        node_name = "%s-%s-%s" % (thread, stage_logical_name, node)

        # Draw Load graph
        load_grapher = Load(graph_directory, rrd_data_directory)
        load_grapher.render(node_name, stage_start, stage_end)

        # Draw CPU graph
        cpu_grapher = Cpu(graph_directory, rrd_data_directory)
        cpu_grapher.render(node_name, stage_start, stage_end)

        # Draw Memory graphs
        mem_grapher = Memory(graph_directory, rrd_data_directory)
        mem_grapher.render(node_name, stage_start, stage_end)

        # # Draw eth0 network graph
        network_grapher = Interface(graph_directory, rrd_data_directory)
        network_grapher.render(node_name, stage_start, stage_end)

        # Draw disk graph
        disk_grapher = Disk(graph_directory, rrd_data_directory)
        disk_grapher.render(node_name, stage_start, stage_end)

        # Swap usage
        swap_grapher = Swap(graph_directory, rrd_data_directory)
        swap_grapher.render(node_name, stage_start, stage_end)

        # Processes
        processes_grapher = Processes(graph_directory, rrd_data_directory)
        processes_grapher.render(node_name, stage_start, stage_end)

        #
        # JMX graphs
        #

        # Generic JMX graphs
        generic_jmx_grapher = GenericJmx(graph_directory, rrd_data_directory)
        generic_jmx_grapher.render(node_name, stage_start, stage_end)

        # Tomcat JMX graphs
        tomcat_jmx_grapher = TomcatJmx(graph_directory, rrd_data_directory)
        tomcat_jmx_grapher.render(node_name, stage_start, stage_end)

        # Bitbucket JMX graphs
        bitbucket_jmx_grapher = BitbucketJmx(graph_directory, rrd_data_directory)
        bitbucket_jmx_grapher.render(node_name, stage_start, stage_end)

        # Threadpool JMX graphs
        threadpool_jmx_grapher = ThreadpoolJmx(graph_directory, rrd_data_directory)
        threadpool_jmx_grapher.render(node_name, stage_start, stage_end)

        # Hazelcast JMX graphs
        hazelcast_jmx_operations_grapher = HazelcastOperationServiceJmx(graph_directory, rrd_data_directory)
        hazelcast_jmx_operations_grapher.render(node_name, stage_start, stage_end)
        hazelcast_jmx_events_grapher = HazelcastEventServiceJmx(graph_directory, rrd_data_directory)
        hazelcast_jmx_events_grapher.render(node_name, stage_start, stage_end)

        # Hikari JMX graphs
        hikari_jmx_grapher = HikariJmx(graph_directory, rrd_data_directory)
        hikari_jmx_grapher.render(node_name, stage_start, stage_end)

        # Hibernate JMX graphs
        hibernate_jmx_grapher = HibernateJmx(graph_directory, rrd_data_directory)
        hibernate_jmx_grapher.render(node_name, stage_start, stage_end)


@click.command()
@click.option('-r', '--run', required=True, help='The run to graph',
              type=click.Choice(e3.get_runs()))
def graph_experiment_command(run):
    graph_experiment(run)

if __name__ == '__main__':
    graph_experiment_command()
