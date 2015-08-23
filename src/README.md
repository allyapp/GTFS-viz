# Instructions

### Installation

In order to run the application, PostGIS and virtualenv (Python) must be installed.

If you are on OS X, use homebrew to install it.

```
$ pip install virtualenv
$ brew install postgres postgis
```

Create a database user and choose a password, for example `gtfs`:

```
$ createuser -PEs gtfs
```

Create a database with postgis enabled. First create a template, then connect to the template and create the postgis extensions and alter the permissions.

```
$ createdb template_postgis -T template0
$ psql -D template_postgis
template_postgis# create extension postgis;
template_postgis# GRANT ALL ON geometry_columns TO PUBLIC;
template_postgis# GRANT ALL ON spatial_ref_sys TO PUBLIC;
template_postgis=# GRANT ALL ON geography_columns TO PUBLIC;
template_postgis=# \q
$ createdb gtfs -O gtfs -T template_postgis
```

Now grab the repository with the code and put it somewhere:

```
$ cd /path/to/sandbox
$ git clone https://github.com/quiquaTMP/GTFS-viz.git
```

Create a virtualenv for python:

```
$ virtualenv env/gtfs
$ source env/gtfs/bin/activate
```

Install the required python libraries. 
You need to use this repository first, because of some
changes made to `flask-restless`, which are not in the released version of it.
(I forked it to my account to keep it around).

```
(gtfs) $ pip install git+https://github.com/quiqua/flask-restless.git#flask-restless
```

Afterwards, install the application:

```
(gtfs) $ pip install -e gtfs-viz/src/.
```

If everything went well, reactivate your virtualenv to have access to the supplied executable.

```
(gtfs) $ deactivate
(gtfs) $ source env/gtfs/bin/activate
```

### Running the application

In order to run the application, you need to do the following (if not already done):

```
$ cd path/to/sandbox
$ source env/gtfs/bin/activate
```

Now open the `config.py` and edit the Postgres connection string to match your setup:

```
$ vi gtfs-viz/src/gtfsviz/config.py
```

Save the changes.

You can now create the tables needed for running the application:

```
(gtfs) $ gtfsviz-util create_db
```

Feed the database with your GTFS data:

```
(gtfs) $ gtfsviz-util feed --path path/to/dataset
```

It could take a moment, depending on the dataset.

If no errors occured, you can now start the webserver:

```
(gtfs) $ gtfsviz-util runserver
```

Now open up <http://127.0.0.1:5000/> and make some
queries :)