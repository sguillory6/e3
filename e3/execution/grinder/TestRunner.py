import importlib
import os
import shutil
import sys

from java.lang import System
from net.grinder.script.Grinder import grinder
from org.slf4j import LoggerFactory

import TestScript
import utils

# Ensure we don't write to the agent or worker logs
script_logger = LoggerFactory.getLogger("atlassian")

# The workload run by this TestRunner is defined in a JSON file containing an array of jobs, in format like this:
#   [
#        {
#            "script": "BrowseProjectsAndRepositories",
#            "description": "Browse",
#            "scale": 0.1,
#            "weight": 0.3,
#            ...
#        },
#        ...
#   ]
# The "script" defines a class name to run.
# The "weight" defines what proportion of clients are running the job.
# The "scale" is not used during test execution, but is used in later analysis stages to more fairly scale each
#    component of the overall throughput number.
root = System.getProperty("root")
if not root:
    raise ValueError("Required system property 'root' is not provided. Set using: -Droot=<e3 root>")

work_dir = '%s/work/' % root

wkld = System.getProperty("workload")
if not wkld:
    raise ValueError("Required system property 'workload' is not provided. Set using: -Dworkload=<workload name>")

workload_json_file = "%s/e3/data/workloads/%s.json" % (root, wkld)
if not os.path.exists(workload_json_file):
    workload_json_file = "%s/workloads/%s.json" % (root, wkld)
    if not os.path.exists(workload_json_file):
        raise ValueError("System property 'workload' must be the name of a valid "
                         "workload located in %s/e3/data/workloads or %s/workloads" % (root, root))

workload = utils.load_json(workload_json_file)
if not workload or len(workload) == 0:
    raise ValueError("The workload JSON file '%s' could not be loaded or is invalid" % workload_json_file)

# Import site packages for jython
sys.path.append('%s/site-packages/' % root)

TestScript.global_test_count = len(workload)

# Import the parent module
for job in workload:
    importlib.import_module(job["script"])
    importlib.import_module(job["testDataProvider"])

# Clean out the working directory
if os.path.exists(work_dir):
    script_logger.warn("Deleting directory %s" % work_dir)
    shutil.rmtree(work_dir)


def choose_job():
    process_count_per_agent = grinder.getProperties().getDouble("grinder.processes", 1.0)
    thread_count_per_process = grinder.getProperties().getDouble("grinder.threads", 1.0)
    agent_count = float(System.getProperty("agentCount"))

    process_number_on_agent = float(grinder.getProcessNumber() - grinder.getFirstProcessNumber())
    thread_number_in_process = float(grinder.getThreadNumber())
    agent_number = float(grinder.getAgentNumber())

    client_number = agent_number + agent_count * (
        process_number_on_agent + thread_number_in_process * process_count_per_agent
    )
    total_clients = agent_count * process_count_per_agent * thread_count_per_process
    # The + 0.5 is to round to nearest if the calculation would otherwise lie near a boundary.
    weight = (client_number + 0.5) / total_clients
    chosen_job = 0
    for i in range(len(workload)):
        chosen_job = i
        weight -= workload[i]["weight"]
        if weight < 0:
            break
    return chosen_job


def create_test_runner(job_number, job_data):
    script_logger.info("Creating test runner %s, %s" % (job_data['script'], job_data))
    script = job_data["script"]
    script_exec = utils.load_script(script)
    return script_exec(job_number, job_data)


class TestRunner(object):
    def __init__(self):
        job_number = choose_job()
        job_data = workload[job_number]
        self.testRunner = create_test_runner(job_number, job_data)

    def __call__(self):
        try:
            self.testRunner()
        except Exception as ex:
            # Ensure that if an exception is raised and NOT handled in the TestScript, we mark the test as failed
            grinder.getStatistics().getForLastTest().success = False
            grinder.getLogger().error("Script '%s' failed due to exception: %s", type(self.testRunner), ex)
            # Re-raise the exception to grinder
            raise
