# Examples

Obtain examples

    $ git clone https://github.com/sns-chops/multiphonon
    $ cd multiphonon/examples

## Run python script examples

First create a conda environment, activate it, and install multiphonon:

    $ conda create -n mph-demo python=2.7
    $ source activate mph-demo
    $ conda config --add channels conda-forge
    $ conda config --add channels mcvine
    $ conda install multiphonon

The following examples do not contain the preprocessing step to reduce raw experimental
data to I(Q,E) spectrum and do not require Mantid.

The first example shows the core functionality of the multiphonon code,
converting S(Q,E) histogram to DOS:

    $ python getdos-Al.py

A similar example below does basically the same conversion, but starting
from the S(Q,E) histogram represented by numpy arrays of Q axis, E axis, intensity
matrix, and squared errorbar matrix:

    $ python getdos-Al-from-nparrs.py


## Run jupyter notebook examples

To run the example notebooks, install in the same conda environment some extra packages

    $ conda config --add channels mantid
    $ conda config --add channels neutrons
    $ conda install mantid-framework ipywe jupyter

Start a jupyter server

    $ jupyter notebook
    
And then open an example notebook and follow instructions

**Note:** For an example notebook, look for a pdf with same name. It should contain expected outputs and plots.

Notebooks:
* For users who are not familar with python and more comfortable with GUI, please start with
  [the vanadium example with UI widgets](getdos2-V_Ei120meV.ipynb).
* For users who are comfortable with python and jupyter notebook, please start with
  [the vanadium example without UI widgts](getdos2-V_Ei120meV-noUI.ipynb).

