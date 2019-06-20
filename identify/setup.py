import subprocess

from setuptools import (
    find_packages,
    setup,
    Command,
)

PACKAGE_NAME = 'identify'


class SimpleCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


class TestCommand(SimpleCommand):
    def run(self):
        subprocess.run(['mypy', PACKAGE_NAME])
        subprocess.run(['flake8'])
        subprocess.run(['tox'])


setup(
    name=PACKAGE_NAME,
    description='Identify your personality through your social network.',
    packages=find_packages(),
    install_requires=[
        'pandas==0.24.*',
    ],
    extras_require=dict(
        dev=[
            'black==19.*',
            'flake8==3.7.*',
            'isort==4.3.*',
            'mypy==0.701.*',
            'pytest==4.5.*',
            'pytest-cov==2.7.*',
            'pytest-mock==1.10.*',
            'pytest-xdist==1.28.*',
            'tox==3.12.*',
        ],
    ),
    cmdclass=dict(
        test=TestCommand,
    ),
)
