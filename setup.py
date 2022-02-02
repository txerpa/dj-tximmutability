#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import os
import re
import sys

from setuptools import find_packages, setup


def get_metadata(package, field):
    """
    Return package data as listed in `__{field}__` in `init.py`.
    """
    init_py = codecs.open(os.path.join(package, '__init__.py'), encoding='utf-8').read()
    match = re.search(
        "^__{}__ = ['\"]([^'\"]+)['\"]".format(field), init_py, re.MULTILINE
    )
    if match:
        return match.group(1)
    raise RuntimeError('Unable to find {} string.'.format(field))


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

version = get_metadata("tximmutability", "version")
author = get_metadata("tximmutability", "author")
email = get_metadata("tximmutability", "email")

if sys.argv[-1] == 'tag':
    print("Tagging the version on git:")
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit()

with open('README.md', 'r') as f:
    readme = f.read()

with open('CHANGELOG.md', 'r') as f:
    history = f.read().replace('.. :changelog:', '')

setup(
    name='dj-tximmutability',
    version=version,
    description='Mutability rules for Django models.',
    long_description=readme,
    long_description_content_type='text/markdown',
    author=author,
    author_email=email,
    url='https://github.com/txerpa/dj-tximmutability',
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    install_requires=["Django>=2.2,<=3.2", "django-model-utils==4.1.1"],
    python_requires=">=3.8",
    license='MIT License',
    zip_safe=False,
    keywords=['django', 'tximmutability', 'immutability', 'mutability'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Framework :: Django :: 3.1',
        'Framework :: Django :: 3.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Utilities',
    ],
)
