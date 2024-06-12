Installation
============

.. note:: SNS users can skip this step and use this software package directly at SNS analysis cluster (see :ref:`usage`).

Minimal installation
--------------------

The multiphonon package can be installed using conda (python 2)
on a recent 64bit linux (ubuntu/fedora/centos) distribution::

      $ conda config --add channels conda-forge
      $ conda config --add channels mcvine
      $ conda install multiphonon

Information on dependencies of this code can be found at `the conda recipe <https://github.com/neutrons/multiphonon/blob/next/conda-recipe/meta.yaml>`_.

      
Full installation
-----------------
  
The full installation requires `mantid <http://mantidproject.org>`_-framework, which can be installed using conda
on a recent, 64bit, linux (ubuntu/fedora/centos) **standard desktop** distribution.

The multiphonon package converts a I(Q,E) spectrum to DOS.
Experimental data obtained from direct-geometry inelastic neutron spectrometers first need to
be converted to I(Q,E) spectra.
Those experimental data are usually in the form of nexus files
(including event mode nexus files, histogram mode nexus files,
and nxspe files) and can be reduced to I(Q,E) spectra using `mantid <http://mantidproject.org>`_.
Convenient methods and example notebooks exist in multiphonon for this preprocessing step.

For those methods to work, mantid-framework is needed::

      $ conda config --add channels mantid
      $ conda install mantid-framework

Finally, some example jupyter notebooks need `ipywe <https://github.com/scikit-beam/ipywe>`_::

      $ conda config --add channels neutrons
      $ conda install ipywe


Notes on Mantid conda installation
""""""""""""""""""""""""""""""""""
`Mantid <http://mantidproject.org>`_ is a large, sophisticated software for neutron data reduction and analysis.
Its flagship application is its GUI `mantidplot <https://www.mantidproject.org/MantidPlot:_General_Concepts_and_Terms>`_.
The multiphonon package does not require mantidplot but depends on the algorithms in mantid-framework for reducing DGS data.
At this time, support of conda installation of mantid-framework is less universal than the multiphonon package itself.
No substantial tests have been done on mantid-framework running on headless systems.


System requirements
-------------------

If mantid is used to reduce data from nexus files, the `mantid system requirements <https://www.mantidproject.org/System_Requirements>`_
should be observed. Actually, 8GB memory is recommended.

If mantid is not used, system requirements may be relaxed.


Why not PyPI installation
-------------------------      
Some required and optional dependencies of multiphonon contain sophistated C++ libraries so it is much easier to rely
on the conda environment for installation. However, multiphonon package itself is a pure python package,
and can be installed by::

    $ python setup.py install
    
if all dependecies are already installed.
