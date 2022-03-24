import click
import docker
# globals
import globals
from config import *
# command groups
from netem import netem
from partition import partition
import node
import log
import client

# define a group
@click.group()
def cli():
    '''graftd-netem module'''
    # init
    globals.init()
    globals.init_net()

@click.command()
def reset():
    # stop all nodes
    node.stop_nodes()
    # clear partitions
    globals.iptables.clear()
    # stop client
    try:
        globals.docker_client.containers.get(GRAFTD_CLIENT_NAME).remove(force=True)
        click.echo(f"successfully removed client:{GRAFTD_CLIENT_NAME}")
    except docker.errors.NotFound as e:
        click.echo(e)
    # stop log
    log.stop_log()
    # remove network
    try:
        globals.docker_client.networks.get(GRAFTD_NETWORK).remove()
        click.echo(f"successfully removed network:{GRAFTD_NETWORK}")
    except docker.errors.NotFound as e:
        click.echo(e)
    pass

cli.add_command(netem)
cli.add_command(partition)
cli.add_command(node.node)
cli.add_command(client.client)
cli.add_command(log.log)
# reset all
cli.add_command(reset)

if __name__ == '__main__':
    cli()