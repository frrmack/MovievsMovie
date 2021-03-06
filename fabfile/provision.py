"""
Functions for provisioning environments with fabtools (eat shit puppet!)
"""
# standard library
import sys
import copy
import os
from distutils.util import strtobool

# 3rd party
import fabric
from fabric.api import env, task, local, run, settings, cd, sudo, lcd
import fabtools
from fabtools.vagrant import vagrant_settings

# local
import decorators
import utils

@task
@decorators.needs_environment
def apt_get_update(max_age=86400*7):
    """refresh apt-get index if its more than max_age out of date
    """
    with vagrant_settings(env.host_string):
        try:
            fabtools.require.deb.uptodate_index(max_age=max_age)
        except AttributeError:
            msg = (
                "Looks like your fabtools is out of date. "
                "Try updating fabtools first:\n"
                "    sudo pip install fabtools==0.17.0"
            )
            raise Exception(msg)

@task
@decorators.needs_environment
def users():
    """create users"""
    with vagrant_settings(env.host_string):
        fabtools.require.user('guest', password="tiyp,guest")

@task
@decorators.needs_environment
def python_packages():
    """install python packages"""
    filename = os.path.join(utils.remote_project_root(), "REQUIREMENTS")
    with vagrant_settings(env.host_string):
        fabtools.require.python.requirements(filename, use_sudo=True)


@task
@decorators.needs_environment
def download_text_corpora():
    """install NLTK corpora"""
    with vagrant_settings(env.host_string):
        run('curl https://raw.github.com/sloria/TextBlob/master/download_corpora.py | python')

@task
@decorators.needs_environment
def debian_packages():
    """install debian packages"""
    
    # get the list of packages
    filename = os.path.join(utils.project_root(), "REQUIREMENTS-DEB")
    with open(filename, 'r') as stream:
        packages = stream.read().strip().splitlines()

    # install them all with fabtools.
    with vagrant_settings(env.host_string):
        fabtools.require.deb.packages(packages)

@task
@decorators.needs_environment
def setup_django(do_rsync=True):
    """setup django"""

    # http://stackoverflow.com/a/19536667/564709
    if isinstance(do_rsync, (str, unicode,)):
        do_rsync = bool(strtobool(do_rsync))
        
    with vagrant_settings(env.host_string):

        # open up and listen to port 8000
        sudo("iptables -A INPUT -p tcp --dport 8000 -j ACCEPT")

        # extract necessary configuration variables from INI file
        parser = utils.get_config_parser()
        mysql_root_password = parser.get('mysql', 'root_password')
        django_username = parser.get('mysql', 'django_root_username')
        django_password = parser.get('mysql', 'django_root_password')
        django_db = parser.get('mysql', 'django_database')

        # setup mysql
        fabtools.require.mysql.server(password=mysql_root_password)
        with settings(mysql_user='root', mysql_password=mysql_root_password):
            fabtools.require.mysql.user(django_username, django_password)
            fabtools.require.mysql.database(django_db,owner=django_username)


        # collect the static files
        with cd("/vagrant/Web"):
            run("./manage.py collectstatic --noinput")

        # rsync directory to get all models, views, etc into the
        # /srv/www directory.
        #
        # TODO: Use a soft link to the figures/templates directory to
        # avoid unnecessary rsyncing of data from analysis?
        site_name = "movievsmovie.datasco.pe"
        web_dir = "Web"
        site_root = os.path.join("/srv", "www", site_name, web_dir)
        fabtools.require.directory(site_root, owner="www-data", use_sudo=True)
        if do_rsync:
            sudo("rsync -avC --exclude='*.hg' /vagrant/%s %s" % (
                web_dir, os.path.dirname(site_root)
            ))

        # write the local django settings. since local.py is listed in
        # the .hgignore, the -C option to rsync must ignore it. this
        # needs to go AFTER rsyncing
        for root_dir in ["/vagrant/" + web_dir, site_root]:
            # make sure the dir exists (for the site_root one)
            target_dir = root_dir+"/Web/settings/"
            fabtools.require.directory(target_dir, owner="www-data", use_sudo=True)
            # use_sudo is necessary (for the site_root one)
            fabtools.require.files.template_file(
                path=root_dir+"/Web/settings/local.py",
                template_source=os.path.join(
                    utils.fabfile_templates_root(), "django_settings.py"
                ),
                context={
                    "django_db": django_db,
                    "django_username": django_username,
                    "django_password": django_password,
                },
                use_sudo=True,
            )

        # make sure permissions are set up properly
        #sudo("chmod -R a+w %s" % site_root)
        sudo("chmod -R g+w %s" % site_root)
        sudo("chgrp -R www-data %s" % site_root)
            
        # make sure database is up and running
        with cd("/vagrant/Web"):
            run("./manage.py syncdb --noinput")
            run("./manage.py migrate")


        # setup apache
        # fabtools.require.apache.module_enabled("mod_wsgi") # __future__
        config_filename = os.path.join(
            utils.fabfile_templates_root(), 
            "apache.conf",
        )
        fabtools.require.apache.site(
            'movie.vs.movie.datasco.pe',
            template_source=config_filename,
            wsgi_application_group=r"%{GLOBAL}",
            site_name=site_name,
            site_root=site_root,
        )
        fabtools.require.apache.disabled('default')




@task
@decorators.needs_environment
def setup_analysis():
    """prepare analysis environment"""
    with vagrant_settings(env.host_string):
        
        # write a analysis.ini file that has the provider so we can
        # easily distinguish between development and production
        # environments when we run our analysis
        template = os.path.join(
            utils.fabfile_templates_root(), 
            "server_config.ini",
        )
        fabtools.require.files.template_file(
            path="/vagrant/server_config.ini",
            template_source=template,
            context=env,
        )


@task
@decorators.needs_environment
def load_popular_movies():
    """populate the database with movies to rate"""
    with vagrant_settings(env.host_string):
        
        # scrape the top 1000 popular movies from imdb
        # this will make sure that the Rate Movies view
        # has all the stuff it needs.
        # you only need to do this once, so do it if
        # shawshank isn't in there
        stampfile = "/vagrant/data/.popular_movie_download_complete"
        if not fabtools.files.is_file( stampfile ):
            with cd("/vagrant/Web"):
                run("./manage.py put_movies_in_with_popularity_rank ../data/popular_movies_1000.txt")
                run("touch %s" % stampfile)

@task(default=True)
@decorators.needs_environment
def default(do_rsync=True):
    """run all provisioning tasks"""
    # http://stackoverflow.com/a/19536667/564709
    if isinstance(do_rsync, (str, unicode,)):
        do_rsync = bool(strtobool(do_rsync))

    # rsync files (Vagrant isn't doing any provisioning now)
    if do_rsync:
        local("vagrant provision %(host_string)s" % env)

    # run all of these provisioning tasks in the order specified here
    apt_get_update()
    users()

    # install debian packages first to make sure any compiling python
    # packages have necessary dependencies
    debian_packages()
    python_packages()
    #download_text_corpora()

    setup_django(do_rsync=do_rsync)
    setup_analysis()

    # if this is the first time setting up,
    # populate the db with some popular movies
    # to have something available to rate
    load_popular_movies()


