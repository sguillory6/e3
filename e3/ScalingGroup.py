import logging
import logging.config
import click

from common.E3 import e3
from provisioning.Aws import Aws


@click.command()
@click.option('-name', '--name', required=True, help='Scaling group name')
@click.option('-desired', '--desired', required=True, help='Number of instance in scaling group')
@click.option('-max', '--max_size', required=False, help='Number of max instance in scaling group')
@click.option('-min', '--min_size', required=False, help='Number of min instance in scaling group')
def command(name, desired, max_size, min_size):
    e3.setup_logging()
    if not name:
        logging.error("Please provide name of the scaling group %s" % name)
        return

    if desired <= 0:
        logging.error("Please provide positive number for desired parameter")
        return

    if max_size < min_size:
        max_size = min_size

    if max_size <= 0 and min_size <= 0:
        max_size = min_size = desired

    Aws.auto_scaling.update_auto_scaling_group(
        AutoScalingGroupName=name,
        MinSize=min_size,
        MaxSize=max_size,
        DesiredCapacity=desired)

if __name__ == '__main__':
    command()
