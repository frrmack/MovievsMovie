# standard library
import os

# 3rd party
from fabric.api import env, task, local, run, settings, runs_once, execute, roles, hide
from fabric import colors
from fabric.contrib.files import upload_template

# local
import utils
import decorators

@task
@decorators.needs_environment
def up():

    # bring up ze box
    local((
        "vagrant up "
        "--provider=%(provider)s "
        "--no-provision "
        "%(host_string)s "
    ) % env)

    # friendly reminder to provision account
    print(colors.green((
        "server '%(host_string)s' launched! "
        "remember to provision when all servers are launched"
    )) % env)

@task
@decorators.needs_environment
def destroy():
    local('vagrant destroy -f %(host_string)s' % env)
