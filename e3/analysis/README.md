# E³ - Analyzing Results

E³ includes two types of analysis chart output types: [`gnuplot`](./gnuplot) and [`rrdtool`](./rrdtool).

While some of the charts produced by these tools overlap, some charts are only available in one tool. This
guide should serve as an introduction into using E³ to analyze your experiment data, as well as showing
you how to interpret the results.

- [Server Vital Signs](#markdown-header-server-vital-signs)
- [Experiment Summaries](#markdown-header-experiment-summaries)
- [Stage Summaries](#markdown-header-stage-summaries)
    - [`gnuplot`](#markdown-header-gnuplot)
    - [`rrdtool`](#markdown-header-rrdtool)

## Server Vital Signs

Some data is graphed by both the `gnuplot` and `rrdtool` scripts, for example: 

- Server CPU usage
- Server memory usage
- Bitbucket "Hosting Ticket" usage and limit
- Hazelcast remote operations
- Server network I/O

These statistics can help you determine under how much load the system running Bitbucket is, as well as whether or not
there is spare capacity. If, for example, you are seeing very even network I/O, which is seemingly topping out, while
other metrics are not showing signs of exhaustion, you may have a bottleneck in the network infrastructure.

## Experiment Summaries

The `gnuplot` scripts will produce several charts which serve to compare experiment threads: 

- **Throughput** - This chart shows a summary of the average "Tests per second (TPS)" that were run in each stage.
  Note that some tests may throw this metric out of balance: some tests run significantly faster and more often than 
  others. The `scale` value in your `workload` JSON file can help to offset this unbalance.

  ![throughput.png](https://developer.atlassian.com/blog/2016/12/how-we-built-bitbucket-data-center-to-scale/throughput.png)

- **Mean Test Time** - This chart shows the mean time to complete each test _as reported by the worker_. These charts
  can help determine which operations slow down under load. Note that this metric is a _mean_, which means outliers can
  disproportionatley affect this value.

- **Histogram** - This chart shows a Histogram for each experiment thread. It will indicate the contribution to TPS
  of each test in the experiment.

  ![histogram.png](https://developer.atlassian.com/blog/2016/12/how-we-built-bitbucket-data-center-to-scale/histogram-thread-008.png)

## Stage Summaries

### `gnuplot`

The `gnuplot` scripts will also produce a "stage summary" for every experiment thread. This summary is a single file that
contains many cluster and worker metrics for the relevant thread and stage: 

- **Gantt chart** - This chart indicates which client threads were running which tests, as well as how long each test took.

- **Scatter plot** - This chart plots a point for each test run on. The y-axis is a logarithmic scale of test duration, the
  x-axis indicates time in the stage.

- **CPU** - These charts indicate worker, file server and cluster node CPU utilization.

- **Network** - These charts indicate network utilization. Both the number of octets and packets are graphed.

- **Memory** - These charts indicate the worker, file server and cluster node memory utilization.

- **Hosting tickets** - These charts indicate the available and used Bitbucket Hosting Tickets. Hosting tickets are
  acquired for Git operations and are used throttle load in order to prevent overloading the server.

- **Queued Hosting Operations** - These charts indicate the number of queued hosting operations for each cluster node.
  Once the available hosting tickets have been used, Bitbucket will begin queuing Git requests.

- **Hazelcast statistics** - These charts indicate the cluster's "chattyness".

- **Database Connections** - These charts indicate the number of active database connections for each cluster node.


### `rrdtool`

The `rrdtool` scripts will produce a per-stage HTML report for every experiment thread. This summary includes the above
mentioned vital signs, as well as many other metrics useful for "drilling down" on a per-stage level, for example: 

- **Git process count** - The number of `git` processes running on each cluster node

- **Java on-heap and off-heap memory** - The used, committed, and max Java heap, as well as the "non-heap" Java memory.

- **Disk usage** - The amount of disk I/O on various devices attached to cluster nodes and file server.

