import click
import globals
import docker
from clint.textui import puts, colored, columns
from config import *

# define a group
@click.group()
def node():
    '''node add/pause/resume/stop'''
    pass

# control node
@click.command()
@click.option('--id', prompt='Node ID', help='ID of Node')
@click.option('--join', prompt='Leader ID', default='', help='ID of Leader')
def start(id, join):
    '''Start graftd node'''
    join_cmd = ''
    if join != '':
        join_cmd = f'-join {join}:{GRAFTD_HTTP_PORT}'

    try:
        # restore node if exists
        node = globals.docker_client.containers.get(id)
        node.start()
    except docker.errors.NotFound:
        globals.docker_client.containers.run(
            GRAFTD_IMAGE,
            command=f'/raftnode -id {id} {join_cmd} ~/{id}',
            detach=True,
            cap_add=['NET_ADMIN'],
            name=id,
            hostname=id,
            network=GRAFTD_NETWORK,
            labels={'aliyun.logs.catalina': 'stdout'},
            publish_all_ports=True,
            environment=[
                "ELECTION_TIMEOUT=10000",  #ms
                "HEARTBEAT_TIMEOUT=10000", #ms
                "COMMIT_TIMEOUT=50", #ms
                "IGNORE_EMPTY_APPEND=1",
                "SNAPSHOT_INTERVAL=20", #second
                "SNAPSHOT_THRESHOLD=5" 
            ]
            #remove=True
        )

# control node
@click.command()
@click.option('--id', prompt='Node ID', help='ID of Node')
def remove(id):
    '''Remove graftd node'''
    try:
        # remove node if exists
        node = globals.docker_client.containers.get(id)
        node.remove(force=True)
    except docker.errors.NotFound as e:
        click.echo(e)

@click.command()
@click.option('--id', prompt='Node ID', help='ID of Node')
def pause(id):
    '''Pause graftd node'''
    n = globals.docker_client.containers.get(id)
    n.pause()

@click.command()
@click.option('--id', prompt='Node ID', help='ID of Node')
def stop(id):
    '''Stop graftd node'''
    n = globals.docker_client.containers.get(id)
    n.stop()

@click.command()
@click.option('--id', prompt='Node ID', help='ID of Node')
def unpause(id):
    '''Unpause graftd node'''
    n = globals.docker_client.containers.get(id)
    n.unpause()

def get_node_ip(node):
    return node.attrs['NetworkSettings']['Networks'][GRAFTD_NETWORK]['IPAddress']

@click.command()
def show():
    nodes = filter(lambda c: c.image.tags[0] == GRAFTD_IMAGE, globals.docker_client.containers.list())
    nodes = sorted(nodes, key=lambda c: c.name)

    puts(colored.blue(columns(["NODE",               10],
                              ["CONTAINER ID",       15],
                              ["STATUS",             10],
                              ["IPAddress",          15])))


    for node in nodes:
        puts(columns([node.name,                    10],
                     [node.id[:12],                 15],
                     [node.status,                  10],
                     [get_node_ip(node),            15]))

def stop_nodes():
    nodes = filter(lambda c: len(c.image.tags) != 0 and c.image.tags[0] == GRAFTD_IMAGE, globals.docker_client.containers.list())
    for n in nodes:
        try:
            n.remove(force=True)
            click.echo(f"successfully stopped {n.name}")
        except docker.errors.APIError as e:
            click.echo(e)

# docker operation
node.add_command(start)
node.add_command(stop)
node.add_command(remove)
node.add_command(pause)
node.add_command(unpause)
node.add_command(show)
