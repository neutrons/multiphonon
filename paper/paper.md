---
title: 'Multiphonon: Phonon Density of States tools for Inelastic Neutron Scattering Powder Data'
tags:
  - neutron
  - inelastic neutron scattering
  - neutron spectroscopy
  - phonon density of states
  - density of states
authors:
  - name: Jiao Lin
    orcid: 0000-0001-9233-0100
    affiliation: 1
    affiliations:
  - name: Oak Ridge National Laboratory
    index: 1

date: September 26, 2017
bibliography: paper.bib
---

# Summary

multiphonon is a python package that calculates phonon density
of states from inelastic neutron scattering (see, for example [@FultzINSbook])
spectrum from powder sample.
The algorithm is a self-consistent iterative procedure
until the measured spectrum can be accounted for by
the one-phonon scattering, multi-phonon scattering, and multiple
scattering from the deduced phonon density of states,
assuming incoherent approximation
(Appendix of [@KreschNickel2007] and Section 6.5 "Calculation of Multiphonon Scattering" of [@FultzINSbook]).

-![S(Q,E) -> DOS](sqe2dos.png)

# References
paper.bib

# Notice of Copyright
This manuscript has been authored by UT-Battelle, LLC under Contract
No. DE-AC05-00OR22725 with the U.S. Department of Energy. The United
States Government retains and the publisher, by accepting the article
for publication, acknowledges that the United States Government retains
a non-exclusive, paid-up, irrevocable, worldwide license to publish
or reproduce the published form of this manuscript, or allow others
to do so, for United States Government purposes. The Department of Energy
will provide public access to these results of federally sponsored
research in accordance with the DOE Public Access Plan
(http://energy.gov/downloads/doe-public-access-plan).

# Acknowledgements

This work is sponsored by the Laboratory Directed Research and
Development Program of Oak Ridge National Laboratory, managed by
UT-Battelle LLC, for DOE. Part of this research is supported by the U.S.
Department of Energy, Office of Science, Office of Basic Energy
Sciences, User Facilities under contract number DE-AC05-00OR22725.


