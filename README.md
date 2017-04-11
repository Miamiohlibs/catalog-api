Catalog API [![Build Status](https://travis-ci.org/unt-libraries/catalog-api.svg?branch=master)](https://travis-ci.org/unt-libraries/catalog-api)
===========

About
-----

The Catalog API is a Python Django project that provides a customizable REST
API layer for Innovative Interfaces' Sierra ILS. This differs from the built-in
Sierra API in a number of ways, not least of which is that the API design is
fully under your control. In addition to a basic API implementation, a complete
toolkit is provided that allows you to turn any of the data exposed via Sierra
database views (and even data from other sources) into your own API resources.

### Key Features

* All 300+ Sierra database views are modeled using the Django ORM.

* [Django Rest Framework](http://www.django-rest-framework.org/) provides the
API implementation. Serializers and class-based views are easy to extend.

* The API layer has a built-in browseable API view, and content negotiation is
supported. Visit API URLs in a web browser and get nicely formatted, browseable
HTML; request resources in JSON format and get JSON.

* [HAL](http://stateless.co/hal_specification.html), or Hypertext Application
Language (hal+json), is the media type that is used to serve the built-in
resources. "HAL is a simple format that gives a consistent and easy way to
hyperlink between resources in your API." _But_ you are not restricted to using
HAL--you are free to implement the media types and formats that best fit your
use cases.

* The API supports a wide range of query filters, and more are planned: equals,
greater than, less than, in, range, regular expressions, keyword searches,
and more.

* Your API data is completely decoupled from your Sierra data. An extensible
_exporter_ Django app allows you to define custom 
[ETL](https://en.wikipedia.org/wiki/Extract,_transform,_load) processes. Solr
instances that store and index data for the API are included. Or, you can set
up your own data storage and tie your exporters and REST Framework views and
serializers into it.

* Although Sierra data is read-only, the API framework does allow you to
implement POST, PUT, PATCH, and DELETE methods along with GET. So, you can
create your own editable fields on API resources that don't get stored in
Sierra; in fact, you could create resources that merge data from a variety of
sources. Data that isn't sourced from Sierra can be merged when your export
jobs run.

* Accessing API resources _only_ accesses the data in Solr and Redis; it
doesn't hit the Sierra database at all. Thus, API performance is isolated from
performance of your Sierra database, and API usage has no impact on your
Sierra database. You don't have to worry about API users running up against
the concurrent connection limit in Sierra.

* [Celery](http://www.celeryproject.org/) provides an asynchronous task queue
and scheduler. Set up your exporters to run as often as you need so that your
API stays in synch with Sierra as data in Sierra is added, updated, or deleted.

* API resources can be grouped and completely compartmentalized into reusable
Django apps. New apps can expose new resources and/or override the default
base resources. (The _shelflist_ app provides an example of this.)


Requirements
------------
* Python 2 >= 2.7.5, plus pip, virtualenv, and a number of required libraries.
(See the next section for more detail.)
* Java >= 1.7.0_45.
* [Redis](http://redis.io/) >= 2.4.10.
* For development, if you are using the provided sqlite database as the
Django DB, [sqlite3](https://www.sqlite.org) needs to be installed. Otherwise,
be sure to install whatever additional prerequisites are needed for your
database software, such as the mysql-development library and 
[mysqlclient](https://pypi.python.org/pypi/mysqlclient) if you're using MySQL.


Recommended Development Installation and Getting Started
--------------------------------------------------------
This project is currently in production at UNT, but the architecture as it is
in the repository is likely not optimal for production deployment at other
institutions. Cleaning this up to help simplify deployment is on our to-do
list, but, for now, these instructions assume you'll be deploying to a
development environment. Considerations for production deployment are included
where applicable, but of course these will heavily depend on your environment
and needs.

1. **Set up Sierra User(s).**

    The catalog-api requires access to Sierra to export data. You must create
    a new Sierra user for each instance of the project that will be running
    (e.g., for each dev version, for staging, for production). Be sure that
    each user has the _Sierra SQL Access_ application assigned in the Sierra
    admin interface.

    You must also set the Sierra user's `search_path` in PostgreSQL so that
    the user can issue queries without specifying the `sierra_view` prefix.
    Without doing this, the SQL generated by the Django models will not work.

    For each Sierra user you created, log into the database as that user and
    send the following query, replacing `user` with the name of that user:

        ALTER ROLE user SET search_path TO sierra_view;

2. **Install prerequisites.**

    * **Python 2 >= 2.7.5**.

    * **Latest version of pip**. Python >=2.7.9 from [python.org](https://www.python.org)
    includes pip. Otherwise, go
    [here for installation instructions](https://pip.pypa.io/en/stable/installing/).

        Once pip is installed, be sure to update to the latest version:

            pip install -U pip
    
    * **virtualenv**. If you've already installed pip:

            pip install virtualenv
            
        Note: Virtualenv also includes pip, so you could install virtualenv
        first, without using pip.

    * **Requirements for psycopg2**. In order for 
    [psycopg2](http://initd.org/psycopg/) to build correctly, you'll need to
    have the appropriate dev packages installed.

        On Ubuntu/Debian:
    
            sudo apt-get install libpq-dev python-dev

        On Red Hat:

            sudo yum install python-devel postgresql-devel

        On Mac, with homebrew:
            
            brew install postgresql

    * **Java**.

        On Ubuntu/Debian:

            sudo apt-get install openjdk-8-jre

        On Red Hat:
    
            sudo yum install java-1.8.0-openjdk

    * **Redis** is required to serve as a message broker for Celery. It's also
    used to store some application data. You can follow the
    [quickstart guide](http://redis.io/topics/quickstart) to get started, but
    please make sure to set up your `redis.conf` file appropriately.

        Default Redis settings only save your data periodically, so you'll want
        to take a look at
        [how Redis persistence works](http://redis.io/topics/persistence). I'd
        recommend RDB snapshots _and_ AOF persistence, but you'll have to turn
        AOF on in your configuration file by setting `appendonly yes`. Note
        that if you store the `dump.rdb` and/or `appendonly.aof` files anywhere
        in the catalog-api project _and_ you rename them, you'll need to add
        them to `.gitignore`.

        You'll also want to be sure to take a look at the _Securing Redis_
        section in the quickstart guide.

        ***Production Note***: The quickstart section _Installing Redis more
        properly_ contains useful information for deploying Redis in a
        production environment.

    * **Your database of choice to serve as the Django database.** In
    development, [sqlite3](https://www.sqlite.org) works fine. (This is the
    assumed database backend.) You can get precompiled binaries for your OS
    from the [sqlite downloads page](https://www.sqlite.org/download.html).
    Just make sure the command-line shell (sqlite3) goes in a directory that is
    on your PATH.

        ***Production Note***: In production, using sqlite is not recommended.
        Use PostgreSQL or MySQL instead.

3. **Set up a virtual environment.**

    **virtualenv**

    [virtualenv](https://virtualenv.readthedocs.org/en/latest/) is commonly
    used with Python, and especially Django, projects. It allows you to isolate
    the Python environment for projects on the same machine from each other
    (and, importantly, from the system Python). Using virtualenv is not
    strictly required, but it is strongly recommended.

    **(Optional) virtualenvwrapper**

    [virtualenvwrapper](https://virtualenvwrapper.readthedocs.org/en/latest/)
    is very useful if you need to manage several different virtual environments
    for different projects. At minimum, it makes creation, management, and
    activation of virtualenvs easier. The instructions below assume that you
    are not using virtualenvwrapper.

    **Without virtualenvwrapper**

    First generate the virtual environment you're going to use for the
    project. Create a directory where it will live (&lt;DIR&gt;), and then:
    
        virtualenv <DIR>

    This creates a clean copy of whatever Python version you installed
    virtualenv on in that directory.

    Next, activate the new virtual environment.

        source <DIR>/bin/activate

    Once it's activated, any time you run Python, it will use the Python that's
    in the virtual environment. This means any pip installations or other
    modules you install (e.g., via a setup.py file) while this virtualenv is
    active will be stored and used only in this virtual environment. You can
    create multiple virtualenvs on the same machine for different projects in
    order to keep their requirements nicely separated.

    You can deactivate an active virtual environment with:

        deactivate

    You'll probably want to add the `source <DIR>/bin/activate` statement to
    your shell startup script, e.g. such as `~/.bash_profile` and/or `~/.bashrc`
    (if you're using bash), that will activate the appropriate environment on
    startup.

4. **Fork catalog-api on GitHub and clone to your local machine.**

    The catalog-api project is intended to be modified for use at your
    institution, so it's recommended that you fork the repository before
    creating a working copy.

    * Go to [GitHub](https://github.com), and log into your account.
    * Go to the UNT Libraries'
    [catalog-api repository](https://github.com/unt-libraries/catalog-api).
    * Click the Fork button to copy the repository to your local account.

    Now create your working copy (replace [your-github-account] with your
    GitHub account name):

        git clone https://github.com/[your-github-account]/catalog-api.git
    
    Or, if you're authenticating via SSH:
    
        git clone git@github.com:[your-github-account]/catalog-api.git

    If you're new to git and/or GitHub, see the GitHub help pages about
    [how to fork](https://help.github.com/articles/fork-a-repo),
    [how to synch your fork with the original repository](https://help.github.com/articles/syncing-a-fork/),
    [managing branches](https://help.github.com/articles/managing-branches-in-your-repository/),
    and [how to submit pull requests](https://help.github.com/articles/using-pull-requests/)
    (for when you want to contribute back).

    **Aside about Project Structure**

    There are two primary directories in the project root: `django` and `solr`.

    The `django` directory contains the Django project and related
    code, in `django\sierra`. The `manage.py` script for issuing Django
    commands is located here, along with the apps for the project:

    * `api`: Contains the Django REST Framework implementation of the default
    API resources, which include apiusers, bibs, items, eresources,
    itemstatuses, itemtypes, locations, and marc.
    * `base`: Contains the Django ORM models for Sierra.
    * `export`: Contains code for exporters, including definitions of the
    exporters themselves, models related to export jobs, changes to the Django
    admin interface to allow you to manage and track export jobs, and tasks
    for running export jobs through Celery.
    * `sierra`: Contains configuration and settings for the project.
    * `shelflist`: Implements a shelflistitems resource in the API; contains
    overrides for export classes and api classes that implement the resource
    and add links to shelflistitems from item resources and location resources.
    This provides an example of how you could create Django apps with self-
    contained functionality for building new features onto existing API
    resources.

    The `solr` directory contains the included Solr instance and a [fork
    of SolrMarc](https://github.com/sul-dlss/solrmarc-sw) from Naomi Dushay of 
    Stanford University Libraries, which is used for loading MARC data into
    Solr. (See the
    [SolrMarc documentation](https://code.google.com/archive/p/solrmarc/wikis)
    for more information.)

5. **Install all python requirements.**

        pip install -r requirements/requirements-base.txt

6. **Set environment variables.**

    * To `PATH`, add the path to your JRE `/bin` directory and the path to your
    Redis `/src` directory, where the `redis-server` binary lives. 
    Example: `/home/developer/jdk1.7.0_45/bin:/home/developer/redis-2.8.9/src`
    * `JAVA_HOME` -- Should contain the path to your JRE.
    * `REDIS_CONF_PATH` -- Contains the path to the `redis.conf` file you want
    to use for your Redis instance. This is not required, but it's strongly
    recommended. If blank, then when you run Redis with the `start_servers.sh`
    script, Redis will run using the built-in defaults. The main problem with
    this is that the built-in defaults don't provide very good persistence,
    and you will probably lose some data whenever you shut down or restart
    Redis.

    Optional environment variables can be set for development cases where
    multiple instances of the project will run on the same server concurrently.

    * `SOLR_PORT` (Optional) -- Defaults to 8983.
        * If you change this to something other than 8983, you'll have to make
        sure to set a custom SOLRMARC `config.properties` file with a 
        `solr.hosturl` value pointing to the correct port. (This is addressed
        in the next step.)
    * `DJANGO_PORT` (Optional) -- Defaults to 8000.
    * `REDIS_PORT` (Optional) -- Defaults to 6379. If you use a `redis.conf`
    file and specify the port there, `REDIS_PORT` is not needed. If you specify
    both, `REDIS_PORT` will override the port in the configuration file.

    If adding environment variables to your `.bash_profile`, be sure to refresh
    it after you save changes:
    
        . ~/.bash_profile

    If using virtualenvwrapper, environment variables can be set each
    time a virtual environment is activated. See the [virtualenvwrapper
    documentation](https://virtualenvwrapper.readthedocs.org/en/latest/scripts.html#postactivate)
    for more details.

7. **Set local configuration settings.** 

    Django settings for the catalog-api project are in
    `<project_root>/django/sierra/sierra/settings`. Global settings are
    included in the repository in `base.py`, `dev.py`, and `production.py`.
    These attempt to pull local settings from a `settings.json` file that
    is not in the repository--in fact, it's ignored entirely.

    There _is_ a `settings_template.json` file in the repository. This contains
    all of the possible local settings that you may want to set. Some are
    required and some are optional. Some are needed only if you're deploying
    the project in a production environment. Note that many of these are
    things you want to keep secret.

    In order to use the catalog-api, you'll need to create your `settings.json`
    for each environment. Simply copy `settings_template.json` to
    `settings.json` (in the `settings` directory). Fill in the settings that
    are required and any others that are applicable to your environment, and
    then delete the rest. (Non-required settings get a default value specified
    in, e.g., `base.py`.) When you're finished, be sure to delete all comments
    from the file.

    In `settings.json`, you'll find the following:

    * Required Settings -- Your settings file won't load without these.
        * `SECRET_KEY` -- Leave this for now. You'll generate a new secure
        secret key in the next step.
        * `SETTINGS_MODULE` -- The settings module that you want Django to
        use in the current environment, in Python path syntax
        (e.g., sierra.settings.ENVFILE). Unless you create new settings files
        that import from `base.py`, this will either be `sierra.settings.dev`
        or `sierra.settings.production`. See the 
        [Django documentation](https://docs.djangoproject.com/en/1.7/topics/settings/)
        for more information.
        * `SIERRA_DB_USER` -- The username for your Sierra user that has SQL
        access that you set up in step 1.
        * `SIERRA_DB_PASSWORD` -- Password for your Sierra user.
        * `SIERRA_DB_HOST` -- The hostname for your Sierra database server.
        * `LOG_FILE_DIR` -- The full path to the directory where you want
        Django log files stored. You must create this directory if it does
        not already exist; Django won't create it for you, and it will error
        out if it doesn't exist.
        * `MEDIA_ROOT` -- Full path to the directory where downloads and
        user-uploaded files are stored. MARC files that are generated (e.g.,
        to be loaded by SolrMarc) are stored here. Like `LOG_FILE_DIR`, you
        must create this directory if it does not already exist.
    * Optional Settings, Development or Production -- These are settings you
    may need to set in a development or production environment, depending on
    circumstances. Remove the key from the JSON file if you want to use the
    default value.
        * `ADMINS` -- An array of arrays, where each nested array follows the 
        pattern `['name', 'email@email.com']`. These are the people that will
        be emailed if there are errors. Default is an empty array.
        * `EXPORTER_EMAIL_ON_ERROR` -- true or false. If true, the Admins will
        be emailed when an exporter program generates an error. Default is
        `True`.
        * `EXPORTER_EMAIL_ON_WARNING` -- true or false. If true, the Admins
        will be emailed when an exporter program generates a warning. Default
        is `True`.
        * `TIME_ZONE` -- String representing the server timezone. Default is
        `America/Chicago` (central timezone).
        * `CORS_ORIGIN_REGEX_WHITELIST` -- An array containing regular
        expressions that should match URLs for which you want to allow
        cross-domain JavaScript requests to the API. If you're going to have
        JavaScript apps on other servers making Ajax calls to your API, then
        you'll have to whitelist those domains here. Default is an empty array.
        * `SOLRMARC_CONFIG_FILE` -- The name of the file that contains
        configuration settings for SolrMarc for a particular environment. This
        will match up with a `config.properties` file in
        `<project_root>/solr/solrmarc`. (See "SolrMarc Configuration," below,
        for more information.) Default is `dev_config.properties`.
    * Production Settings -- These are settings you'll probably only need to
    set in production. If your development environment is very different than
    the default setup, then you may need to set these there as well.
        * `STATIC_ROOT` -- Full path to the location where static files are
        put when you run the `collectstatic` admin command. Note that you
        generally won't need this in development: when the `DEBUG` setting is
        `True`, then static files are discovered automatically. Otherwise,
        you need to make sure the static files are available via a
        web-accessible URL, which this helps you do. Default is `None`.
        * `SITE_URL_ROOT` -- The URL prefix for the site home. You'll need this
        if your server is set to serve this application in anything but the
        root of the website (like `/catalog/`). Default is `/`.
        * `MEDIA_URL` -- The URL where user-uploaded files can be accessed.
        Default is `/media/`.
        * `STATIC_URL` -- The URL where static files can be accessed. Default
        is `/static/`.
        * `SOLR_HAYSTACK_URL` -- The URL pointing to your Solr instance where
        the `haystack` core can be accessed. Default is
        `http://localhost:{SOLR_PORT}/solr/haystack`.
        * `SOLR_BIBDATA_URL` -- The URL pointing to your Solr instance where
        the `bibdata` core can be accessed. Default is
        `http://localhost:{SOLR_PORT}/solr/bibdata`.
        * `SOLR_MARC_URL` -- The URL pointing to your Solr instance where
        the `marc` core can be accessed. Default is
        `http://localhost:{SOLR_PORT}/solr/marc`.
        * `REDIS_CELERY_URL` -- The URL (using the `redis` protocol rather than
        `http`) pointing the the Redis database you're using as your Celery
        messge broker. Default is `redis://localhost:{REDIS_PORT}/0`.
        * `REDIS_APPDATA_HOST` -- The hostname for the Redis instance you're
        using to store application data. It's strongly recommended that you use
        a different port or database for app data than you use for your Celery
        message broker. Default is `localhost`.
        * `REDIS_APPDATA_PORT` -- The port for the Redis instance you're using
        to store app data. Default is your `REDIS_PORT` value.
        * `REDIS_APPDATA_DATABASE` -- The number of the Redis database you're
        using to store app data. Default is `1`.
        * `ADMIN_ACCESS` -- true or false. Default is `True`, but you can set
        to `False` if you want to disable the Django Admin interface for
        a particular catalog-api instance.
        * `ALLOWED_HOSTS` -- An array of hostnames that represent the domain
        names that this Django instance can serve. This is a security measure
        that is required to be set in production. Defaults to an empty
        array.
        * `EXPORTER_AUTOMATED_USERNAME` -- The name of the Django user that
        should be tied to scheduled (automated) export jobs. Make sure that the
        Django user actually exists (if it doesn't, create it). It can be
        helpful to have a unique Django user tied to automated exports so that
        you can more easily differentiate between scheduled exports and
        manually-run exports in the admin export interface. Defaults to
        `django_admin`.
        * `DEFAULT_DATABASE` -- Specifies the setup for the default Django
        database. (Note that is different than your Sierra database.) The
        default setup is to create a sqlite database file called
        `django_sierra` in the project directory. Set up the ENGINE, NAME,
        USER, PASSWORD, and HOST keys if you want to use a different database.

    **SolrMarc Configuration**

    SolrMarc is used to index bib records in Solr. The SolrMarc code is located
    in `<project_root>/solr/solrmarc/`.

    Files that control SolrMarc configuration include the following.

    * `*_config.properties` -- Contains settings for SolrMarc. There are two
    settings here that are of immediate concern.
        * `solr.hosturl` -- Should contain the URL for the Solr index that
        SolrMarc loads into.
        * `solrmarc.indexing.properties` -- Points to the `*_index.properties`
        file used by your SolrMarc instance, described below.
    * `*_index.properties` -- Defines how MARC fields translate to fields in
    your Solr index. You'll change this file if/when you want to change how
    bib API resources are created.

    If you've set a `SOLR_PORT` other than the default (8983), then you
    must make a change to the SolrMarc `config.properties`. Create a copy of
    `<project_root>/solr/solrmarc/dev_config.properties`.
    In the copy, change the port of the `solr.hosturl` value to match the
    correct port. Or, if you're using your own Solr instance, change the
    URL to point to that instead.

    In your `settings.json` file, set the `SOLRMARC_CONFIG_FILE` setting to
    the filename of the `config.properties` file you just created.
    
    ***Production Note***: You'll likely want to keep the URL for your
    production Solr instance out of GitHub. The `production_config.properties`
    file is in `.gitignore` for that reason. There is a
    `production_config.properties.template` file that you can copy over to
    `production_config.properties` and fill in the `solr.hosturl` value.

8. **Generate a new secret key for Django.**

        cd <project_root>/django/sierra
        manage.py generate_secret_key

    Copy/paste the new secret key into `SECRET_KEY` in `settings.json`.

9. **Run migrations and install fixtures.**

        cd <project_root>/django/sierra
        manage.py migrate
        manage.py loaddata export/fixtures/starting_metadata.json

    This creates the default Django database and populates certain tables with
    needed data. If you haven't overridden the default database setup in your
    `settings.json` file, then it will create a sqlite database named
    `django_sierra` in the `<project_root>/django/sierra` directory. This 
    filename is in `.gitignore`. If you set a different database name and store
    it anywhere within the project, be sure to add the filename to
    `.gitignore.`

10. **Create a superuser account for Django.**

        cd <project_root>/django/sierra
        manage.py createsuperuser

    Run through the interactive setup. Remember your username and password, as
    you'll use this to log into the Django admin screen for the first time.
    (You can create additional users from there.)

11. **(Optional) Run Sierra database tests.**
    
        cd <project_root>/django/sierra
        manage.py test base

    This runs a series of tests over each of the ORM models for Sierra to
    ensure that the models match the structures in the database. You should run
    this when you first install the catalog-api to ensure the models match your
    Sierra setup--systems may differ from institution to institution based on
    what products you have.

    Note: If any `*_maps_to_database` tests fail, it indicates that there are
    fields on the model that aren't present in the database. These are more
    serious (but often easier to fix) than `*_sanity_check` tests, which test
    to ensure that relationship fields work properly. In either case, you can
    check the models against the SierraDNA documentation and your own database
    to see where the problems lie and decide if they're worth trying to fix in
    the models. If tests fail on models that are central, like `RecordMetadata`
    or `BibRecord`, then it's a problem. If tests fail on models that are more
    peripheral, like `LocationChange`, then finding and fixing those problems
    may be less of a priority, especially if you never intend to use those
    models in your API.

    Presumably because the Sierra data that customers have access to is
    implemented in views instead of tables, proper data integrity is lacking in
    a few cases. (E.g., the views sometimes don't implement proper primary key
    / foreign key relationships.) This can cause `*_sanity_check` tests to fail
    in practice on live data when they should work in theory.

12. **Start servers and processes: Solr, Redis, Django Development Web Server,
and Celery.**

    In the root of the repository a few bash scripts are included that let
    you start and stop servers quickly and easily in the default development
    environment. But the first time you install the project, you may want to
    try starting the servers manually so you can test individually and make
    sure they work.

    * **Solr**

            cd <project_root>/solr/instances
            java -jar start.jar -Djetty.port=$SOLR_PORT -Dlog4j.configuration=file:resources/console_log4j.properties
        
        (If you didn't set the `$SOLR_PORT` environment variable, you can leave
        out `-Djetty.port=$SOLR_PORT`, and it will run on the default port,
        8983.)

        This will start Solr, using a logging configuration file that outputs
        to the console. (The default logging configuration will output to a
        file in `<catalog_api_root>/solr/instances/logs`.) You should see a
        bunch of INFO logs scroll by for a second or two.

        Try going to `http://localhost:SOLR_PORT/solr/` in a Web browser.
        (Replace `SOLR_PORT` with the value of the `SOLR_PORT` environment
        variable, and, if testing from an external machine, replace `localhost`
        with your hostname.) You should see an Apache Solr admin screen.

        You can stop Solr with CTRL-C in the terminal where it's running in the
        foreground. For now, just leave it up.

    * **Redis**

        Open a new terminal to test Redis.

            cd <project_root>
            redis-server $REDIS_CONF_PATH --port $REDIS_PORT
        
        (Use whichever environment variables you actually have set.
        Minimally, you can run `redis-server` and it will run using the
        default configuration on port 6379.)

        If you followed the Redis quick-install guide, then you've probably
        already tested this. But, we want Redis running when we test Celery,
        so leave it up for the moment.

    * **Django Development Web Server**

        Open another terminal to test Django.

            cd <project_root>/django/sierra
            manage.py runserver 0.0.0.0:$DJANGO_PORT
        
        (In this case, if you didn't set the `$DJANGO_PORT` environment
        variable, replace `$DJANGO_PORT` with `8000`.)

        If all goes well, you should see something like this:

            System check identified no issues (0 silenced).

            February 10, 2016 - 11:40:40
            Django version 1.7, using settings 'sierra.settings.my_dev'
            Starting development server at http://0.0.0.0:8000/
            Quit the server with CONTROL-C.

        Try going to `http://localhost:DJANGO_PORT/api/v1/` in a browser.
        (Replace `localhost` with your hostname if accessing from an external
        computer, and replace `DJANGO_PORT` with your `DJANGO_PORT` value.)
        You should see a DJANGO REST Framework page displaying the API Root.

        ***Production Note***: The Django Development Web Server is intended
        to be used only in development environments. Never ever use it in
        production! Configuring Django to work with a real web server like
        Apache is a necessary step when moving into production. See the
        [Django documentation](https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/modwsgi/)
        for more details.

    * **Celery**

        Open up another terminal to test Celery.

            cd <project_root>/django/sierra
            celery -A sierra worker -l info -c 4

        You'll get some INFO logs, as well as a UserWarning about not using
        the DEBUG setting in a production environment. Since this is
        development, it's nothing to worry about. You should get a final log
        entry with `celery@hostname ready`.

    * **Celery Beat**

        Celery Beat is the task scheduler that's built into Celery. It's what
        lets you schedule your export jobs to run at certain times. You
        generally won't have Celery Beat running in a development environment,
        so for now we just want to test to make sure it will start up.

        With Celery still running, open another terminal.

            cd <project_root>/django/sierra
            celery -A sierra beat -S djcelery.schedulers.DatabaseScheduler

        You should see a brief summary of your Celery configuration, and then
        a couple of INFO log entries showing that Celery Beat has started.

        ***Production Note***: See the 
        [Celery documentation](http://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html)
        for how to set up periodic tasks. In our production environment, we use
        the DatabaseScheduler and store periodic-task definitions in the Django
        database. These are then editable in the Django Admin interface.

    Once you've confirmed each of the above processes runs, then you can
    stop them. (Ctrl-C in each of the running terminals.) From now
    on, you can just start/stop them from the provided shell scripts.

    **Convenience Scripts**

    * `start_servers.sh` -- Starts Solr, Redis, and Django on the ports you've
    specified in your environment variables as background processes.
    Optionally, you can issue an argument, `django` or `solr` or `redis`, to
    run one of those as a foreground process (and direct output for that
    process to stdout). Often, in development, `start_servers.sh django` can be
    useful so that you get Django web server logs output to the console. Solr
    output and Redis output are often not as immediately useful. Solr output
    will still be logged to a file in `<project_root>/solr/instances/logs`, and
    Redis output will be logged based on how you've configured your Redis
    instance.

    * `stop_servers.sh` -- Stops Solr, Redis, and Django (if they're currently
    running).

    * `start_celery.sh` -- Starts Celery as a foreground process. Often, in
    development, you'll want Celery logged to the console so you can keep an
    eye on output. (Use CTRL-C to stop Celery.)

    ***Production Notes*: Daemonizing Processes for a Production Environment**

    In a production environment, you'll want to have all of these servers
    and processes daemonized using init.d scripts.

    * Redis ships with usable init scripts. See the
    [quickstart guide](http://redis.io/topics/quickstart) for more info.

    * For both Celery and Celery Beat, there are example init
    scripts available, although you'll have to edit some variables.
    See the
    [Celery documentation](http://docs.celeryproject.org/en/latest/tutorials/daemonizing.html)
    for details.

    * For Solr, you'll need to create your init.d file yourself, but there
    are a number of tutorials available on the Web. The Solr instance
    provided with this project uses a straightforward multi-core setup,
    so the init.d file should be straightforward.

13. **Test record exports.**

    If everything up to this point has worked, then let's try triggering a few
    record exports and then making sure data shows up in the API.

    * Start up your servers and Celery.

    * Go to `http://localhost:DJANGO_PORT/admin/export/` in a web browser
    (using the appropriate hostname and port).

    * Log in using the superuser username and password you set up in step 10.

    * Under the heading **Manage Export Jobs**, click _Trigger New Export_.

    * First thing we want to do is export administrative metadata (like 
    Location codes, ITYPEs, and Item Statuses).

        * _Run this Export_: "Load ALL III administrative metadata-type data
        into Solr."
        * _Filter Data By_: "None (Full Export)"
        * Click Go.
        * You'll see some activity in the Celery log, and the export should be
        done within a second or two. Refresh your browser and you should
        see a Status of _Successful_.

    * Next, try exporting one or a few bib records and any attached items.
        
        * _Run this Export_: "Load bibs and attached records into Solr."
        * _Filter Data By_: "Record Range (by record number)."
        * Enter a small range of bib record IDs in the _From_ and _to_ fields.
        Be sure to omit the dot and check digit. E.g., from b4371440 to 
        b4371450.
        * Click Go.
        * You'll see activity in the Celery log, and the export should complete
        within a couple of seconds. Refresh your browser and you should see a
        status of _Successful_.

    * Finally, try viewing the data you exported in the API.

        * Go to `http://localhost:DJANGO_PORT/api/v1/` in your browser.
        * Click the URL for the `bibs` resource, and make sure you see data
        for the bib records you loaded.
        * Navigate the various related resources in `_links`, such as `marc`
        and `items`. Anything that's linked should take you to the data for
        that resource.


Running Tests
-------------

In addition to the production Sierra database tests described above, there are
other tests you can run using pytest. For the current build, running them
requires a little bit of extra setup. In the future we'll be moving to a
Docker-based workflow to eliminate these steps. And, in the future, we'll fold
the production Sierra database tests into the pytest tests.

1. **Set up PostgreSQL** -- You'll need to have a PostgreSQL server running
    locally that the Sierra test database can be built on, and you'll need a
    user that can create databases on that server.

    * Spin up `postgres` locally.

    * Connect to your local `postgres` database.

            sudo -u postgres psql postgres

    * Create your user.

            postgres=# CREATE USER <user> PASSWORD '<password>';

    * Give that user permission to create databases.

            postgres=# ALTER USER <user> CREATEDB;

2. **Set up additional test settings** -- Add the following to your
    `settings.json` file:

    * `TEST_SIERRA_DB_USER` -- The username you set up in the previous step for
        your local PostgreSQL instance.

    * `TEST_SIERRA_DB_PASSWORD` -- The password for the user you set up in the
        previous step.

    * `TEST_SIERRA_DB_HOST` -- The host for your local PostgreSQL instance.

3. **Install additional python packages needed for tests.**

        cd <project_root>
        pip install -r requirements/requirements-tests.txt

4. **Run tests.** 

        cd <project_root>
        py.test

A few notes about tests:

* Your postgres server needs to be running when you run tests.

* Our `pytest.ini` file specifies the `--reuse-db` option, so the Sierra
test database does not get dropped after tests are run. This saves some
setup time when you run tests, but it also means the test database will
persist locally. You can force the test database to be rebuilt using
`py.test --create-db`.

* `settings.sierra.test` Django settings are used when tests are run. This is
defined in `pytest.ini`, and this is where the configuration for the test
databases lives, if you're curious.


License
-------

See LICENSE.txt.


Contributors
------------

* [Jason Thomale](https://github.com/jthomale)
* [Jason Ellis](https://github.com/jason-ellis)
