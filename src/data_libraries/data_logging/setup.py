import sys

from setuptools import setup, find_packages

PACKAGE_NAME = "data_logging"

if sys.version_info < (3, 8):
    print(
        "Python 3.8 or higher is required to run this package... exiting",
        file=sys.stderr,
    )
    sys.exit(1)

print("Number of arguments", sys.argv, "arguments.")

setup_requires = [
    "glue-setuptools",
    "pytest-runner",
    "setuptools-lint",
    "wheel",
]


install_requires = []

tests_require = [
    "pytest",
    "pytest-cov",
    "pytest-env",
    "pytest-html",
    "pytest-pythonpath",
    "tox",
]

extras = {
    "test": install_requires + tests_require,
    "dev": install_requires + tests_require + setup_requires,
}

setup(
    name=f"myapp-{PACKAGE_NAME}",
    version="1",
    description="Data Logging Library",
    author="CursorAI",
    author_email="",
    url="",
    packages=find_packages(exclude=["tests*"]),
    package_data={PACKAGE_NAME: ["version"]},
    py_modules=["setup"],
    license="MIT",
    setup_requires=setup_requires,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
        "test": [str(req) for req in extras["test"]],
        "dev": [str(req) for req in extras["dev"]],
    },
)
