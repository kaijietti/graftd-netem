import click
import globals

# define a group
@click.group()
def netem():
    '''netem show/delay/clear'''
    pass

# tc netem
empty_queue = 'noqueue'
qdisc_show_command = 'tc qdisc show dev eth0'
qdisc_clear_command = 'tc qdisc delete dev eth0 root'

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
@click.option('--time', prompt='Time', help='time in ms')
def delay(id, time):
    node = globals.docker_client.containers.get(id)
    node.exec_run(f"{add_or_change_netem(node)} delay {time}ms")

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


# qdisc netem
netem.add_command(show)
netem.add_command(clear)
netem.add_command(delay)
