#!/usr/bin/env python


from setuptools import setup, find_packages

# define distribution
setup(
    name = "multiphonon",
    version = "0.1",
    packages = find_packages(".", exclude=['tests', 'docs']),
    package_dir = {'': "."},
    test_suite = 'tests',
    install_requires = [
        'numpy', 'scipy',
    ],
    dependency_links = [
    ],
    author = "SNS-chops team",
    description = "Multiphonon scattering and multiple scattering correction for powder data",
    license = 'BSD',
    keywords = "neutron, inelastic neutron scattering, powder, phonon",
    url = "https://github.com/sns-chops/multiphonon",
    # download_url = '',
)

