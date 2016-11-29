#!/usr/bin/env python
import os

import click
import glob

if __name__ == "__main__":
    import sys
    sys.path.append(os.path.realpath(os.path.join(__file__, "..", "..", "..")))

from common.E3 import e3
from common.TemplateEngine import TemplateEngine
from common.Utils import open_with_external_tool


def get_image_layout(analysis_root):
    node_set = set()
    img_dict = {}
    threads = glob.glob1(analysis_root, "thread-*")
    for thread in threads:
        img_dict[thread] = {}
        thread_dir = os.path.join(analysis_root, thread)
        stages = glob.glob1(thread_dir, "stage-*")
        for stage in stages:
            img_dict[thread][stage] = {}
            stage_dir = os.path.join(os.path.join(thread_dir, stage))
            nodes = os.listdir(stage_dir)
            for node in nodes:
                node_set.add(node)
                node_dir = os.path.join(stage_dir, node)
                for img in glob.glob1(node_dir, "*.png"):
                    prefix = "%s-%s-%s" % (thread, stage, node)
                    key = img[len(prefix) + 1:-4]
                    if key not in img_dict[thread][stage].keys():
                        img_dict[thread][stage][key] = []
                    img_dict[thread][stage][key].append(node)
    return node_set, img_dict


def experiment_report(run):
    analysis_root = e3.get_analysis_dir(run)

    top = [
        'load',
        'cpu-all-average',
        'bitbucket-hosting-tickets',
        'hazelcast-operations',
        'hazelcast-events',
        'processes-count-git',
        'processes-resident-git',
        'memory',
        'java-memory-heap',
        'jvm-file-handles',
        'interface-eth0',
        'bitbucket-command-tickets',
        'processes-cputime-git',
        'processes-disk-io-git',
        'bitbucket-scm-stats',
        'disk-xvda',
        'disk-xvdb',
        'disk-xvdf'
    ]

    nodes, images = get_image_layout(analysis_root)
    nodes = sorted(nodes)

    reports = []
    for thread in images.keys():
        for stage in images[thread].keys():
            bottom = set(images[thread][stage].keys()) - set(top)
            template_engine = TemplateEngine(os.path.dirname(__file__), {
                'thread': thread,
                'stage': stage,
                'top': top,
                'bottom': bottom,
                'nodes': nodes,
                'data': images[thread][stage],
            })

            report_file = os.path.join(analysis_root, "%s-%s-report.html" % (thread, stage))
            with open(report_file, "w+") as report:
                report.write(template_engine.include("Report.html"))
                reports.append(report_file)

    # Open the resulting images using the system "open" or "see" command
    open_with_external_tool(reports)


@click.command()
@click.option('-r', '--run', required=True, help='The run to graph',
              type=click.Choice(e3.get_runs()))
def experiment_report_command(run):
    experiment_report(run)

if __name__ == '__main__':
    experiment_report_command()
