#!/usr/bin/env python

import os

from setuptools import find_packages, setup

here = os.path.dirname(__file__)
version_ns = {}
with open(os.path.join(here, "multiphonon", "_version.py")) as f:
    exec(f.read(), {}, version_ns)

# define distribution
setup(
    name="multiphonon",
    version=version_ns["__version__"],
    packages=find_packages(".", exclude=["tests", "docs"]),
    package_dir={"": "."},
    test_suite="tests",
    install_requires=[
        "numpy",
        "scipy",
    ],
    dependency_links=[],
    author="SNS-chops team",
    description="Multiphonon scattering and multiple scattering correction for powder data",
    license="BSD",
    keywords="neutron, inelastic neutron scattering, powder, phonon",
    url="https://github.com/neutrons/multiphonon",
    # download_url = '',
)
