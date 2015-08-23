# -*- coding: utf-8 -*-
from setuptools import setup

install_requires = ['Flask', 'flask-restless', 'Flask-SQLAlchemy',
                    'click', 'pathlib', 'psycopg2', 'shapely==1.5.9', 'simplejson',
                    'geoalchemy2', 'mzgtfs', 'progress', 'marshmallow']

setup(
    name="gtfsviz",
    version='0.1.0',
    url='http://github.com/quiqua/gtfsviz',
    description='A prototype to visualize and query gtfs data.',
    author='Marcel Radischat',
    author_email='marcel@quiqua.eu',
    packages=['gtfsviz'],
    scripts=['manage.py'],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'gtfsviz-util = manage:cli'
        ]
    },
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)
