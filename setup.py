#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

CURRENT_PYTHON = sys.version_info[:2]


def get_version(*file_paths):
    """Retrieves the version from tximmutability/__init__.py"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M
    )
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


version = get_version("tximmutability", "__init__.py")

if sys.argv[-1] == 'publish':
    try:
        import wheel

        print("Wheel version: ", wheel.__version__)
    except ImportError:
        print('Wheel library missing. Please run "pip install wheel"')
        sys.exit()
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

if sys.argv[-1] == 'tag':
    print("Tagging the version on git:")
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit()

with open('README.rst', 'r') as f:
    readme = f.read()
# readme = open('README.rst').read()
with open('HISTORY.rst', 'r') as f:
    history = f.read().replace('.. :changelog:', '')
# history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='dj-tximmutability',
    version=version,
    description='Mutability rules for Django models.',
    long_description=readme + '\n\n' + history,
    author='Marija Milicevic',
    author_email='marija.milicevic@txerpa.com',
    url='https://github.com/marija_milicevic/dj-tximmutability',
    packages=[
        'tximmutability',
    ],
    include_package_data=True,
    install_requires=["django>=2.2,<=3", "django-model-utils==4.1.1"],
    python_requires=">=3.5",
    license="BSD",
    zip_safe=False,
    keywords=['django', 'tximmutability', 'immutability', 'mutability'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
