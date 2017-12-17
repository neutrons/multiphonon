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

This example shows the core functionality of the multiphonon code,
converting S(Q,E) histogram to DOS:

    $ python getdos-Al.py


## Run jupyter notebook examples

To run the example notebooks, install in the same conda environment some extra packages

    $ conda config --add channels mantid
    $ conda config --add channels neutrons
    $ conda install mantid ipywe jupyter

Start a jupyter server

    $ jupyter notebook
    
And then open an example notebook and follow instructions

**Note:** For an example notebook, look for a pdf with same name. It should contain expected outputs and plots.
