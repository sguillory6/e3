# E3: Elastic Experiment Executor

E3 is a framework to set up, execute, and analyze performance experiments on Bitbucket Server and Data Center instances.
You can run it from your own machine(s), or (optionally) provision all the machines you need using Amazon Web Services (AWS).

Experiments are described in JSON files that define:

* the independent stage(s) to run (in parallel),
* the size and shape of the instance(s) under test,
* the size and shape of the worker machine(s) that  (often important when ), and
* the mix of operations in the workload, and
* the amount of load to apply in each step of the experiment. 

There is a library of pre-defined experiments under `data/experiments`, or you can define your own. 

## Setup

E3 depends on a number of open source software packages. The easiest way to install these pre-requisites is with your
operating system's package manager. For example (choose the line most appropriate for you):

```
# MacOS with homebrew
    brew    install gnuplot --with-cairo
    brew    install imagemagick python rrdtool
    
# Linux Ubuntu, Debian, ...
    apt-get install gnuplot imagemagick python rrdtool

# Linux Red Hat, CentOS, ...
    yum     install gnuplot imagemagick python rrdtool
```

Most of E3 is written in Python and requires a number of Python libraries to be installed. One way to do this is as
follows:

```
sudo pip install virtualenv
virtualenv .ve
source .ve/bin/activate
pip install -r requirements.txt
```

If you provision your experiments in AWS, you must have an AWS account with permission to create resources. You can
specify the credentials for your AWS account in any of the places that `boto3` looks.
(See https://boto3.readthedocs.io/en/latest/guide/configuration.html#configuring-credentials.)

**Warning: Provisioning AWS infrastructure can incur significant service charges from Amazon. You are responsible for all
Amazon service charges arising from your use of the E3 framework.**

## Getting started

To provision, run, and gather data from an experiment designed to stress different Bitbucket instances with
lots of parallel Git hosting operations over SSH:

```
./Orchestrate.py -e cluster-scaling-ssh
```

## More advanced usage

Performance experiments have a number of phases, which correspond to the the following packages:

* `generator`, which generates random test data for the Bitbucket instance. 
  (You can skip this step if you already have some test data, or are willing to use one of the pre-generated
  test data snapshots provided by Atlassian.)
* `provisioning`, which spins up Bitbucket instance(s), cluster(s) of worker machines, and other associated
  infrastructure in AWS. (You can skip this step if you have your own infrastructure, but you will need to
  fill in your machines' details into your experiment file first.)
* `execution` which actually runs the client workload from the worker machine(s) (and also resets the
  Bitbucket instance(s) to a known good state in between stages).
* `gather` which gathers data from an experiment run (either running or finished) off all the machines.
* `analysis` which analyzes the data from an experiment run into charts that help visualize how well the
  instance(s) performed and all their "vital signs" while under stress.

These phases can be run individually or 

```
./provisioning/Provision.py -e cluster-scaling.ssh
./Run.py 
```

### Snapshot generation.

The snapshot generation script can be run by executing the Snapshot.py script like so.
`/Snapshot.py --url "https://stash-instance" --username admin --password admin --repo-count 100 --distribution exponential --distribution-factor 2 --name name --description "snapshot description"`


## Experiment?
An experiments defines.
#### Topology
Defines a set of nodes that will be orchestrated in order to run an experiment in practise these will either be `ec2` or
`RDS` instances running in `AWS` this can be further broken down into `System topology` and `Test Topology`. Each
topology will support further configuration options such as  `ec2-instance-type` and `ebs-volume-type`.
##### System Topology
Defined the system under test that the experiment will be run against. Some of the topologies that will be supported
include.
* Standalone bitbucket instance connected to postgresql database all running on the same ec2-instance.
* Bitbucket data centre cluster comprising (2,4) nodes connected to RDS database.
* Bitbucket data centre cluster comprising (2,4) nodes connected to RDS database with x mirrors.
##### Test Topology
Defines the number of nodes that will be orchestrated in order to place load on the system under test.
#### Test data
Define the test data to be loaded into the system under test essentially comprises a tuple of ec2 volume snapshots comprising
Repository data and database data.
#### Load
This defines the type and volume of load to be executed against the system under test by the test topology. A registry of
intrinsic will be built up over time to reflect realistic user behaviour.
#### Collect
Defines the data to be collected from the experiment and how often to collect it.
#### Analysis
Defines the analysis steps to be performed against the data collected.

## Third party components

This framework makes use of the following technologies.

* [Python](https://www.python.org/)
* [AWS](https://aws.amazon.com/)
* [boto3](https://github.com/boto/boto3) AWS SDK for Python.
* [collectd](https://collectd.org/) to fetch metrics from Experiment runs.
* [Grinder](http://grinder.sourceforge.net/) to co-ordinate test load across a number of machines.
* [Click](http://click.pocoo.org/5/) Command line option passing

#### Components

At a high level this framework is made up of the following independent components. Each component will support reading/
writing to a json file that describes the work done or the work desired.

##### Validation
Takes a best effort approach to ensuring that an experiment will not fail because of something that could have been
checked upfront for example checking that all `AWS` resources defined as being part of an Experiment exist.
##### Orchestration
The orchestration component is responsible for taking `Experiment` config and setting up all the resource into a state
into which test runs can begin. This includes provisioning both the `System Topology` as well as the `Test Topology`,
Running any custom data setup that a targeted `Experiment` desires.
To see options for orchestration run `./python Orchestrate.py --help`
##### Workload
Perform load against a `System Topology`
##### Collect
Collect data from a test topology
##### Analyze
Perform analysis against the data collected in the previous step.



# TODO
* Provision system under test with test data snapshot
* Provision system under test with collectd.
* Save the results of the orchestration step to .json file
* Add more functionality to orchestrate command line to enable the querying the resources provisioned by a experiment
* Add proper logging
* Tests
