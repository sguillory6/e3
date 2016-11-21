# Running Grinder Locally

### Library setup

Right click on __e3/execution/lib/grinder-3.11/lib__ in the Project view, select __Add as library__

Once the folder has been added as a library.
You can proceed with the launch configuration creation.
 

### Launch configuration

__To execute grinder locally for development purposes you can set up a launch configuration__

##### Main Class

* net.grinder.Grinder

##### VM Options

* -javaagent:/Users/charles/.m2/repository/net/sf/grinder/grinder-dcr-agent/3.11/grinder-dcr-agent-3.11.jar
* -Dgrinder.debug.singleprocess=true
* -Dgrinder.useConsole=false
* -Dgrinder.runs=0
* -Dgrinder.duration=180000
* -Dgrinder.script=TestRunner.py
* -Droot=../../../e3-home
* -Dinstance=bitbucket-data-center-charles-d69c68
* -Dworkload=high-traffic-web
* -DagentCount=1

##### Working directory

* /path/to/atlassian-aws-deployment-e3/e3/execution/grinder

##### Use classpath of module

* select __atlassian_aws_deployment-e3__
