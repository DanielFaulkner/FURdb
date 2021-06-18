#!/usr/bin/python3
# FURanalyse
# Tools to analyse RNA query sequences against the FUR database

import argparse
from lib import libFURanalysis
import sys

## Command line options:
### Parse the command line arguments
parser = argparse.ArgumentParser(description="FUR analysis")
# Command:
parser.add_argument("action", help="Action (export, reportall, reportgtf, reportcount and reportcontigcount)", action="store")
# Arguments:
parser.add_argument("-i","--input", help="Input filename", type=argparse.FileType('r'))
parser.add_argument("-o","--output", help="Output filename", type=argparse.FileType('w'))
parser.add_argument("-c","--config", help="Config filename", type=argparse.FileType('r'))
parser.add_argument("-H","--hostname", help="SQL server hostname", action="store")
parser.add_argument("-U","--username", help="SQL server username", action="store")
parser.add_argument("-P","--password", help="SQL server password", action="store")
parser.add_argument("-D","--database", help="SQL server database", action="store")
parser.add_argument("-T","--table", help="Table name", action="store")
parser.add_argument("-v","--verbose", help="Increased verbosity", action="store_true")
# Export options:
parser.add_argument("--ori", help="Orientation", action="store")
parser.add_argument("--end", help="End", action="store")
parser.add_argument("--equal", help="Equal length", action="store_true")
parser.add_argument("--largest", help="Largest sequence only", action="store_true")
parser.add_argument("--closest", help="Closest sequence only", action="store_true")
parser.add_argument("--fixed", help="Fixed sequence length", nargs=1, type=int)
# Analysis options:
parser.add_argument("--quality", help="Minimum alignment quality", nargs=1, type=int)
parser.add_argument("--all", help="Include annotations with no matches", action="store_true")
parser.add_argument("--sensecount", help="Sense end count file", type=argparse.FileType('w'))
parser.add_argument("--anticount", help="Antisense end count file", type=argparse.FileType('w'))
parser.add_argument("--noheader", help="Omit header line", action="store_true")
parser.add_argument("--regions", help="Organise by regions (GTF)", action="store_true")

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

# Other optional settings

tablename = "DeduplicatedContigs"
if args.table:
    tablename=args.table
elif "table" in loadedarguments:
    tablename = loadedarguments.get("table").strip()

exOrientation = "G"
if args.ori:
    exOrientation=args.ori
elif "ori" in loadedarguments:
    exOrientation = loadedarguments.get("ori").strip()

exEnd = "B"
if args.end:
    exEnd=args.end
elif "end" in loadedarguments:
    exEnd = loadedarguments.get("end").strip()

exEqual = 0
if args.equal:
    exEqual=1
elif "equal" in loadedarguments:
    exEqual = int(loadedarguments.get("equal"))

exLargest = 0
if args.largest:
    exLargest=1
elif "largest" in loadedarguments:
    exLargest = int(loadedarguments.get("largest"))

exClosest = 0
if args.closest:
    exClosest=1
elif "closest" in loadedarguments:
    exClosest = int(loadedarguments.get("closest"))

exFixed = 0
if args.fixed:
    exFixed=args.fixed[0]
elif "quality" in loadedarguments:
    exFixed = int(loadedarguments.get("fixed"))

quality = 40
if args.quality:
    quality=args.quality[0]
elif "quality" in loadedarguments:
    quality = int(loadedarguments.get("quality"))

# Set sample name to the first part of the filename
samplename = ""
if inputfile:
    samplename = inputfile.name.split('.')[0]

all = 0
if args.all:
    all=1
elif "all" in loadedarguments:
    all = int(loadedarguments.get("all"))

sensecountfile = None
if args.sensecount:
    sensecountfile=args.sensecount
elif "output" in loadedarguments:
    sensecountfile = open(loadedarguments.get("sensecount").strip(),'w')

anticountfile = None
if args.anticount:
    anticountfile=args.anticount
elif "anticount" in loadedarguments:
    anticountfile = open(loadedarguments.get("anticount").strip(),'w')

header = 1
if args.noheader:
    header=0
elif "noheader" in loadedarguments:
    header = int(loadedarguments.get("noheader"))

regions = 0
if args.regions:
    regions=1
elif "regions" in loadedarguments:
    regions = int(loadedarguments.get("regions"))

# Process the input:
# Check which command has been requested
if args.action.lower()=="export":
    # Check the provided arguments:
    if not outputfile:
        print("Output filename argument required")
        sys.exit()
    # Connect to database
    if verbosity:
        print("Connecting to FUR database")
    try:
        analysisobj = libFURanalysis.analysis(username,password,hostname,database,verbosity)
    except:
        print("\nError connecting to database - check the settings used.\n")
        raise
    # Set the table:
    analysisobj.setTableVar(tablename)
    # Export the sequence information
    if verbosity:
        print("Exporting sequence information")
    analysisobj.exportSequencesAdv(outputfile,exOrientation, exEnd, exEqual,exLargest,exFixed,exClosest)
    if verbosity:
        print("Exported to "+outputfile.name)
        numExcluded = len(analsisobj.excludedAnnos)
        if numExcluded>0:
            print(str(numExcluded)+" annotations did not meet the export criteria.")
            #print("These annotations are:")    # Uncomment to list the excluded annotation IDs
            #for item in analsisobj.excludedAnnos:
            #    print(item)
elif args.action.lower()=="reportall":
    # Check the provided arguments:
    if not inputfile:
        print("Input filename argument required")
        sys.exit()
    if not outputfile:
        print("Output filename argument required")
        sys.exit()
    # Connect to database
    if verbosity:
        print("Connecting to FUR database")
    try:
        analysisobj = libFURanalysis.analysis(username,password,hostname,database,verbosity)
    except:
        raise("Error connecting to database - check the settings used.")
    # Set the table:
    analysisobj.setTableVar(tablename)
    # Export report
    if verbosity:
        print("Processing alignment file (this will take a few minutes)")
    samalignobj = libFURanalysis.alignfile(analysisobj,inputfile,quality,all)
    if verbosity:
        print("Producing report")
    libFURanalysis.reportAll(samalignobj,outputfile,header)
    if verbosity:
        print("Report on all annotation information saved to "+outputfile.name)
elif args.action.lower()=="reportgtf":
    # Check the provided arguments:
    if not inputfile:
        print("Input filename argument required")
        sys.exit()
    if not outputfile:
        print("Output filename argument required")
        sys.exit()
    # Connect to database
    if verbosity:
        print("Connecting to FUR database")
    try:
        analysisobj = libFURanalysis.analysis(username,password,hostname,database,verbosity)
    except:
        raise("Error connecting to database - check the settings used.")
    # Set the table:
    analysisobj.setTableVar(tablename)
    # Export report
    if verbosity:
        print("Processing alignment file (this may take a few minutes)")
    samalignobj = libFURanalysis.alignfile(analysisobj,inputfile,quality,all)
    if verbosity:
        print("Producing report")
    libFURanalysis.reportGTF(samalignobj,outputfile,regions,header)
    if verbosity:
        print("Report in GTF format saved to "+outputfile.name)
elif args.action.lower()=="reportcount":
    # Check the provided arguments:
    if not inputfile:
        print("Input filename argument required")
        sys.exit()
    if not outputfile:
        print("Output filename argument required")
        sys.exit()
    # Connect to database
    if verbosity:
        print("Connecting to FUR database")
    try:
        analysisobj = libFURanalysis.analysis(username,password,hostname,database,verbosity)
    except:
        raise("Error connecting to database - check the settings used.")
    # Set the table:
    analysisobj.setTableVar(tablename)
    # Export report
    if verbosity:
        print("Processing alignment file (this will take a few minutes)")
    samalignobj = libFURanalysis.alignfile(analysisobj,inputfile,quality,all)
    if verbosity:
        print("Producing report")
    libFURanalysis.reportCount(samalignobj,sensecountfile,anticountfile,outputfile,header,samplename)
    if verbosity:
        print("Report on annotation counts saved to "+outputfile.name)
elif args.action.lower()=="reportcontigcount":
    # Check the provided arguments:
    if not inputfile:
        print("Input filename argument required")
        sys.exit()
    if not outputfile:
        print("Output filename argument required")
        sys.exit()
    # Connect to database
    if verbosity:
        print("Connecting to FUR database")
    try:
        analysisobj = libFURanalysis.analysis(username,password,hostname,database,verbosity)
    except:
        raise("Error connecting to database - check the settings used.")
    # Set the table:
    analysisobj.setTableVar(tablename)
    # Export report
    if verbosity:
        print("Processing alignment file (this will take a few minutes)")
    samalignobj = libFURanalysis.alignfile(analysisobj,inputfile,quality,all)
    if verbosity:
        print("Producing report")
    libFURanalysis.reportContigCount(samalignobj,outputfile,header,samplename)
    if verbosity:
        print("Report on annotation counts saved to "+outputfile.name)
else:
    print("Invalid command entered. Please use either: export, reportall, reportgtf, reportcount or reportcontigcount")
