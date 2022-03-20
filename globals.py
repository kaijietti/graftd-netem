import docker
import click
from iptables import IPTables
from config import *

def init():
    # define global vars here
    global docker_client
    docker_client = docker.from_env()
    global iptables
    iptables = IPTables()

    # create graft-net if need
    try:
        docker_client.networks.get(GRAFTD_NETWORK)
    except docker.errors.NotFound:
        ipam_pool = docker.types.IPAMPool(
            subnet='192.168.0.0/16',
            gateway='192.168.0.1'
        )

        ipam_config = docker.types.IPAMConfig(
            pool_configs=[ipam_pool]
        )

        docker_client.networks.create(
            GRAFTD_NETWORK,
            driver="bridge",
            ipam=ipam_config
        )
        click.echo(f"successfully created docker-network:{GRAFTD_NETWORK}")

    # start long lived graftd client
    global graftd_client
    try:
        graftd_client = docker_client.containers.get(GRAFTD_CLIENT_NAME)
    except docker.errors.NotFound:
        graftd_client = docker_client.containers.run(
            GRAFTD_CLIENT_IMAGE,
            detach=True,
            tty=True,
            name=GRAFTD_CLIENT_NAME,
            hostname=GRAFTD_CLIENT_NAME,
            network=GRAFTD_NETWORK,
            remove=True
        )