# standard library
import os
import ConfigParser

# 3rd party
import requests
from fabric.api import *
from fabric import colors
import pyrax
import fabtools

# local
import exceptions

def fabfile_root():
    return os.path.dirname(os.path.abspath(__file__))

def project_root():
    return os.path.dirname(fabfile_root())

def remote_project_root():
    return "/vagrant"

def remote_web_root():
    return os.path.join(remote_project_root(), "Web")

def fabfile_templates_root():
    return os.path.join(fabfile_root(), "templates")

def get_config_parser():
    parser = ConfigParser.RawConfigParser()
    parser.read(os.path.join(project_root(), "config.ini"))
    return parser

def set_hosts_from_config():
    parser = get_config_parser()
    env.hosts = parser.get('servers', env.provider).split(",")

def pyrax_login():
    # login https://github.com/rackspace/pyrax/blob/master/docs/pyrax_doc.md
    # https://github.com/rackspace/pyrax/issues/79#issuecomment-18715899
    pyrax.set_setting("identity_type", "rackspace")
    try:
        pyrax.set_credential_file(os.path.join(project_root(), "config.ini"))
    except requests.exceptions.ConnectionError:
        print(colors.red("Make sure you are online to access Rackspace API."))
        raise        

def vagrant_id_filename(server_name, provider):
    return os.path.join(
        project_root(), ".vagrant", "machines", server_name, provider, "id"
    )

def sync_vagrant_rackspace_environment():
    pyrax_login()

    # iterate over all of the cloud servers to identify those that are
    # already running.
    # https://github.com/rackspace/pyrax/blob/master/docs/cloud_servers.md
    cs = pyrax.connect_to_cloudservers(region="ORD")
    for server in cs.servers.list():

        # if the cloud server is already running and managed by
        # vagrant (in env.hosts), then let's make sure the id file is
        # set correctly
        server_configured = False
        filename = vagrant_id_filename(server.name, "rackspace")
        if server.name in env.hosts:
            if os.path.exists(filename):
                with open(filename, 'r') as stream:
                    if server.id == stream.read():
                        server_configured = True
        
        # if the server is not configured on the local machine, just
        # need to create the file with the server.id in it
        if server.name in env.hosts and not server_configured:
            if not os.path.exists(os.path.dirname(filename)):
                local("mkdir -p %s" % os.path.dirname(filename))
            with open(filename, 'w') as stream:
                stream.write(server.id)
