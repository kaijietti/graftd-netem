import click
import globals
# refs:
# https://man7.org/linux/man-pages/man8/tc-netem.8.html

# define a group
@click.group()
def netem():
    '''netem show/delay/clear'''
    pass

# tc netem
empty_queue = 'noqueue'
qdisc_show_command = 'tc qdisc show dev eth0'
qdisc_clear_command = 'tc qdisc delete dev eth0 root'

def netem_qdisc_show(node):
    _, output = node.exec_run(qdisc_show_command)
    click.echo(output)

def check_netem_empty(node):
    _, output = node.exec_run(qdisc_show_command)
    if empty_queue in str(output):
        return True
    return False

def add_or_change_netem(node):
    cmd = 'change'
    if check_netem_empty(node):
        cmd = 'add'
    return f"tc qdisc {cmd} dev eth0 root netem"

@click.command()
@click.option('--id', prompt='Node ID', help='ID of Node')
def show(id):
    node = globals.docker_client.containers.get(id)
    _, output = node.exec_run(qdisc_show_command)
    click.echo(output)

@click.command()
@click.option('--id', prompt='Node ID', help='ID of Node')
def clear(id):
    node = globals.docker_client.containers.get(id)
    node.exec_run(qdisc_clear_command)
    netem_qdisc_show(node)

@click.command()
@click.option('--id', prompt='Node ID', help='ID of Node')
@click.option('--time', prompt='Time', help='adds the chosen delay to the packets outgoing to chosen network interface.')
def delay(id, time):
    node = globals.docker_client.containers.get(id)
    node.exec_run(f"{add_or_change_netem(node)} delay {time}ms")
    netem_qdisc_show(node)

@click.command()
@click.option('--id', prompt='Node ID', help='ID of Node')
@click.option('--packets', prompt='Packets', help='maximum number of packets the qdisc may hold queued at a time.')
def limit(id, packets):
    node = globals.docker_client.containers.get(id)
    node.exec_run(f"{add_or_change_netem(node)} limit {packets}")
    netem_qdisc_show(node)

@click.command()
@click.option('--id', prompt='Node ID', help='ID of Node')
@click.option('--percent', prompt='Precent', help='adds an independent loss probability to the packets outgoing from the chosen network interface.')
def loss(id, percent):
    node = globals.docker_client.containers.get(id)
    node.exec_run(f"{add_or_change_netem(node)} loss {percent}")
    netem_qdisc_show(node)

@click.command()
@click.option('--id', prompt='Node ID', help='ID of Node')
@click.option('--percent', prompt='Precent', help='allows the emulation of random noise introducing an error in a random position for a chosen percent of packets.')
def corrupt(id, percent):
    node = globals.docker_client.containers.get(id)
    node.exec_run(f"{add_or_change_netem(node)} corrupt {percent}")
    netem_qdisc_show(node)

@click.command()
@click.option('--id', prompt='Node ID', help='ID of Node')
@click.option('--percent', prompt='Precent', help='using this option the chosen percent of packets is duplicated before queuing them.')
def duplicate(id, percent):
    node = globals.docker_client.containers.get(id)
    node.exec_run(f"{add_or_change_netem(node)} duplicate {percent}")
    netem_qdisc_show(node)

@click.command()
@click.option('--id', prompt='Node ID', help='ID of Node')
@click.option('--percent', prompt='Precent', help='using this option the chosen percent of packets is duplicated before queuing them.')
def reorder(id, percent):
    node = globals.docker_client.containers.get(id)
    code, _ = node.exec_run(f"{add_or_change_netem(node)} reorder {percent}")
    if code == 0:
        # suc
        netem_qdisc_show(node)
    else:
        # fail
        click.echo('reordering not possible without specifying some delay\n')

# qdisc netem
netem.add_command(show)
netem.add_command(clear)
netem.add_command(limit)
netem.add_command(delay)
netem.add_command(loss)
netem.add_command(corrupt)
netem.add_command(duplicate)
netem.add_command(reorder)
