import sys

from setuptools import setup, find_packages

PACKAGE_NAME= "data_delivery_lambdas"

if sys.version_info < (3, 8): 
    error = "Requires Python 3.12 or higher.... exiting"
    print(error, file=sys.stderr)
    sys.exit(1)

tests_require=[
    "boto3",
    "awswrangler",
    "pytest-cov",
    "pytest-mock",
    "pytest",
    "tox"
]

extras = {
    "test": install_requires + tests_require,
    "dev": setup_requires + install_requires + tests_require,
}
setup(  
    name="data_delivery",
    version="0.1.0",
    packages=find_packages(exclude=["tests*"]),
    package_data={PACKAGE_NAME: ["version"]},
    setup_requires=["setuptools>=42"],
    install_requires=install_requires
    extras_require=extras,
    install_requires=[
        "influxdb_client==1.17.0",
        "urllib3==1.26.6"
    ],
,
)
