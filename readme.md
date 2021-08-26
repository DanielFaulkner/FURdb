# FUR database (FURdb)
The Flanking Unique Region database identifies unique genomic regions flanking annotation entries and allows them to be exported for alignment. The alignment file can then be used to produce expression counts for each annotation. This information can aid in identifying annotations which contain an active promoter.

Supported annotation file formats are: BED, GTF/GFF, DFAM and UCSC Table browser downloads.  

The 'doc' folder contains documentation on the use of FURdb.  

**NOTE:** While care has been made to remove errors the outputs of these utilities come with no guarantee of accuracy. Please check the outputs of FURdb are accurate and suitable before using in research or production settings. Please note the RPKM values generated do NOT account for some of the available options, and therefore should not be relied upon. Additionally the GUI is a work in progress, and the current prototype requires pyQT5 to run.  

## Requirements
- Python, version 3
- Linux - however other operating systems may work with little or no modification needed.

## Author

FURdb was written by Daniel Rowell Faulkner.
