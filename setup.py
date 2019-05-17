#!/usr/bin/env python
# from os.path import basename
# from os.path import glob
# from os.path import splitext
import os
import sys

import setuptools


os.chdir(os.path.dirname(sys.argv[0]) or ".")


VERSION = "0.0.2"


tests_requires = (
    # https://github.com/pytest-dev/pytest/issues/3579
    "pytest >= 3.7.2",
    "pytest-benchmark",
    "pytest-cov",
    "pytest-random-order",
    "pytest-xdist",
)

setuptools.setup(
    name="mercle",
    version=VERSION,
    url="https://github.com/EdgyEdgemond/merCle",
    author="Daniel Edgecombe",
    author_email="swinging.clown@gmail.com",
    include_package_data=True,
    packages=setuptools.find_packages("src"),
    package_dir={"": "src"},
    # py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    install_requires=(
        "cffi>=1.4.1",
    ),
    extras_require={

        # Useful tools for managing releases
        "release": (
            "bumpversion",
        ),

        # Useful tools for profiling and inspecting code.
        "dev": (
            "flake8",
            "flake8-commas",
            "flake8-isort",
            "flake8-mypy",
            "flake8-quotes",
            "isort>=4.3.15",
            "pudb",
            "pytest-pudb",
            "pytest-watch",
        ),

        # Handy if you want to run specific tests using the ``pytest``
        # command (``setup.py test`` runs all tests by default, and it's
        # a bit tricky to pass args to that command).
        "test": tests_requires,

    },
    # cffi_modules=[
    #     "./src/build_merkle.py:ffi",
    # ],

    # Configure test dependencies and runner.
    # https://docs.pytest.org/en/latest/goodpractices.html#integrating-with-setuptools-python-setup-py-test-pytest-runner
    setup_requires=["pytest-runner"],
    test_suite="tests",
    tests_require=tests_requires,
)
