# E³: Elastic Experiment Executor

E³ is a framework to set up, execute, and analyze performance experiments on Bitbucket Server and Data Center instances.
These experiments can be useful to compare the performance of different Bitbucket versions, software configurations, and
hardware infrastructure setups under workloads of different sizes and shapes.

While the experiment runs, both system-level and application-level metrics are monitored from all machines involved
using the [`collectd`](https://collectd.org/) service. This information, as well as data on response times and throughput
gathered from client and server-side logfiles can be summarized in a number of different graphical charts and visualizations.

The machine(s) that run the actual client(s) and Bitbucket node(s) can be any machines you have access to, or (if you
prefer) can all be provisioned automatically in the Amazon Web Services (AWS) cloud.

- [Setup](#markdown-header-setup)
    - [Pre-requisites](#markdown-header-pre-requisites)
    - [Installing](#markdown-header-installing)
- [Getting started](#markdown-header-getting-started)
- [Experiments](#markdown-header-experiments)
    - [Defining an Experiment](#markdown-header-defining-an-experiment)
    - [Experiment Phases](#markdown-header-experiment-phases)
    - [Snapshots](#markdown-header-snapshots)
    - [Workloads](#markdown-header-workloads)
    - [Analysis](#markdown-header-analysis)
- [Contributing](#markdown-header-contributing)
- [License](#markdown-header-license)

## Setup

### Pre-requisites

#### Software
E³ requires a Linux or MacOS machine with a number of open source software packages. The easiest way to install these
pre-requisites is with your operating system's package manager. For example:


##### MacOS with homebrew
    brew    install gnuplot --with-cairo
    brew    install imagemagick python rrdtool
   
##### Linux Ubuntu, Debian, ...
    apt-get install gnuplot imagemagick python rrdtool

##### Linux Red Hat, CentOS, ...
    yum     install gnuplot imagemagick python rrdtool


For other systems, refer to your system's documentation on how to install these prerequisites.

#### AWS

E³ provides the ability to easily provision machines in the AWS Cloud.

You can specify the credentials for your AWS account in any of the places that `boto3` looks.
(See [configuring credentials](https://boto3.readthedocs.io/en/latest/guide/configuration.html#configuring-credentials).)

If your organization uses IAM roles to autheticate with AWS, E³ also includes the ability to acquire AWS credentials
automatically. For an example implementation information see [`AtlassianAwsSecurity.py`](provisioning/AtlassianAwsSecurity.py).

```
  .     Warning:
 / \    Provisioning AWS infrastructure can incur significant service charges from Amazon.
/ ! \   You are responsible for all Amazon service charges arising from your use of the E³ framework.
‾‾‾‾‾   You are responsible for securing any proprietary data on your test machines.
```


### Installing

Most of E³ is written in Python and requires a number of Python libraries. These requirements are described in a standard
`requirements.txt` file, and can be installed using the standard Python `pip` and `virtualenv` tools as follows:

```bash
sudo pip install virtualenv
virtualenv .ve
source .ve/bin/activate
pip install -r requirements.txt
```

## Getting started

To provision machines to run, gather data, and analyze an experiment designed to stress different
Bitbucket instances with lots of parallel Git hosting operations over SSH:

```bash
./Orchestrate.py -e cluster-scaling-ssh
```

## Experiments

### Defining an Experiment

Experiments are described in JSON files that define:

* the independent experiment thread(s) to run (in parallel),
* the size and shape of the Bitbucket instance(s) under test,
* the shape of the data (projects, repositories, users, etc.) in the Bitbucket instance(s),
* the size and shape of the client machine(s) that put load on the Bitbucket instance(s), and
* the mix of operations in the workload, and
* the amount of load to apply in each stage of the experiment (the number of client threads).

There is a library of pre-defined experiments under [`e3-home/data/experiments`](./e3-home/data/experiments),
or you can define your own.

The workloads referenced in the experiment JSON file are defined in [`e3-home/data/workloads`](./e3-home/data/workloads).

### Experiment Phases

Performance experiments have a number of phases, which correspond to the the following entry points:

1. [`Provision`](./e3/Provision.py), which spins up Bitbucket instance(s), cluster(s) of worker machines, and other associated
   infrastructure in AWS. Will automatically create a 'run file' in [`e3-home/runs`](./e3-home/runs) from your experiment
   definition. (You can skip this step if you have your own infrastructure, but you will need to
   create a run file and fill in your machines' details first.)
2. [`Run`](./e3/Run.py), which actually runs the client workload from the worker machine(s) (and also resets the
   Bitbucket instance(s) to a known good state in between stages).
3. [`Gather`](./e3/Gather.py) which gathers data from an experiment run (either running or finished) off all the machines.
4. [`Analyze`](./e3/Analyze.py) which analyzes the data from an experiment run into charts that help visualize how well the
   instance(s) performed and all their "vital signs" while under stress.
5. [`Deprovision`](./e3/Deprovision.py) which deprovisions the test machines and archives the experiment run.

In addtion to the global [`Orchestrate`](./e3/Orchestrate.py) entry point, which runs all these phases in order,
each phase can also be run individually:

```bash
cd ./e3
./Provision.py -e <experiment_name>
./Run.py -r <run_name>
./Gather.py -r <run_name>
./Analyze.py -r <run_name>
```

### Snapshots

Snapshot descriptor files are used to describe a Bitbucket dataset.
They are stored in [`e3-home/snapshots`](./e3-home/snapshots).
Atlassian provides a number of default snapshots:

- [`e3-medium`](./e3-home/snapshots/e3-medium.json)
- [`bitbucket-e3-small`](./e3-home/snapshots/bitbucket-e3-small.json)
- [`bitbucket-e3-medium`](./e3-home/snapshots/bitbucket-e3-medium.json)

These default snapshots all have:

- a public [EBS snapshot](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSSnapshots.html) of the file server
- a public [RDS snapshot](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Overview.BackingUpAndRestoringAmazonRDSInstances.html#Overview.BackingUpAndRestoringAmazonRDSInstances-Snapshots)
of the Database
- a public [Elasticsearch snapshot](https://www.elastic.co/guide/en/elasticsearch/reference/2.3/modules-snapshots.html) in [S3](https://docs.aws.amazon.com/AmazonS3/latest/dev/Welcome.html)
containing the search index

for the data described in the JSON snapshot descriptor.

If you are running experiments in AWS, these default snapshots can help to quickly get you up and running experiments.

If you are running experiments elsewhere, you will need to provide E3 with a descriptor of the dataset of the Bitbucket
instance you are running an experiment against.
To generate a new snapshot descriptor you can use the [`Snapshot`](./e3/util/Snapshot.py) script:

```bash
./util/Snapshot.py --url "https://bitbucket-instance" --username admin --password admin --name snapshot-name --description "snapshot description"
```

#### Creating your own dataset in AWS

After you have run the `./util/Snapshot.py` script with the `--aws true` option, you will need to take an [EBS](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSSnapshots.html)
 (and possibly [RDS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Overview.BackingUpAndRestoringAmazonRDSInstances.html#Overview.BackingUpAndRestoringAmazonRDSInstances-Snapshots)
  and [Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/2.3/modules-snapshots.html)) snapshot of your data.
This is most easily achieved through the use of the Atlassian Bitbucket DIY backup scripts, which come with the Atlassian Bitbucket AMI.
Alternatively, you can clone the repository from [bitbucket.org](https://bitbucket.org/atlassianlabs/atlassian-bitbucket-diy-backup/overview).

See [Using Bitbucket Server DIY backup in AWS](https://confluence.atlassian.com/bitbucketserver/using-bitbucket-server-diy-backup-in-aws-776640203.html).

You will then need to configure the snapshot fields for EBS (git repositories), RDS (database) and ES (search index) in the generated snapshot (see example below)

The following example configuration specifies snapshots taken from a Bitbucket Data Center instance.
```json
"ebs": {
    "ap-southeast-2": "snap-5387b4a1",
    "us-east-1": "snap-25e718aa"
},
"rds": {
    "account": "098706035825",
    "id": "e3-medium"
},
"es": {
    "id" : "e3-medium",
    "bucket": "bitbucket-server-e3"
}
```

#### SSH Keys

A keys file can be used to store public/private key pairs, which users are supposed to use to authenticate with Bitbucket when running an experiment.
These descriptors are stored in [`e3-home/keys`](./e3-home/keys).

If you are using an existing dataset, you will need to provide the public and private SSH keys that E³ can use to authenticate over SSH.
If you provide a `key-file` to the `Snapshot` script, it will look up the users in your instance and map the private key to the configured public key for each user.

#### Passwords

Currently, the `Snapshot` script assumes all users have the same password (`password` by default). 

**Note:** 
E³ assumes every user has access to every project/repository. Test scripts are not resilient to failures because of insufficient permissions.

### Workloads

A workload defines the types and distribution of execution scripts run in your experiment. You can only define a single workload per experiment.
Workload descriptors are stored in [`e3-home/workloads`](./e3-home/workloads).

A workload description contains: 

- `script`: the path of the script relative to the `e3/execution/grinder` directory
- `description`: the name of the description; used in graphs produced by analysis
- `scale`: the relative weight to give the experiment in the analysis stage. Can be used to reduce the visual impact of less important or cheaper operations.
- `weight`: the weight to give to this execution script. All weights should add up to 1.0

#### Weights 

The way E³ assigns work to client threads and workers means that weights in a workload definition do not have infinite resolution.
An example to illustrate this: 

##### experiment.json

```json
{
    ...
    "stages": [
        {
            "clients": 10
        },
        {
            "clients": 20
        }
    ]
}
```

Because the experiment defined above is running a stage with only 10 clients, the maximum resolution the weights can afford is 1/10 or 0.1.
Therefore defining a workload that contains a script with a weight under 0.1 may not be executed.

E³ will also attempt to distribute client threads amongst all worker machines evenly. This means when choosing the number of client threads for each stage,
you should aim to ensure the number is divisible by the number of worker machines you have allocated.

### Analysis

E³ provides the ability to produce graphs from the data collected from the worker machines as well as the Bitbucket machines.

There are 2 types of analysis scripts included: 

- `gnuplot`
- `rrdtool`

Calling `./e3/Analyze.py -r <run_name` will produce both types of graphs for a specific run.

To produce only one type of graph:

    ./e3/analysis/gnuplot/Analyze.py <run_name>

or

    ./e3/analysis/rrdtool/Analyze.py -r <run_name>

Any produced graphs will be stored in the `e3-home/runs/<run_name>/analysis` directory.

For more information on Analysis, see the dedicated [README](./e3/analysis/README.md).

---

## Contributing

Pull requests, issues and comments welcome. For pull requests:

* Follow the existing style
* Separate unrelated changes into multiple pull requests

See the existing [issues](https://bitbucket.org/atlassian/elastic-experiment-executor/issues?status=new&status=open) for things to start contributing.

For bigger changes, make sure you start a discussion first by creating
an issue and explaining the intended change.

Atlassian requires contributors to sign a Contributor License Agreement,
known as a CLA. This serves as a record stating that the contributor is
entitled to contribute the code/documentation/translation to the project
and is willing to have it used in distributions and derivative works
(or is willing to transfer ownership).

Prior to merging your pull requests, please follow the appropriate
link below to digitally sign the CLA. The Corporate CLA is for those who are
contributing as a member of an organization and the individual CLA is for
those contributing as an individual.

* [Corporate CLA](https://na2.docusign.net/Member/PowerFormSigning.aspx?PowerFormId=e1c17c66-ca4d-4aab-a953-2c231af4a20b)
* [Individual CLA](https://na2.docusign.net/Member/PowerFormSigning.aspx?PowerFormId=3f94fbdc-2fbe-46ac-b14c-5d152700ae5d)

## License

Copyright (c) 2016 Atlassian and others.
Apache 2.0 licensed, see [LICENSE.txt](LICENSE.txt) file.
