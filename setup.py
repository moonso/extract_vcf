# -*- coding: utf-8 -*-
from __future__ import absolute_import
from setuptools import setup, find_packages


setup(
  name='extract_vcf',
  version='0.3',
  url='https://github.com/moonso/extract_vcf',
  description='Tool to extract information from vcf file.',
  author='Måns Magnusson',
  author_email='mans.magnusson@scilifelab.se',
  license = 'MIT License',
  packages=find_packages(exclude=[
                                  'tests/',
                                  'scripts/'
                                  ]
                        ),
  include_package_data=True,
  zip_safe=False,
  install_requires=[
  ],
  scripts=[
  ],
  # test_suite='tests',
  classifiers=[
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries'
  ]
)
