import docker
from iptables import IPTables
from config import *

def init():
    # define global vars here
    global docker_client
    docker_client = docker.from_env()
    global iptables
    iptables = IPTables()
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