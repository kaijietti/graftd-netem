import docker
def init():
    # define global vars here
    global docker_client
    docker_client = docker.from_env()
