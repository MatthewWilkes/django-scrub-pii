# -*- coding: utf-8 -*-

import os

from setuptools import setup
from setuptools import find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

def as_blocktext(text):
    return "::\n\n    " + text.replace("\n", "\n    ")+"\n"

setup(
    name='django-scrub-pii',
    version='1.1.3',
    description='A django add-on that allows models to be decorated with information about which fields contain '
                'sensitive information, and an associated management command that creates a script to remove that'
                ' information.',
    long_description=(read('README.rst') + '\n' +
                      read('HISTORY.rst') + '\n' +
                      as_blocktext(read('LICENSE'))),
    classifiers=[
        "Programming Language :: Python",
    ],
    author='Matthew Wilkes',
    author_email='matt@matthewwilkes.name',
    url='',
    license='BSD',
    packages=find_packages(),
    install_requires=[
        'setuptools',
        'django==1.8',
    ],
    extras_require={
        'test': [
            'nose',
            'nose-selecttests',
            'coverage',
            'unittest2',
            'flake8',
        ],
        'development': [
            'zest.releaser',
            'check-manifest',
        ],
    },
    entry_points="""
    """,
    include_package_data=True,
    zip_safe=False,
)
