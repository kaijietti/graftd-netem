import imp
import click
# globals
import globals
# command groups
from node import node
from netem import netem

# define a group
@click.group()
def cli():
    '''graftd-netem module'''
    # init
    globals.init()
    pass

cli.add_command(node)
cli.add_command(netem)

if __name__ == '__main__':
    cli()