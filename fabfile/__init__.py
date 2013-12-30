# 3rd party
from fabric.api import env, task

# local
import utils
import vagrant
import provision
#import data

@task
def movdev():
    """define development server"""
    env.provider = "virtualbox"
    utils.set_hosts_from_config()

@task
def moviefight():
    """define rackspace server"""
    env.provider = "rackspace"
    utils.set_hosts_from_config()

    # If these servers have already been launched on rackspace (say,
    # by someone else) but the ids are not stored locally on this
    # machine, we need to create the id files in the .vagrant/
    # directory.
    utils.sync_vagrant_rackspace_environment()
