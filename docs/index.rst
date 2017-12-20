.. multiphonon documentation master file, created by
   sphinx-quickstart on Mon Sep 25 12:55:50 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

API documentation for multiphonon package
=========================================

.. toctree::
   :maxdepth: 2

Convenient function: getDOS from NeXus files
--------------------------------------------

.. autofunction:: multiphonon.getdos.getDOS

backward transformation: S(Q,E) -> DOS
--------------------------------------
This is the core functionality of this package.

.. autofunction:: multiphonon.backward.sqe2dos.sqe2dos
.. autofunction:: multiphonon.backward.singlephonon_sqe2dos.sqe2dos

forward transformation: DOS -> S(Q,E)
-------------------------------------

Simulate S(Q,E) spectrum from phonon DOS using incoherent approximation

.. autofunction:: multiphonon.forward.dos2sqe
.. autofunction:: multiphonon.forward.phonon.sqe
.. autofunction:: multiphonon.forward.phonon.sqehist

helper functions
----------------
.. autofunction:: multiphonon.sqe.interp
.. autofunction:: multiphonon.redutils.reduce
.. automodule:: multiphonon.backward.plotutils
   :members:
		
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

