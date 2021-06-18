#!/usr/bin/python3
#
# FURsetup
# A command line interface for the libFURdatabase library.
# Allows for the setup of the FUR database.

from lib import libFURdatabase
from lib import libFURshared   # Reusing code from annotation utilities project (for file type detection)
import argparse
import sys

# Program constants
overwrite = 1   # When set the program deletes any existing databases.

## Command line options:
### Parse the command line arguments
parser = argparse.ArgumentParser(description="FUR database setup utility")
# Command:
parser.add_argument("action", help="Database action (create, export, delete, deduplicate or info)", action="store")
# Arguments:
parser.add_argument("-i","--input", help="Input filename", type=argparse.FileType('r'))
parser.add_argument("-o","--output", help="Output filename", type=argparse.FileType('w'))
parser.add_argument("-g","--genome", help="Genome filename", type=argparse.FileType('r'))
parser.add_argument("-c","--config", help="Config filename", type=argparse.FileType('r'))
parser.add_argument("-H","--hostname", help="SQL server hostname", action="store")
parser.add_argument("-U","--username", help="SQL server username", action="store")
parser.add_argument("-P","--password", help="SQL server password", action="store")
parser.add_argument("-D","--database", help="SQL server database", action="store")
parser.add_argument("-t","--type", help="Annotation filetype", action="store")
parser.add_argument("-T","--table", help="Table name", action="store")
parser.add_argument("-s","--flankingsize", help="Size of flanking regions", nargs=1, type=int)
parser.add_argument("-f","--flankingoffset", help="Adds a margin before the flanking regions", nargs=1, type=int)
parser.add_argument("-m","--mincontigsize", help="Minimum contig lengths", nargs=1, type=int)
parser.add_argument("-n","--noalt", help="Discard alternative genome sequences on import", action="store_true")
parser.add_argument("-e","--expdup", help="Expected number of duplicates (for use with concatenated psl files)", nargs=1, type=int)
parser.add_argument("-v","--verbose", help="Increased verbosity", action="store_true")

# Any commands entered without a flag
args = parser.parse_args()


# Load the options either from the config file or command line

# Load config file options, if provided
loadedarguments = {}
if args.config:
    fileobj = args.config
    # Put any arguments present into a dictionary
    for line in fileobj:
        if line[0] != "#":
            entries = line.split('\t')
            if len(entries)==2:
                loadedarguments[entries[0]]=entries[1]

# Load config options passed from the command line

# Set verbosity:
verbosity = 0
if args.verbose:
    verbosity=1
elif "verbose" in loadedarguments:
    verbosity = int(loadedarguments.get("verbose"))

# Set SQL details:
hostname = ""
if args.hostname:
    hostname=args.hostname
elif "hostname" in loadedarguments:
    hostname = loadedarguments.get("hostname").strip()

username = ""
if args.username:
    username=args.username
elif "username" in loadedarguments:
    username = loadedarguments.get("username").strip()

password = ""
if args.password:
    password=args.password
elif "password" in loadedarguments:
    password = loadedarguments.get("password").strip()

database = "FURdb"
if args.database:
    database=args.database
elif "database" in loadedarguments:
    database = loadedarguments.get("database").strip()

# Input and output files (NOTE: The command line interface reuses the input/output option so this should be passed at the prompt)
inputfile = None
if args.input:
    inputfile=args.input
elif "input" in loadedarguments:
    inputfile = open(loadedarguments.get("input").strip(),'r')

outputfile = None
if args.output:
    outputfile=args.output
elif "output" in loadedarguments:
    outputfile = open(loadedarguments.get("output").strip(),'w')

genomefile = None
if args.genome:
    genomefile=args.genome
elif "genome" in loadedarguments:
    genomefile = open(loadedarguments.get("genome").strip(),'r')

# Other optional commands

filetype = None
if args.type:
    filetype=args.type.upper()
elif "type" in loadedarguments:
    filetype = loadedarguments.get("type").strip().upper()

tablename = "UnmaskedContigs"
if args.table:
    tablename=args.table
elif "table" in loadedarguments:
    tablename = loadedarguments.get("table").strip()

flankingsize = 5000
if args.flankingsize:
    flankingsize=args.flankingsize[0]
elif "flankingsize" in loadedarguments:
    flankingsize = int(loadedarguments.get("flankingsize"))

flankingoffset = 0
if args.flankingoffset:
    flankingoffset=args.flankingoffset[0]
elif "flankingoffset" in loadedarguments:
    flankingoffset = int(loadedarguments.get("flankingoffset"))

mincontigsize = 20
if args.mincontigsize:
    mincontigsize=args.mincontigsize[0]
elif "mincontigsize" in loadedarguments:
    mincontigsize = int(loadedarguments.get("mincontigsize"))

noaltchr = 0
if args.noalt:
    noaltchr=1
elif "noalt" in loadedarguments:
    noaltchr = int(loadedarguments.get("noalt"))

expdup=1
if args.expdup:
    expdup=args.expdup[0]
elif "expdup" in loadedarguments:
    expdup = int(loadedarguments.get("expdup"))

# Check which command has been requested
if args.action.lower()=="create":
    # Create the database and load the flanking sequences
    # Check the required inputs:
    if not inputfile:
        print("Annotation file required (missing --input option)")
        sys.exit()
    if not genomefile:
        print("Genome file required (missing --genome option)")
        sys.exit()
    if not filetype:
        filetype = libFURshared.detectFileType(inputfile)
        if not filetype:
            print("\nInput file type could not be detected, please specify using the type argument.\n")
            sys.exit()
    else:
        if filetype not in ["BED", "DFAM", "UCSC"]:
            print("\nAccepted annotation file type options are BED, DFAM or UCSC.\n")
            sys.exit()
    # Perform the action
    # Create database
    if verbosity:
        print("Creating database")
    libFURdatabase.createDB(username,password,hostname,database, overwrite)
    # Connect to database
    if verbosity:
        print("- Connecting to database, "+database)
    databaseobj = libFURdatabase.database(username,password,hostname,database, verbosity)
    # Populate annotation table
    if verbosity:
        print("- Populating annotation table, with "+filetype+" file "+inputfile.name)
    databaseobj.populateAnnotations(inputfile, filetype)
    # Populate flanking region table
    if verbosity:
        print("- Populating flanking region table, using file "+genomefile.name+" with a size of "+str(flankingsize)+"bp offset by "+str(flankingoffset)+"bp")
    databaseobj.populateFlankingRegions(genomefile, flankingsize, flankingoffset)
    # Populate unmasked contigs table
    if verbosity:
        print("- Populating unmasked region table, using a minimum contig size of "+str(mincontigsize)+"bp")
    databaseobj.populateUnmaskedContigs(mincontigsize)
elif args.action.lower()=="deduplicate":
    # Create a table with duplicate entries removed
    # Check the required inputs:
    if not inputfile:
        print("Deduplication file required (missing --input option)")
        sys.exit()
    # Connect to database
    if verbosity:
        print("- Connecting to database, "+database)
    databaseobj = libFURdatabase.database(username,password,hostname,database, verbosity)
    # Populate deduplication table
    if verbosity:
        print("- Populating deduplicated contigs table, from "+inputfile.name+" with a minimum contig size of "+mincontigsize)
        if noaltchr == 1:
            print("-- Duplicates on chromosomes ending in '_alt' are being ignored.")
    databaseobj.populateDeduplicatedContigs(inputfile, mincontigsize, noaltchr, expdup)
elif args.action.lower()=="delete":
    # Delete contents from a table
    # Check the required inputs:
    if not tablename:
        print("Table name required (missing --table option)")
        sys.exit()
    # Connect to database
    if verbosity:
        print("- Connecting to database, "+database)
    databaseobj = libFURdatabase.database(username,password,hostname,database, verbosity)
    # Remove all entries from the table
    if verbosity:
        print("- Removing all entries from "+tablename+" table")
    databaseobj.deleteTableRows(tablename)
elif args.action.lower()=="export":
    # Simple export of a table sequences as a FASTA file
    # Check the required inputs:
    if not outputfile:
        print("Output file name required (missing --output option)")
        sys.exit()
    # Connect to database
    if verbosity:
        print("- Connecting to database, "+database)
    databaseobj = libFURdatabase.database(username,password,hostname,database, verbosity)
    # Export the table
    if verbosity:
        print("- Exporting sequences in "+tablename+" table to "+outputfile.name+" (FASTA format)")
    databaseobj.exportStoredSequences(outputfile, tablename)
elif args.action.lower()=="info":
    # Display basic information on the database for diagnosis purposes
    # Connect to database
    if verbosity:
        print("- Connecting to database, "+database)
    databaseobj = libFURdatabase.database(username,password,hostname,database, verbosity)
    # Displaying basic table statistics
    tableinfo = databaseobj.tablesizes()
    print("\nDatabase information for "+database)
    for table in tableinfo:
        print("Table: "+table[0]+" has "+str(table[1])+" entries and contains "+str(table[2])+"bp of sequence.")
    print()
else:
    print("ERROR: Invalid action")
    print("Valid options are: create, deduplicate, delete, export and info.")
