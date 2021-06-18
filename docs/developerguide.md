# Developer guide:

FURdb has been written in Python, using the standard builtin libraries where possible. To avoid adding additional installation steps builtin libraries should be used preferentially.

To enable code reuse each tool has a corresponding module in the 'lib' folder which contains functions and objects which are suitable for reuse. Those functions which are shared between tools are the module libFURshared.py. Comments and docstrings have been used to give indications of usage within those modules.


## External resources:
- [BED and GTF](https://genome.ucsc.edu/FAQ/FAQformat.html)
- [GTF](https://mblab.wustl.edu/GTF22.html)
- [DFAM](https://www.dfam.org/releases/Dfam_3.3/userman.txt)
- [UCSC Table browser](https://genome.ucsc.edu/cgi-bin/hgTables)
-- See userguide for further information on the use of FURdb.
-- See Annotation Utilities documentation for help on pre/post processing tasks.
