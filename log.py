import click
import globals
import docker
from config import *

# define a group
@click.group()
def log():
    '''log start/stop'''
    pass

@click.command()
def start():
    # start vizor
    vizor = globals.docker_client.containers.run(
        VIZOR_IMAGE,
        command="/vizor",
        detach=True,
        remove=True,
        name=VIZOR_IMAGE,
        hostname=VIZOR_IMAGE,
        ports={'8090/tcp': 8090}
    )
    click.echo("successfully started vizor")

    # connect
    globals.docker_client.networks.get(GRAFTD_NETWORK).connect(vizor)
    click.echo(f"successfully connected vizor to docker-network:{GRAFTD_NETWORK}")


    # start logstash-http
    globals.docker_client.containers.run(
        LOGSTASH_IMAGE,
        detach=True,
        name=LOGSTASH_IMAGE,
        hostname=LOGSTASH_IMAGE,
        network=GRAFTD_NETWORK,
        publish_all_ports=True,
        remove=True
    )
    click.echo("successfully started logstash-http")

    # start log-pilot
    globals.docker_client.containers.run(
        LOGPILOT_IMAGE,
        detach=True,
        cap_add=['SYS_ADMIN'],
        volumes=[
            "/var/run/docker.sock:/var/run/docker.sock",
            "/etc/localtime:/etc/localtime",
            "/:/host:ro"
        ],
        environment=["LOGGING_OUTPUT=logstash", f"LOGSTASH_HOST={LOGSTASH_IMAGE}", "LOGSTASH_PORT=5044"],
        name=LOGPILOT_NAME,
        hostname=LOGPILOT_NAME,
        network=GRAFTD_NETWORK,
        publish_all_ports=True,
        remove=True
    )
    click.echo("successfully started log-pilot")

def stop_log():
    try:
        globals.docker_client.containers.get(LOGPILOT_NAME).stop()
        click.echo("successfully stopped log-pilot")
    except docker.errors.NotFound as e:
        click.echo(e)

    try:
        globals.docker_client.containers.get(LOGSTASH_IMAGE).remove(force=True)
        click.echo("successfully stopped logstash-http")
    except docker.errors.NotFound as e:
        click.echo(e)

    try:
        globals.docker_client.containers.get(VIZOR_IMAGE).stop()
        click.echo("successfully stopped vizor")
    except docker.errors.NotFound as e:
        click.echo(e)

@click.command()
def stop():
    return stop_log()


log.add_command(start)
log.add_command(stop)