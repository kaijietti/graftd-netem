from setuptools import setup

setup(
    name='graft-netem',
    version='0.1.0',
    py_modules=['graftd_netem'],
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'graftd_netem = graftd_netem:cli',
        ],
    },
)