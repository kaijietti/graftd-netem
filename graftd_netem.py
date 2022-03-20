import imp
import click
# globals
import globals
# command groups
from node import node
from netem import netem
from partition import partition
from client import client
from log import log

# define a group
@click.group()
def cli():
    '''graftd-netem module'''
    # init
    globals.init()
    pass

cli.add_command(node)
cli.add_command(netem)
cli.add_command(partition)
cli.add_command(client)
cli.add_command(log)

if __name__ == '__main__':
    cli()