API
===

The multiphonon package provides tools to convert powder spectra
measured at direct-geometry inelastic neutron spectrometers to phonon density of states (DOS).

Most users will only need functions in  `Convenient functions`_, which reduces raw data in the form of NeXus files to I(Q,E) using Mantid,
and then obtain phonon DOS. 

Some users may obtain I(Q,E) spectrum through other routes, and only need 
methods to convert I(Q,E) to phonon DOS. These methods are 
in the `backward transformation`_ section.

Sometimes it may be useful to "simulate" the neutron powder spectrum from a phonon DOS,
probably obtained from ab initio calculation or other modeling techniques.
These methods are in `forward transformation`_.

Some helper functions users may found useful are in `helper functions`_.

Convenient functions
--------------------
Calculate DOS from NeXus files

.. autofunction:: multiphonon.getdos.getDOS

backward transformation
-----------------------
S(Q,E) -> DOS

This is the core functionality of this package.

.. autofunction:: multiphonon.backward.sqe2dos.sqe2dos
.. autofunction:: multiphonon.backward.singlephonon_sqe2dos.sqe2dos

forward transformation
----------------------
DOS -> S(Q,E)

Simulate S(Q,E) spectrum from phonon DOS using incoherent approximation

.. autofunction:: multiphonon.forward.dos2sqe
.. autofunction:: multiphonon.forward.phonon.sqe
.. autofunction:: multiphonon.forward.phonon.sqehist

helper functions
----------------
.. autofunction:: multiphonon.sqe.interp
.. autofunction:: multiphonon.getdos.reduce2iqe
.. autofunction:: multiphonon.redutils.reduce
.. automodule:: multiphonon.backward.plotutils
   :members:
		
