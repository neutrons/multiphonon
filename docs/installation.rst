Installation
============


.. note:: SNS users can skip this step and use this software package directly at SNS analysis cluster (see :ref:`usage`).

The multiphonon package can be installed using conda (python 2)
on a recent, standard, 64bit, linux (ubuntu/fedora/centos) desktop distribution::

      $ conda config --add channels conda-forge
      $ conda config --add channels mcvine
      $ conda install multiphonon

Information on dependencies of this code can be found at `the conda recipe <https://github.com/sns-chops/multiphonon/tree/master/conda-recipe/meta.yaml>`_.

The multiphonon package converts a I(Q,E) spectrum to DOS.
Experimental data obtained from direct-geometry inelastic neutron spectrometers first need to
be converted to I(Q,E) spectra.
Those experimental data are usually in the form of nexus files
(including event mode nexus files, histogram mode nexus files,
and nxspe files) and can be reduced to I(Q,E) spectra using `mantid <http://mantidproject.org>`_.
Convenient methods and example notebooks exist in multiphonon for this preprocessing step.
For those methods and notebooks to work, the following installation is needed::

      $ conda config --add channels mantid
      $ conda install mantid-framework

Finally, example jupyter notebooks need `ipywe <https://github.com/scikit-beam/ipywe>`_::

      $ conda config --add channels neutrons
      $ conda install ipywe

      
Why not PyPI installation
-------------------------      
Some required and optional dependencies of multiphonon contain sophistated C++ libraries so it is much easier to rely
on the conda environment for installation. However, multiphonon package itself is a pure python package,
and can be installed by::

    $ python setup.py install
    
if all dependecies are already installed.
