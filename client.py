import json
import click
import globals
from config import *

# define a group
@click.group()
def client():
    '''client set/get/delete'''
    pass

@click.command()
@click.option('--id', prompt='Node ID', help='ID of Node')
@click.option('--key', prompt='Key', help='key')
def get(id, key):
    cmd = "curl -v http://{}:{}/key/{}".format(id, GRAFTD_HTTP_PORT, key)
    o = globals.graftd_client.exec_run(cmd)
    click.echo(o.output)

@click.command()
@click.option('--id', prompt='Node ID', help='ID of Node')
@click.option('--key', prompt='Key', help='key')
@click.option('--value', prompt='Value', help='value')
def set(id, key, value):
    cmd = "curl -v -XPOST http://{}:{}/key -d'{}'".format(id, GRAFTD_HTTP_PORT, json.dumps({key : value}, separators=(',',':')))
    o = globals.graftd_client.exec_run(cmd)
    click.echo(o.output)

@click.command()
@click.option('--id', prompt='Node ID', help='ID of Node')
@click.option('--key', prompt='Key', help='key')
def delete(id, key):
    cmd = "curl -v -XDELETE http://{}:{}/key/{}".format(id, GRAFTD_HTTP_PORT, key)
    o = globals.graftd_client.exec_run(cmd)
    click.echo(o.output)

client.add_command(get)
client.add_command(set)
client.add_command(delete)