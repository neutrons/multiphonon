# Examples

To run the example notebooks, first create a conda environment, activate it, and install relevant packages:

    $ conda create -n mph-demo python=2.7
    $ source activate mph-demo
    $ conda config --add channels conda-forge
    $ conda config --add channels mantid
    $ conda config --add channels mcvine
    $ conda config --add channels neutrons
    $ conda install multiphonon
    $ conda install jupyter


Obtain examples

    $ git clone https://github.com/sns-chops/multiphonon
    $ cd multiphonon/examples

## Run jupyter notebook examples
Start a jupyter server

    $ jupyter notebook
    
And then open an example notebook and follow instructions

**Note:** For an example notebook, look for a pdf with same name. It should contain expected outputs and plots.


## Run python script examples

For example

    $ python getdos-Al.py
