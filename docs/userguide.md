# FURdb userguide

FURdb identifies unique genomic regions flanking annotation entries and allows them to be exported for alignment and using the alignment file can produce expression counts for each annotation.

**Supported file types:**  
- BED
- UCSC Table browser
- DFAM
- GTF/GFF

All files must use tab separation and comments and headers must be indicated with a preceding '#' character. FURdb will try to determine the file type based on it's file extension or content. If FURdb is unable to determine the file type of an input this can be corrected by changing the file extension to either .bed,.csc,.fam or .gtf. Alternatively the -type argument can be used during FURdb setup.

The genome is also required (same revision as used for the annotations). Using a genome with a RepeatMasker soft mask is recommended to improve the process of removing duplicate sequences.

**Requirements:**  
Python (version 3) is required.  
BLAT is required.  
A sequence alignment package, such as Bowtie2, is required.  
mySQL is optional.  
FURdb has been written and tested in Linux, but may work with other operating systems with little or no modification.  

## FURdb setup (FURsetup.py)

This tool creates and sets up the FUR database. If the details for an SQL server are not provided pythons SQLite module will be used to create an SQL style database file. Creating the database requires multiple commands, to create the initial database, export the sequences, duplicate identification using BLAT and import the BLAT matches back into the database for the removal of duplicates.

**Arguments (required):**  
Action                Either create; export; delete; deduplicate or info.  
-i/ --input           Input filename  
-g/ --genome          Genome filename  

**Arguments (optional):**  
-t/ --type            Input file format (either DFAM, BED or UCSC)  
-o/ --output          Output filename  
-c/ --config          Config filename (tab separated file with argument tab option)  
-H/ --hostname        SQL Hostname (leave unfilled or set to “” to use a local file)  
-U/ --username        SQL Username  
-P/ --password        SQL Password  
-D/ --database        SQL Database name (or SQL filename if using SQLite)  
-T/ --table           SQL Table (for actions which require a table)  
-s/ --flankingsize    Size of the flanking region to import into the database  
-f/ --flankingoffset  Size of the offset between the annotation and flanking region.  
-m/ --mincontigsize   Minimum length of a contig.  
-n/ --noalt           Ignore alternative genome sequences  
-e/ --expdup          Expected number of duplicates (for use with concatenated psl files)
-v/ --verbose         Increased feedback  

**Actions:**  
- create:       Creates the database (requires --input and --genome arguments)
- export:       Performs a simple export of a table (required --output argument)
- delete:       Removes all entries from a table (required --table argument)
- deduplicate:  Removes duplicates identified in a .psl file (--input argument required)
- info:         Displays general information on database size.

**Example:**  
Setting up a database, without using an external SQL server. Note this will overwrite an existing database.  

Importing the annotation regions and exporting the sequences for duplicate identification:
python FURsetup.py create -i inputannotations.tsv -g genomefile.fa  
python FURsetup.py export -o exportfile.fa  

Checking for duplicates within the exported sequences:  
Option 1, Identify duplicates between exported flanking regions:  
- blat exportfile.fa exportfile.fa blatfile.psl  
Option 2, Identify duplicates between exported flanking regions and the genome (longer):  
- blat genome.fa exportfile.fa blatfile.psl  
Option 3, Perform both of the above steps:  
- blat exportfile.fa exportfile.fa blatfile1.psl  
- blat genome.fa exportfile.fa blatfile2.psl -noHead  
- cat blatfile1.psl blatfile2.psl > blatfile.psl  

Removing the identified matches from FURdb:  
Deduplication options 1 or 2:  
- python FURsetup.py deduplicate -i blatfile.psl  
Deduplication option 3:  
- python FURsetup.py deduplicate -i blatfile.psl -e 2  


## FURdb analysis (FURanalyse.py)

This tool queries a FUR database with a transcriptome to produce a report of expression counts.  

**Arguments (required):**  
Action                Either create; export; reportall; reportgtf; reportcount or reportcontigcount.  
-i/ --input           Input filename  
-o/ --output          Output filename   

**Arguments (optional):**  
-c/ --config          Config filename (tab separated file with argument tab option)  
-H/ --hostname        SQL Hostname (leave unfilled or set to “” to use a local file)  
-U/ --username        SQL Username  
-P/ --password        SQL Password  
-D/ --database        SQL Database name (or SQL filename if using SQLite)  
-T/ --table           SQL Table (sets the table to export or compare to)  
-v/ --verbose         Increased feedback  
--ori                 Export, orientation to use when exporting sequences  
                      (Genomic[G], Sense[S], Antisense[A], Bidirectional promoter[B])  
--end                 Export, which end (Sense aka 5’ [S], Antisense aka 3’ [A], Both[B])  
--equal               Export, one sequence of equal lengths from each end  
--largest             Export, only the largest sequence from each end  
--closest             Export, only the closest sequence from each end  
--fixed               Export, a fixed length sequence  
--quality             Minimum alignment quality value when interpreting SAM files  
--all                 Include annotations with no matching alignments  
--sensecount          Filename for the sense count report file (use with reportcount)  
--anticount           Filename for the antisense count report file (use with reportcount)  
--noheader            Omit the header line from the report  
--regions             Create an export entry for each flanking region instead of annotation.  

Note: Use of the orientation option requires the transcriptome to be directional and the alignment to be some combination of forward strand only/reverse complement strand only.  

**Actions:**  
- export:           Exports the sequences for analysis (ie. with bowtie2, bwt etc)    
- reportall:        Outputs a tab separated file will all information on the analysed alignments    
- reportgtf:        Outputs a gtf compatible file.    
- reportcount:      Outputs a tab separated file with only the annotation id and the count.   
- reportcontigcount Outputs a tab separated file with contig ids and the count.   

**Example:**  
Exporting the sequences from the default database. Performing an alignment with bowtie2 followed by producing a report. This example uses the --equal option to ensure the same sized regions are used from each side of the annotation, allowing a comparison across the annotation.  

python FURanalyse.py export -o output.fa --equal  
bowtie2-build output.fa Contigs  
bowtie2 -x Contigs -U RNAtranscriptome.fastq -S RNAalignment.sam  
python FURanalyse.py reportall -i RNAalignment.sam -o expressionreport.tsv  

**WARNING:**  
The report returns the RPKM score of each result. This value assumes that the entire, deduplicated, flanking regions were used when looking for matches. Using options to set a fixed or equal flanking region size are NOT reflected in the RPKM score at this time. Until these changes are reflected in the RPKM score it is recommended not to use the RPKM value as an indicator in these situations.  


## FURdb inspection (FURinspect.py)

This tool allows the lookup of specific information in the database. Which can be used in combination with the reports generated by FURanalyse to see which contigs and sequences are present within a high scoring annotation or which annotation a high scoring contig refers to.  

**Arguments (required):**  
Action                Either lookupsequence; lookupanno or lookupcontig.  
-i/ --id              ID number to lookup  

**Arguments (optional):**  
-c/ --config          Config filename (tab separated file with argument tab option)  
-H/ --hostname        SQL Hostname (leave unfilled or set to “” to use a local file)  
-U/ --username        SQL Username  
-P/ --password        SQL Password  
-D/ --database        SQL Database name (or SQL filename if using SQLite)  
-T/ --table           SQL Table (sets the table to lookup)  
-v/ --verbose         Increased feedback  

**Actions:**  
- lookupsequence:   Returns a sequence using the contig ID number.  
- lookupanno:       Looks up which contigs belong to an annotation.  
- lookupcontig:     Looks up which annotation a contig belongs to.  

**Example:**  
Looking up details on the sequence with ID number 30 in the default database.  

python FURinspect.py lookupsequence -i 30


## Example project  
An example project using the default database settings.

- Download and perform any preprocessing on an annotation file. (annofile.tsv)  
- Download the genome (soft masked and the same version as the annotation file uses).  
- Create a local database using the default settings.  
python FURsetup.py create -i annofile.tsv -g genomefile.fa  
- Export sequences for further deduplication  
python FURsetup.py export -o exportfile.fa  
- Identify duplicate regions using BLAT (or other software which generates a PSL file)  
blat exportfile.fa exportfile.fa blatfile.psl  
- Import the results of the BLAT search for matches for duplicate removal  
python FURsetup.py deduplicate -i blatfile.psl  
- Export sequences for alignment with an RNA transcriptome  
python FURanalyse.py export -o output.fa  
- Perform the alignment with the transcriptome (any software which produces .sam files)  
bowtie2-build output.fa Contigs  
bowtie2 -x Contigs -U RNAtranscriptome.fastq -S output.sam  
- Process the .sam alignment file and produce a report  
python FURanalyse.py reportall -i input.sam -o report.tsv  

**Warnings:**  
1. While care has been made to remove any errors the outputs from this software should be double checked, especially before use in published research.  
2. FURdb anaysis is not aware of the export settings used for the alignment. This means the RPKM and contig count columns should be ignored if a filter is applied to the exported sequences. (This maybe addressed in future releases)  

**Useful resources:**
Pre/post processing utilities:  
- [Annotation Utilities](https://github.com/DanielFaulkner/AnnotationUtilities)
Genome:  
- [UCSC](https://hgdownload.soe.ucsc.edu/downloads.html)
Annotations:  
- [DFAM](www.dfam.org)
- [UCSC](https://repeatbrowser.ucsc.edu/data/)
- [UCSC table browser](https://genome.ucsc.edu/cgi-bin/hgTables)
Software:*  
- [Python](https://www.python.org/)
- [BLAT](http://hgdownload.soe.ucsc.edu/admin/exe/)
- [Bowtie2](http://bowtie-bio.sourceforge.net/bowtie2/index.shtml)

*Note: Some of this software maybe available using your standard package repositories under Linux.
