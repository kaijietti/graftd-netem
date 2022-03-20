import click
import globals
from clint.textui import puts, colored, columns
from config import DOCKER_USER_CHAIN, GRAFTD_IMAGE, GRAFTD_NETWORK, PARTITION_CHAIN_PREFIX

# define a group
@click.group()
def partition():
    '''partition show/clear/create'''
    pass

def list_minus(x, y):
    return [item for item in x if item not in y]

def get_node_ip(node):
    return node.attrs['NetworkSettings']['Networks'][GRAFTD_NETWORK]['IPAddress']

@click.command()
def show():
    # lines = globals.iptables.get_chain_rules(DOCKER_USER_CHAIN)
    # for line in lines:
    #     puts(line)
    m = globals.iptables.get_source_chains()

    nodes = filter(lambda c: c.image.tags[0] == GRAFTD_IMAGE, globals.docker_client.containers.list())
    nodes = sorted(nodes, key=lambda c: c.name)

    puts(colored.blue(columns(["NODE",               10],
                              ["CONTAINER ID",       15],
                              ["STATUS",             10],
                              ["IPAddress",          15],
                              ["Partition",          15])))


    for node in nodes:
        puts(columns([node.name,                    10],
                     [node.id[:12],                 15],
                     [node.status,                  10],
                     [get_node_ip(node),            15],
                     [m.get(get_node_ip(node), 'NULL'),15]))

@click.command()
def clear():
    globals.iptables.clear()

@click.command()
@click.option('--partstr', prompt='Partitions', help='partitions')
def create(partstr):

    all_node_ips = [
        get_node_ip(n)
        for n in filter(lambda c: c.image.tags[0] == GRAFTD_IMAGE, globals.docker_client.containers.list())
    ]

    # partstr = 'node0,node1 node2\n'
    # p = ['node0,node1', 'node2']
    # nodepart = [[<Container, 'node0'>, <Container, 'node1'>], [<Container, 'node2'>]]
    ip_parts = [
        [
            get_node_ip(globals.docker_client.containers.get(name))
            for name in p.split(',')
        ] 
        for p in partstr.strip().split()
    ]
    # click.echo(ip_parts)
    # create chain and add rules
    for idx, ip_part in enumerate(ip_parts, start=1):
        # create chain part#{idx}
        chain_name = f'{PARTITION_CHAIN_PREFIX}{idx}'
        globals.iptables.create_chain(chain_name)
        # all ips in this part jump to this chain
        for ip in ip_part:
            globals.iptables.insert_rule(
                chain=DOCKER_USER_CHAIN,
                src=ip,
                target=chain_name
            )
        # DROP other in this chain
        to_block = list_minus(all_node_ips, ip_part)
        for ip in to_block:
            globals.iptables.insert_rule(
                chain=chain_name,
                dest=ip,
                target="DROP"
            )

partition.add_command(show)
partition.add_command(clear)
partition.add_command(create)