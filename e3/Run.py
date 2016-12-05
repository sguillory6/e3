#!/usr/bin/env python

import json
import logging
import logging.config
import os
import re
import sys
import time
from threading import Thread

import click
import requests
import spur
from progressbar import ProgressBar, Percentage, Bar
from spur.results import ExecutionResult

from common import Utils
from common.Config import run_config
from common.E3 import e3
from common.Utils import LogWrapper


class Run:
    """
    This class runs an run as defined in an run file.
    """

    def __init__(self, run_name):
        self._log = logging.getLogger('run')
        logging.getLogger("paramiko").setLevel(logging.WARNING)
        self._run_config = e3.load_run(run_name)
        self._run_name = run_name
        self.number_stages()
        self.denormalize_config()

    def denormalize_config(self):
        """
        This method goes through the run configuration and de-normalises all the stage configuration into
        independent stages. This means that each stage should have all the information it needs to run without having to
        rely on any information from the parent config. If a stage does not a required attribute then that property is
        copied from the top level run configuration.
        :return: an run configuration dict comprising fully denormalized stages
        """
        self.denormalize_attribute("duration")
        self.denormalize_attribute("workload")

    def denormalize_attribute(self, attribute_name):
        """
        Denormalizes the supplied attribute in the run configuration
        :param attribute_name: the name of the attribute to denormalize
        :return: a set of attribute values
        """
        threads = self._run_config["threads"]
        attributes = set()
        if attribute_name in self._run_config:
            attribute = self._run_config[attribute_name]
            attributes.add(attribute)
            self._log.debug("Found a top level attribute %s (%s) in configuration, applying to all %s-less stages",
                            attribute_name, attribute, attribute_name)
            for thread in threads:
                for stage in thread["stages"]:
                    if attribute_name not in stage:
                        stage[attribute_name] = attribute
                    attributes.add(stage[attribute_name])
        else:
            self._log.debug("No top level [%s] attribute found, checking that each stage contains one", attribute_name)
            for thread in threads:
                for stage in thread["stages"]:
                    if attribute_name not in stage:
                        raise Exception("Stage [%s] does not have attribute [%s] and no top level instance defined" %
                                        (stage, attribute_name))
        return attributes

    def run(self):
        """
        Iterate through the run map and start a thread of run execution for each key
        :return:
        """
        run_threads = []
        thread_index = 1
        for thread in self._run_config["threads"]:
            run_thread = RunThread(thread, self._run_name, thread_index)
            thread_index += 1
            run_threads.append(run_thread)
            run_thread.start()
        for run_thread in run_threads:
            run_thread.join()

        self._log.info("Finished running %s" % self._run_name)
        return self._run_name

    def number_stages(self):
        for thread in self._run_config["threads"]:
            stage_key = 0
            for stage in thread["stages"]:
                stage['key'] = '%03d' % stage_key
                stage_key += 1


class RunThread(Thread):
    """
    This class is responsible for setting up and executing a run thread.
    The following activities make up the execution of a stage.
     1. Worker nodes are sanitized. This means that all git processes are killed. Certain java processes are also
     terminated
     2. The data, execution/grinder, and execution/lib directories are distributed to all worker nodes
     3. The grinder console is started on one of the worker nodes. Typically the worker node that was provisioned first
     4. The grinder agents are started on all worker nodes
     5. Stage is started
     6. Wait until run duration has elapsed
     7. Repeat with the next stage on the queue
    """

    def __init__(self, thread, run_name, thread_index):
        self._log = logging.getLogger("run")
        self._run_name = run_name
        self._thread = thread
        # list of workers that have already had the e3 distribution synced to them
        self._synced_workers = set()
        Thread.__init__(self, name='RunThread:%d' % thread_index)
        self._run_config = None

    def run(self):
        for stage in self._thread["stages"]:
            self.run_stage(self._thread, stage)

    def run_stage(self, thread, stage):
        worker_stage = WorkerStage(thread, stage)

        self._log.info("Running Stage - worker: %s, workload: %s, instance %s, clients: %d, worker-nodes: %d, "
                       "clients-per-worker: %d, duration %s ms",
                       worker_stage.worker['stack']['Name'],
                       worker_stage.workload,
                       worker_stage.instance['stack']['Name'],
                       worker_stage.clients,
                       len(worker_stage.worker_nodes),
                       worker_stage.clients_per_worker,
                       worker_stage.duration)

        # TODO refactor run_config into class E3
        self._run_config = run_config(worker_stage.worker['stack']['Name'])

        self.sanitize_workers(worker_stage)
        self.restart_bitbucket(worker_stage)
        self.distribute_grinder(worker_stage)
        self.start_console(worker_stage)
        self.start_agents(worker_stage)
        self.start_stage(worker_stage)
        self.wait_finish(worker_stage)

    def sanitize_workers(self, worker_stage):
        self._log.info("Sanitizing workers")

        for worker in worker_stage.worker_nodes:
            self._log.debug("Sanitizing worker [%s] " % worker.hostname)
            while True:
                try:
                    # Kill all orphaned git processes
                    if self._remotely_kill_process(worker, "TERM", process="git"):
                        # If we could kill processes we wait to see that they exited cleanly
                        time.sleep(10)
                        if self._remotely_kill_process(worker, "0", process="git"):
                            # If they did not, we get forceful
                            self._remotely_kill_process(worker, "KILL", process="git")

                    # Attempt to kill the worker and agent
                    find_grinder_processes = [
                        "sh",
                        "-c",
                        "/usr/sbin/lsof -n -i TCP:6372 -i TCP:6373 -i TCP:3333 | "
                        "grep java |  awk '{print $2}' | sort -u"
                    ]
                    grinder_processes_result = self.run_command(worker, find_grinder_processes)
                    if grinder_processes_result.return_code == 0:
                        grinder_pids_arr = grinder_processes_result.output.split("\n")
                        grinder_pids = []
                        for grinder_pid in grinder_pids_arr:
                            if grinder_pid.isdigit():
                                grinder_pids.append(int(grinder_pid))

                        grinders_killed = 0
                        for pid in grinder_pids:
                            if self._remotely_kill_process(worker, "TERM", pid=int(pid)):
                                grinders_killed += 1

                        if grinders_killed > 0:
                            time.sleep(10)
                            for pid in grinder_pids:
                                if self._remotely_kill_process(worker, "0", pid=int(pid)):
                                    self._remotely_kill_process(worker, "KILL", pid=int(pid))
                except:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    self._log.info("Could not sanitize worker node %s (%s: %s), retrying" %
                                   (worker.user_host, exc_type, exc_value))
                    time.sleep(5)
                else:
                    break

            stage_dir = "%s/%s/stage-%s" % (self._run_config['worker_run_dir'], self._run_name, worker_stage.key)
            self.clean_folder(stage_dir, worker)
            tmp_dir = "%s/tmp" % self._run_config['data_dir']
            self.clean_folder(tmp_dir, worker)

    def dir_exists(self, server, remote_file_name):
        return self.run_command(server, [
            'sudo', 'sh', '-c', 'test -d "%s"' % remote_file_name
        ], is_sudo=True).return_code == 0

    def clean_folder(self, folder_to_clean, worker):
        self._log.debug("Cleaning folder %s " % folder_to_clean)
        if not self.dir_exists(worker, folder_to_clean):
            return

        to_be_deleted = self.do_run_command(worker, [
            'sudo', 'sh', '-c', 'find %s -maxdepth 1 -type d' % folder_to_clean
        ], is_sudo=True).output

        if len(to_be_deleted) > 0:
            to_be_deleted = filter(lambda name: len(name) > 1 and name != folder_to_clean, to_be_deleted.split('\r\n'))
            total = len(to_be_deleted)
            if total > 0:
                if len(folder_to_clean) > 20:
                    folder_name = re.sub(r'^(.{7}).*(.{10})$', '\g<1>...\g<2>', folder_to_clean)
                else:
                    folder_name = folder_to_clean.ljust(20)
                bar = ProgressBar(widgets=[
                    'Cleaning: %s' % folder_name, ' ', Percentage(), ' ', Bar()
                ], maxval=total).start()
                count = 1
                for delete_me in to_be_deleted:
                    bar.update(count)
                    self.run_command(worker, ['sudo', 'rm', '-rf', delete_me], is_sudo=True)
                    count += 1
                bar.finish()

    def distribute_grinder(self, worker_stage):
        self._log.info("Distributing grinder to workers")
        for worker_node in worker_stage.worker_nodes:
            if worker_node.user_host in self._synced_workers:
                self._log.debug("Skipping grinder rsync. %s already has grinder" % worker_node.user_host)
                return
            self._log.debug("Distributing grinder to instance: %s, user_host: %s",
                            worker_node.instance, worker_node.user_host)

            remote_run_dir = '%s/stage-%s' % (self._run_config['worker_run_dir'], worker_stage.key)
            remote_grinder_lib_dir = '%s/execution/lib/grinder-3.11/lib' % self._run_config['worker_e3_dir']
            instances_dir = '%s/data/instances' % self._run_config['worker_e3_dir']
            remote_tmp_dir = '%s/tmp' % self._run_config['data_dir']
            remote_site_packages = '%s/site-packages' % self._run_config['data_dir']

            self.run_command(worker_node, [
                'mkdir', '-p', remote_run_dir, remote_grinder_lib_dir,
                remote_tmp_dir, instances_dir, remote_site_packages
            ])
            key_file = '%s/%s/%s.pem' % (e3.get_e3_home(), "instances", worker_node.instance)

            remote_data_dir = os.path.join(self._run_config['worker_e3_dir'], 'data')
            for directory in ['keys', 'snapshots', 'workloads']:
                local_data_dir = os.path.join(e3.get_e3_home(), directory)
                Utils.rsync(worker_node.user_host, key_file, remote_data_dir, local_data_dir)

            remote_execution_dir = os.path.join(self._run_config['worker_e3_dir'], 'execution')
            local_execution_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'execution'))
            for directory in ['grinder', 'lib']:
                local_execution_subdir = os.path.join(local_execution_dir, directory)
                Utils.rsync(worker_node.user_host, key_file, remote_execution_dir, local_execution_subdir)

            local_site_packages = os.path.abspath(os.path.join(e3.get_e3_home(), "site-packages"))
            Utils.rsync(worker_node.user_host, key_file, remote_site_packages, local_site_packages)

            instance_files = set()
            instance_files.add(worker_stage.instance['stack']['Name'])
            instance_files.add(worker_stage.instance['stack']['RunConfig']['network'])

            remote_instance_dir = os.path.join(self._run_config['worker_e3_dir'], 'data', 'instances')
            local_instance_dir = os.path.join(e3.get_e3_home(), 'instances')
            for inst in instance_files:
                remote_instance_file = os.path.join(remote_instance_dir, inst + '.json')
                local_instance_file = os.path.join(local_instance_dir, inst + '.json')
                Utils.rsync(worker_node.user_host, key_file, remote_instance_file, local_instance_file)

            # Add worker to synced workers when synced
            self._synced_workers.add(worker_node.user_host)

    def start_console(self, worker_stage):
        self._log.info("Starting grinder console on node %s", worker_stage.console.user_host)
        self.spawn_command(worker_stage.console, [
            "java",
            "-cp",
            "%s/execution/lib/grinder-3.11/lib/grinder.jar" % self._run_config['worker_e3_dir'],
            "-Dgrinder.console.httpHost=%s" % worker_stage.console.hostname,
            "-Dgrinder.logLevel=info",
            "net.grinder.Console",
            "-headless"
        ])
        Utils.poll_url("http://%s:6373/version" % worker_stage.console.hostname, 600,
                       lambda response: response.text == 'The Grinder 3.11')

    def start_agents(self, worker_stage):
        self._log.info("Starting grinder agents on workers")
        for worker in worker_stage.worker_nodes:
            self.spawn_command(worker, [
                "java",
                "-cp",
                "%s/execution/lib/grinder-3.11/lib/grinder.jar" % self._run_config['worker_e3_dir'],
                "-Dcom.sun.management.jmxremote",
                "-Dcom.sun.management.jmxremote.port=3333",
                "-Dcom.sun.management.jmxremote.authenticate=false",
                "-Dcom.sun.management.jmxremote.ssl=false",
                "-Dgrinder.consoleHost=%s" % worker_stage.console.hostname,
                '-Dgrinder.jvm.arguments=-Droot=%s -Dinstance=%s -Dworkload=%s -DagentCount=%s' % (
                    self._run_config['data_dir'],
                    worker_stage.instance['stack']['Name'],
                    worker_stage.workload,
                    len(worker_stage.worker_nodes)
                ),
                "net.grinder.Grinder",
                "-daemon", "2"
            ], cwd='%s/execution/grinder' % self._run_config['worker_e3_dir'])
        Utils.poll_url("http://%s:6373/agents/status" % worker_stage.console.hostname, 600,
                       lambda response: len(json.loads(response.text)) == len(worker_stage.worker_nodes))

    def start_stage(self, worker_stage):
        self._log.info("Beginning execution of load (%s/stage-%s)" % (self._run_name, worker_stage.key))
        requests.post('http://%s:6373/agents/start-workers' % worker_stage.console.hostname, timeout=60,
                      data=json.dumps({
                          "grinder.duration": "%d" % worker_stage.duration,
                          "grinder.logDirectory": "../../../runs/%s/stage-%s" % (self._run_name, worker_stage.key),
                          "grinder.numberOfOldLogs": "0",
                          "grinder.processes": "1",
                          "grinder.runs": "0",
                          "grinder.script": "TestRunner.py",
                          "grinder.threads": "%d" % worker_stage.clients_per_worker
                      }),
                      headers={"Content-Type": "application/json"})

    def wait_finish(self, worker_stage):
        wait_seconds = worker_stage.duration / 1000.0
        self._log.info("Waiting %d seconds for load execution to complete", wait_seconds)
        time.sleep(wait_seconds)
        Utils.poll_url("http://%s:6373/agents/status" % worker_stage.console.hostname, 600, self.workers_finished)
        requests.post('http://%s:6373/agents/stop' % worker_stage.console.hostname, timeout=600)
        Utils.poll_url("http://%s:6373/agents/status" % worker_stage.console.hostname, 600, self.workers_stopped)
        self._log.info("Waiting another 10 seconds for agents to gracefully exit")
        time.sleep(10)

    @staticmethod
    def workers_stopped(response):
        for node in json.loads(response.text):
            if len(node['workers']) > 0:
                return False
        return True

    @staticmethod
    def workers_finished(response):
        for node in json.loads(response.text):
            for worker in node['workers']:
                if 'state' in worker and worker['state'] != 'FINISHED':
                    return False
        return True

    def run_command(self, worker_node, cmd, cwd=None, is_sudo=False):
        stdout = LogWrapper(worker_node.hostname, LogWrapper.stdout)
        stderr = LogWrapper(worker_node.hostname, LogWrapper.stderr)
        return self.do_run_command(worker_node, cmd, cwd, is_sudo, stdout, stderr)

    def do_run_command(self, worker_node, cmd, cwd=None, is_sudo=False, stdout=None, stderr=None):
        """
        Executes the specified command on a remote node
        :param worker_node: The node on which to execute the command
        :param cmd: The command to execute
        :param cwd: The working folder from which to launch the command
        :param is_sudo: Does the comment include sudo
        :param stdout: The output from stdout will be written here
        :param stderr:  The output from stderr will be written here
        :return: The process exit code
        :rtype: ExecutionResult
        """
        if type(cmd) is str:
            run_command = cmd.split(" ")
        else:
            run_command = cmd
        args = {
            "allow_error": True,
            "cwd": cwd,
            "stderr": stderr,
            "stdout": stdout
        }
        if is_sudo:
            args["use_pty"] = True
        result = worker_node.shell.run(run_command, **args)
        self._log.debug("%s -- cwd: %s, exit code: %d, instance: %s, user_host: %s, stdout: \"%s\", stderr: \"%s\"",
                        " ".join(run_command), cwd, result.return_code, worker_node.instance, worker_node.user_host,
                        result.output.rstrip(), result.stderr_output.rstrip())
        return result

    def spawn_command(self, worker_node, cmd, cwd=None):
        stdout = LogWrapper(worker_node.hostname, LogWrapper.stdout)
        stderr = LogWrapper(worker_node.hostname, LogWrapper.stderr)
        if type(cmd) is str:
            run_command = cmd.split(" ")
        else:
            run_command = cmd
        result = worker_node.shell.spawn(run_command, allow_error=True, cwd=cwd, stdout=stdout, stderr=stderr)
        self._log.debug("%s -- cwd: %s running: %d,  instance: %s, user_host: %s", " ".join(run_command), cwd,
                       result.is_running(), worker_node.instance, worker_node.user_host)

    def restart_bitbucket(self, worker_stage):
        for instance in worker_stage.instance_nodes:
            self.run_command(instance, "sudo service atlbitbucket restart")
        self._log.info("Sleeping for two minutes to allow bitbucket server time to restart")
        time.sleep(120)

    def _remotely_kill_process(self, node, signal, pid=None, process=None):
        """
        Kill a process on a remote node using the provided signal number and process id (PID)
        :param node: The node on which the process should be killed
        :type node: Node
        :param signal: The signal number to send to the process (TERM, KILL, HUP, 0)
        :type signal: str
        :param pid: The PID of the process to kill
        :type pid: int
        :return: True on success else False
        :rtype: bool
        """
        if pid or process:
            if pid:
                return self.run_command(node, "kill -s %s %d" % (signal, pid)).return_code == 0
            else:
                return self.run_command(node, "killall -s %s %s" % (signal, process)).return_code == 0
        else:
            logging.warn("You must specify either a process name or a pid to kill")
            return False


class WorkerStage:
    def __init__(self, thread, stage):
        self._log = logging.getLogger("run")
        self.clients = stage['clients']
        self.instance = thread['instance']
        self.worker = thread['worker']
        self.duration = stage['duration']
        self.workload = stage['workload']
        self.key = stage['key']

        self.worker_nodes = self.make_nodes(self.worker['stack']['Name'])
        self.instance_nodes = self.make_nodes(self.instance['stack']['Name'])

        self.console = self.worker_nodes[0]
        self.clients_per_worker = float(stage['clients']) / len(self.worker_nodes)

    def make_nodes(self, instance_id):
        nodes = []
        self._log.debug("Loading instance config for instance %s ", instance_id)
        instance_config = e3.load_instance(instance_id)
        self.instance_nodes = []
        for user_host in instance_config['ClusterNodes']:
            if user_host == 'localhost':
                shell = spur.LocalShell()
            else:
                (username, hostname) = user_host.split("@")
                shell = spur.SshShell(
                    hostname=hostname,
                    username=username,
                    private_key_file='%s/%s/%s.pem' % (e3.get_e3_home(), "instances", instance_id),
                    missing_host_key=spur.ssh.MissingHostKey.accept,
                    connect_timeout=3600
                )
            nodes.append(Node(instance_id, user_host, shell))
        return nodes


class Node:
    def __init__(self, instance, user_host, shell):
        self.instance = instance
        self.user_host = user_host
        if '@' in user_host:
            self.hostname = user_host.split('@')[1]
        else:
            self.hostname = user_host
        self.shell = shell


@click.command()
@click.option('-r', '--run', required=True, help='The experiment run you want to execute',
              type=click.Choice(e3.get_runs()), default=e3.get_single_run())
def command(run):
    logging.config.fileConfig(e3.get_logging_conf())
    run_inst = Run(run)
    run_inst.run()


if __name__ == '__main__':
    command()
