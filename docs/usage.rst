.. _usage:

Usage
=====


GetDOS at SNS analysis cluster using jupyter
--------------------------------------------

For SNS users, GetDOS can be performed at SNS analysis cluster through the jupyter.sns.gov website.

* First log into SNS analysis cluster using thinlinc. The instructions for that can be found at https://analysis.sns.gov/
* Inside the thinlinc session of analysis.sns.gov, open a browser window and connect to https://jupyter.sns.gov, and login with your XCAMS/UCAMS account credentials
* Follow the tutorial videos below:
    
  * `For the first time users, a setup is necessary  <https://www.youtube.com/embed/5XOX8RdHBnQ?start=0&end=36&version=3>`_
  * `Run GetDOS2 <https://www.youtube.com/embed/uTEEyifpG-k>`_ (this works for SNS data only)

    
GetDOS using local installation
-------------------------------

For any user, GetDOS can be performed with a local installation of multiphonon.
Examples and instructions can be found `here <https://github.com/sns-chops/multiphonon/tree/master/examples>`_



Multiple-Ei and Stitching
-------------------------

About the last warning in the test: it is expected since we are still experimenting on this new feature for "stitching"
together phonon DOSes measured at different neutron incident energies. Right now researchers more or less do the stitching
manually and somewhat arbitrarily, and this software provides two routines for stitching.
The warning is to alert the users that two methods of stitching were used but they disagree
somewhat in the calculation of scaling factor for stitching. The disagreement is actually acceptable in this case.
