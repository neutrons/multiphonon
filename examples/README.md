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
    
Obtain example notebooks

    $ git clone https://github.com/sns-chops/multiphonon
    $ cd multiphonon/examples
    
Start jupyter server

    $ jupyter notebook
    
Open an example notebook and follow instructions

**Note:** For an example notebook, look for a pdf with same name. It should contain expected outputs and plots.
