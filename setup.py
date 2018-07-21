#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
import os
import uuid
import pip
import sys

from setuptools import setup, find_packages
from distutils.version import LooseVersion

if LooseVersion(pip.__version__) >= "10.0.0":
    from pip._internal.req import parse_requirements
else:
    from pip.req import parse_requirements


__dir__ = os.path.abspath(os.path.dirname(__file__))
scripts_path = os.path.join(__dir__, 'scripts')


def get_url(ir):
    if hasattr(ir, 'url'): return ir.url
    if ir.link is None: return
    return ir.link.url


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()


# Requirements list
requirements_path = os.path.join(__dir__, 'py{}-requirements.txt'.format(sys.version_info.major))
if os.path.exists(requirements_path):
    requirements = parse_requirements(requirements_path, session=uuid.uuid1())
    install_requires = [str(ir.req) for ir in requirements if not get_url(ir)]
    dependency_links = [get_url(ir) for ir in requirements if get_url(ir)]
else:
    install_requires = []
    dependency_links = []


setup_requirements = [
    # TODO(Nekmo): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    # TODO: put package test requirements here
]

if os.path.exists(scripts_path):
    scripts_dir_name = scripts_path.replace(__dir__, '', 1)
    scripts_dir_name = scripts_dir_name[1:] if scripts_dir_name.startswith(os.sep) else scripts_dir_name
    scripts = [os.path.join(scripts_dir_name, file) for file in os.listdir(scripts_path) if '.' not in file]
else:
    scripts = []


packages = find_packages(__dir__)
# Prevent include symbolic links
for package in tuple(packages):
    path = os.path.join(__dir__, package.replace('.', '/'))
    if not os.path.exists(path):
        continue
    if not os.path.islink(path):
        continue
    packages.remove(package)


modules = list(filter(lambda x: '.' not in x, packages))

package_version = __import__(modules[0]).__version__


setup(
    name='telegram-upload',
    version=package_version,
    description="Upload large files to Telegram using your account",
    long_description=readme + '\n\n' + history,
    author="Nekmo",
    author_email='contacto@nekmo.com',
    url='https://github.com/Nekmo/telegram_upload',
    packages=find_packages(include=['telegram_upload']),
    # entry_points={
    #     'console_scripts': [
    #         'telegram_upload=telegram_upload.management:main'
    #     ]
    # },
    include_package_data=True,
    install_requires=install_requires,
    dependency_links=dependency_links,
    license="MIT license",
    zip_safe=False,
    keywords='telegram_upload',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
    scripts=scripts,
)
