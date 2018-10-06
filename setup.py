import os
import imp
import multiprocessing
from setuptools import setup, find_packages

addon = imp.load_source('config', 'config.py')
pkg = addon.FULL_ADDON_NAME
version = imp.load_source('version', os.path.join(pkg, 'version.py'))


def fpath(name):
    return os.path.join(os.path.dirname(__file__), name)


def read(fname):
    return open(fpath(fname)).read()


def desc():
    return read('README.md')


setup(
    name=pkg,
    version=version.VERSION_STRING,
    url='https://github.com/dolfandringa/fab_addon_geoalchemy/',
    license='MIT',
    author=version.AUTHOR_NAME,
    author_email=version.AUTHOR_EMAIL,
    description=version.DESCRIPTION,
    long_description=desc(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    package_data={'': ['LICENSE', 'config.py', 'README.md']},
    zip_safe=False,
    platforms='any',
    dependency_links=[
        'http://github.com/dolfandringa/Flask-AppBuilder/tarball/develop#egg=Flask-AppBuilder-1.13.0'
    ],
    install_requires=[
        'Flask-AppBuilder>=1.13.0',
        'shapely',
        'sqlalchemy',
        'psycopg2',
        'GeoAlchemy2'
    ],
    setup_requires=['pytest-runner'],
    tests_require=[
        'pytest',
        'pytest-cov',
        'coverage'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    test_suite='pytest'
)
