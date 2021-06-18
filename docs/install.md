# Installation

## Requirements:

FURdb is written in, and requires, a recent version of Python (version 3). The mysql-connector module is required for use with SQL databases.

The recommended workflow also requires the Annotation Utilities package for pre/post processing, BLAT for deduplication and an alignment package, capable of generating a .sam file, such as Bowtie2. Optionally a mySQL database can be used for improved performance.

[Annotation Utilities](https://github.com/DanielFaulkner/AnnotationUtilities)
[BLAT](http://hgdownload.soe.ucsc.edu/admin/exe/)

## Instructions:

FURdb does not require installing. Provided the directory structure remains the same FURdb's commands can be run from that location using python (ie. python3 /path/to/FUR<tool>.py).

To make use easier for Linux based operating systems an install script is provided which will configure the FURdb tools so they can be started without the python command (ie. ./path/to/tool.py) and you will be prompted if it is possible to update your user settings to make the application available without typing the full file path (ie. utility.py).

To start the install script from a terminal enter:
python3 install.py

No changes will be made to your user account settings without confirmation.


## Uninstallation:

To uninstall simply delete the directory containing FURdb. If you have used the installer to make the tools available without typing in the file path you will need to edit the ~/.bashrc file to comment out or remove the added line (indicated by a preceding identifying comment).
