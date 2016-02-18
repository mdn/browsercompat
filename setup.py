#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Python packaging script."""

import os
import sys

import webplatformcompat

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = webplatformcompat.__version__

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    print('You probably want to also tag the version now:')
    print('  git tag -a %s -m "version %s"' % (version, version))
    print('  git push --tags')
    sys.exit()

readme = open('README.rst').read()


setup(
    name='browsercompat',
    version=version,
    description='Browser Compatibility API',
    long_description=readme,
    author='John Whitlock',
    author_email='jwhitlock@mozilla.com',
    url='https://github.com/mdn/browsercompat',
    packages=[
        'webplatformcompat',
    ],
    include_package_data=True,
    install_requires=[
    ],
    test_suite='wpcsite.runtests.runtests',
    license='MPL 2.0',
    zip_safe=False,
    keywords='browsercompat',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
