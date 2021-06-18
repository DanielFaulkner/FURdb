#!/usr/bin/python3

# Testing file for FUR inspect Functions

from lib import libFURinspect
import argparse
import sys

## Command line options:
### Parse the command line arguments
parser = argparse.ArgumentParser(description="FURdb inspection utility")
# Command:
parser.add_argument("action", help="Inspection action (lookupsequence, lookupanno, lookupcontig)", action="store")
# Arguments:
parser.add_argument("-c","--config", help="Config filename", type=argparse.FileType('r'))
parser.add_argument("-H","--hostname", help="SQL server hostname", action="store")
parser.add_argument("-U","--username", help="SQL server username", action="store")
parser.add_argument("-P","--password", help="SQL server password", action="store")
parser.add_argument("-D","--database", help="SQL server database", action="store")
parser.add_argument("-v","--verbose", help="Increased verbosity", action="store_true")
parser.add_argument("-T","--table", help="Table name", action="store")
parser.add_argument("-i","--id", help="ID number", nargs=1, type=int)

# Any commands entered without a flag
args = parser.parse_args()

# Store input values:

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

# Inspection specific options

tablename = "DeduplicatedContigs"
if args.table:
    tablename=args.table
elif "table" in loadedarguments:
    tablename = loadedarguments.get("table").strip()

idnum = -1
if args.id:
    idnum=args.id[0]
elif "flankingsize" in loadedarguments:
    idnum = int(loadedarguments.get("idnum"))

# Check if an ID number has been passed:
if idnum<0:
    print("ID number option required")
    sys.exit()

# Process actions

if args.action.lower()=="lookupsequence":
    # Connect:
    if verbosity:
        print("Connecting to database\n")
    inspectobj = libFURinspect.inspect(username,password,hostname,database,verbosity)
    # Get the sequence
    if verbosity:
        print("Retrieving sequence for contig "+str(idnum)+" from table "+str(tablename))
    seq = inspectobj.exportSequenceSingle(idnum, tablename)
    print(seq)
    if verbosity and seq=="":
        print("No sequence returned")
elif args.action.lower()=="lookupanno":
    # Connect:
    if verbosity:
        print("Connecting to database\n")
    inspectobj = libFURinspect.inspect(username,password,hostname,database,verbosity)
    # Look up which contigs refer to an annotation
    contigs = inspectobj.annoContigs(idnum, tablename)
    if verbosity:
        print("Annotation "+str(idnum)+" contains the following contigs in the "+str(tablename)+" table.")
        templatestr = "Contig: {}\tStart position: {}\tEnd position: {}"
        for item in contigs:
            print(templatestr.format(item[0],item[1],item[2]))
    else:
        templatestr = "{}\t{}\t{}"
        for item in contigs:
            print(templatestr.format(item[0],item[1],item[2]))
elif args.action.lower()=="lookupcontig":
    # Connect:
    if verbosity:
        print("Connecting to database\n")
    inspectobj = libFURinspect.inspect(username,password,hostname,database,verbosity)
    # Look up which annotation a contig relates
    anno = inspectobj.contigAnno(idnum, tablename)
    if verbosity:
        print("Contig "+str(idnum)+" in table "+str(tablename)+" is from annotation "+str(anno))
    else:
        print(anno)
else:
    print("Invalid action: Valid commands are lookupsequence, lookupanno and lookupcontig.")
