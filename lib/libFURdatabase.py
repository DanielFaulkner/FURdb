# libFURcreate
# Functions required to create the FUR database

from lib import libFURshared    # Reusing code from annotation utilities project (Annotation object)
import os

# Constants
schemaver = 0		# Database schema version (currently unused but added to detect changes expected in database layout)

# Create the SQL database table structure
# INPUT: SQL login details (host, user, password) the name of the database to create and if an existing database should be replaced.
def createDB(SQLusername, SQLpassword, SQLhostname="localhost", dbname="FURdb", overwrite=0):
        """Creates the database and tables on the specified SQL server."""
        # Connect to SQL server
        if SQLhostname != "":
            # If a hostname is provided connect to the SQL server
            import mysql.connector
            FURdb = mysql.connector.connect(
                host=SQLhostname,
                user=SQLusername,
                password=SQLpassword
                )
            MySQLcursorObj = FURdb.cursor()
            # If set to overwrite drop existing database
            if overwrite==1:
                MySQLcursorObj.execute("DROP DATABASE IF EXISTS "+dbname)
            # Create new database
            MySQLcursorObj.execute("CREATE DATABASE "+dbname)	# If database present will throw an error.
            MySQLcursorObj.execute("USE "+dbname)
            # SQL terminology differences:
            autoinc = "INT AUTO_INCREMENT"
            prikey = ",PRIMARY KEY (id)"
        else:
            # If no hostname is provided use a local SQLite database
            import sqlite3
            # If set to overwrite remove existing database file
            if overwrite==1:
                if os.path.exists(dbname+".db"):
                    os.remove(dbname+".db")
            # Create new database
            FURdb = sqlite3.connect(dbname+".db")
            MySQLcursorObj = FURdb.cursor()
            # SQL terminology differences:
            autoinc = "INTEGER PRIMARY KEY AUTOINCREMENT"
            prikey = ""
		# Create TABLES
        MySQLcursorObj.execute("CREATE TABLE info ("
                    "tableid INT,"
                    "tableschema INT,"
                    "flankingsize INT,"
                    "flankingoffset INT,"
                    "mincontigsize INT,"
                    "PRIMARY KEY (tableid))")
        MySQLcursorObj.execute("CREATE TABLE annotations ("
                    "id "+autoinc+","
                    "repName VARCHAR(45) NOT NULL,"
                    "chrName VARCHAR(45),"
                    "alignStart INT,"
                    "alignEnd INT,"
                    "strand CHAR(1),"
                    "score INT,"
                    "matchStart INT,"
                    "matchEnd INT"
                    ""+prikey+")")
        # Tables of sequence with different levels of duplicate removal applied
        MySQLcursorObj.execute("CREATE TABLE flanking ("
                    "id "+autoinc+","
                    "annotation INT NOT NULL,"
                    "sequence TEXT,"
                    "start INT,"
                    "end INT"
                    ""+prikey+","
                    "FOREIGN KEY (annotation) REFERENCES annotations(id))")
        MySQLcursorObj.execute("CREATE TABLE UnmaskedContigs ("
                    "id "+autoinc+","
                    "annotation INT NOT NULL,"
                    "sequence TEXT,"
                    "start INT,"
                    "end INT"
                    ""+prikey+","
                    "FOREIGN KEY (annotation) REFERENCES annotations(id))")
        MySQLcursorObj.execute("CREATE TABLE DeduplicatedContigs ("
                    "id "+autoinc+","
                    "annotation INT NOT NULL,"
                    "sequence TEXT,"
                    "start INT,"
                    "end INT"
                    ""+prikey+","
                    "FOREIGN KEY (annotation) REFERENCES annotations(id))")
        # Populate any essential details:
        MySQLcursorObj.execute("INSERT INTO info VALUES (1, "+str(schemaver)+", 0, 0, 0)")
        FURdb.commit()
        FURdb.close()

# Shared database object functions
# Inherited by classes requiring an SQL connection to the database
class furdbobj(object):
    # Object creation tasks
    def __init__(self, SQLuser, SQLpass, SQLhost="localhost", SQLdb="FURdb", verbosity=0):
        """Create the object, set verbosity and connect it to the SQL database."""
        self.verbosity = verbosity
        # Connect to SQL server
        if SQLhost != "":
            # If a hostname is provided connect to the SQL server
            import mysql.connector                      # Module not builtin (needs error checking)
            self.FURdb = mysql.connector.connect(
                host=SQLhost,
                user=SQLuser,
                password=SQLpass,
                database = SQLdb
                )                                       # Fails with system halt
        else:
            # If no hostname is provided use a local SQLite database
            import sqlite3
            self.FURdb = sqlite3.connect(SQLdb+".db")   # Fails silently (creates db file)
        # Check database schema.
        MySQLcursorObj = self.FURdb.cursor()
        MySQLcursorObj.execute("SELECT tableschema FROM info")
        for (tableschema) in MySQLcursorObj:
            dbschema = int(tableschema[0])
        if dbschema != schemaver and self.verbosity == 1:
            print("Warning: Unexpected SQL database version.")
        # If successful store the hostname/username/password/database in the object for reuse (if needed)
        self.SQLuser = SQLuser
        self.SQLpass = SQLpass
        self.SQLhost = SQLhost
        self.SQLdb = SQLdb
	# Closes the database connection:
    def close(self):
        """Function to close the current database connection"""
        self.FURdb.close()


# Database population class.
class database(furdbobj):
    # Inherited object creation functions
    def __init__(self, SQLuser, SQLpass, SQLhost="localhost", SQLdb="FURdb", verbosity=0):
        """Create the object, set verbosity and connect it to the SQL database."""
        # Inherit the shared functions from a shared parent class
        super().__init__(SQLuser, SQLpass, SQLhost, SQLdb, verbosity)
    # Add L1 annotions - any filtering should be done on the file prior to this point
    # NOTE: Different sources use different scoring methods.
    def populateAnnotations(self, fileobj, filetype):
        """Populates the annotations table."""
        # Create cursor object
        MySQLcursorObj = self.FURdb.cursor()
        # Store header (if applicable)
        if filetype == "BED":
            header = ""
        else:
            header = fileobj.readline()
        # Loop through the annotation entries adding them to the SQL database
        for line in fileobj.readlines():
            # Process the entry and create a common object
            entry = libFURshared.Annotation(line, filetype, header)
            # If the annotation file lacks information on the position of the match leave those fields unpopulated (BED files)
            if entry.matchStart<0 and entry.matchEnd<0:
                MySQLcursorObj.execute("INSERT INTO annotations (repName, chrName, alignStart, alignEnd, strand, score) VALUES ('"+entry.repName+"', '"+entry.chrName+"', "+str(entry.alignStart)+", "+str(entry.alignEnd)+", '"+entry.strand+"', "+str(entry.score)+")")
            # Otherwise populate all fields
            else:
                MySQLcursorObj.execute("INSERT INTO annotations (repName, chrName, alignStart, alignEnd, strand, score, matchStart, matchEnd) VALUES ('"+entry.repName+"', '"+entry.chrName+"', "+str(entry.alignStart)+", "+str(entry.alignEnd)+", '"+entry.strand+"', "+str(entry.score)+", "+str(entry.matchStart)+", "+str(entry.matchEnd)+")")
        fileobj.close()
        self.FURdb.commit()
	# Create a new flanking region table (Depends on Annotation and Descriptor table)
	# INPUT: Human genome fasta file.
	# Note: Differences in numbering systems could cause an out by one error in the stored sequence.
    def populateFlankingRegions(self, fileobj, size=5000, offset=0):
        """Populates the flanking region table."""
        if self.verbosity:
            print("- Indexing genome")
        genomeIndex = indexFASTA(fileobj)
        # Access the database and store the flanking region size variable
        MySQLcursorObj = self.FURdb.cursor()
        MySQLcursorObj.execute("UPDATE info SET flankingsize="+str(size)+", flankingoffset="+str(offset)+" WHERE tableid=1")
        self.FURdb.commit()
        # Retrieve a list of chromosomes with annotations to process in chromosome order (faster)
        chrPresent = []
        MySQLcursorObj.execute("SELECT DISTINCT chrName FROM annotations")
        for (chrName) in MySQLcursorObj:
            chrPresent.append(chrName[0])
        # For each chromosome:
        for chr in chrPresent:
            if self.verbosity:
                print("Processing chromosome: "+chr)
            chrSequence = loadChr(fileobj, chr, genomeIndex)
            if chrSequence=="":
                if self.verbosity:
                    print("WARNING: No sequence available for chromosome "+chr+". Skipping annotation "+str(id))
            else:
                MySQLcurosorStore=[]
                MySQLcursorObj.execute("SELECT id, alignStart, alignEnd, strand FROM annotations WHERE chrName='"+chr+"'")
                for (id, alignStart, alignEnd, strand) in MySQLcursorObj:
                    # Store the values
                    MySQLcurosorStore=MySQLcurosorStore+[[id, alignStart, alignEnd, strand]]
                for id, alignStart, alignEnd, strand in MySQLcurosorStore:
                    # Retrieve following genomic region
                    startpos = int(alignEnd)+offset
                    endpos = startpos+size
                    seq = chrSequence[startpos:endpos]
                    # Check if the sequence is the expected length and correct if needed
                    if len(seq)!=size:
                        endpos = int(alignEnd)+len(seq)
                    # Store in database
                    if seq!="":
                        MySQLcursorObj.execute("INSERT INTO flanking (annotation, sequence, start, end) VALUES ("+str(id)+",'"+seq+"', "+str(startpos)+", "+str(endpos)+")")
                        self.FURdb.commit()
                    # Retrieve preceeding genomic region
                    endpos = int(alignStart)-offset
                    startpos = endpos-size
                    seq = chrSequence[startpos:endpos]
                    # Check if the sequence is the expected length and correct if needed
                    if len(seq)!=size:
                        startpos = int(alignStart)-len(seq)
                    # Store in database
                    if seq!="":
                        MySQLcursorObj.execute("INSERT INTO flanking (annotation, sequence, start, end) VALUES ("+str(id)+",'"+seq+"', "+str(startpos)+", "+str(endpos)+")")
                        self.FURdb.commit()
    # Create a table of unmasked contigs, preidentified in a softmapped genomic sequence (ie. Rep. Masked hg38)
    def populateUnmaskedContigs(self, minsize = 20):
        """Populate the unmasked table, by removing known repeat sequences already identified in the genome."""
        # Access the database and store the minimum contig length used.
        MySQLcursorObj = self.FURdb.cursor()
        MySQLcursorObj.execute("UPDATE info SET mincontigsize="+str(minsize)+" WHERE tableid=1")
        self.FURdb.commit()
        # Loop through the flanking table processing each entry
        MySQLcurosorStore=[]
        MySQLcursorObj.execute("SELECT annotation, sequence, start, end FROM flanking")
        for (annotation, sequence, start, end) in MySQLcursorObj:
            MySQLcurosorStore=MySQLcurosorStore+[[annotation, sequence, start, end]]
        for annotation, sequence, start, end in MySQLcurosorStore:
            if sequence != "":
                unmaskedseqs = findUnmaskedSeq(sequence, minsize)
                for entry in unmaskedseqs:
                    startpos = entry[0]
                    endpos = entry[1]
                    if self.verbosity>1:
                        print("Adding to annotation "+str(annotation)+" contig "+str(startpos)+":"+str(endpos))
                    MySQLcursorObj.execute("INSERT INTO UnmaskedContigs (annotation, sequence, start, end) VALUES ("+str(annotation)+", '"+sequence[startpos:endpos]+"',"+str(startpos+start)+", "+str(endpos+start)+")")
                    self.FURdb.commit()
    # Simple export function, required for exporting to BLAT for further deduplication
    def exportStoredSequences(self, fileoutobj, table="UnmaskedContigs"):
        """Simple export of all sequences in a table, without modification."""
        MySQLcursorObj = self.FURdb.cursor()
        MySQLcursorObj.execute("SELECT id, sequence FROM "+table)
        for (id, sequence) in MySQLcursorObj:
            name = str(id)
            libFURshared.exportFASTAEntry(fileoutobj, name, sequence)
    def populateDeduplicatedContigs(self, fileobj, minsize = 20, ignorealt=0, expdup=1):
        """Adds those sequences without duplications to the DeduplicatedContigs table."""
        MySQLcursorObj = self.FURdb.cursor()
        MySQLcursorObj2 = self.FURdb.cursor()
        # Create deduplication file object and process the file.
        dedupobj = dedupFile(fileobj)
        contigInfo = dedupobj.processFile(minsize, ignorealt)
        # Check the results from processing the file
        for contig in contigInfo:
            matches = contigInfo.get(contig)
            NumLargeMatches = matches[0]
            MatchPostions = matches[1]
            if NumLargeMatches==expdup and len(MatchPostions)==0:
                # Sequence found only itself. Therefore add to database.
                MySQLcursorObj.execute("SELECT annotation, sequence, start, end FROM UnmaskedContigs WHERE id="+str(contig))
                for (annotation, sequence, start, end) in MySQLcursorObj:
                    MySQLcursorObj2.execute("INSERT INTO DeduplicatedContigs (annotation, sequence, start, end) VALUES ("+str(annotation)+", '"+sequence+"',"+str(start)+", "+str(end)+")")
                    self.FURdb.commit()
            elif NumLargeMatches>expdup:
                # The majority of the sequence was found more than once. Therefore ignore.
                if self.verbosity>1:
                    print("Contig "+str(contig)+" duplicated more than expected. Ignoring.")
            else:
                # Parts of the seqence were duplicated. Needs further checking.
                # Load the sequence
                MySQLcursorObj.execute("SELECT annotation, sequence, start, end FROM UnmaskedContigs WHERE id="+str(contig))
                for (annotation, sequence, start, end) in MySQLcursorObj:
                    MaskedSequence = sequence
                    while len(MatchPostions)>0:
                        duplicate = MatchPostions.pop()
                        MaskedSequence = MaskedSequence[:duplicate[0]]+MaskedSequence[duplicate[0]:duplicate[1]].lower()+MaskedSequence[duplicate[1]:]
                    # Check the masked sequence for unmasked regions of sufficient length
                    unmaskedseqs = findUnmaskedSeq(MaskedSequence, minsize)
                    for entry in unmaskedseqs:
                        startpos = entry[0]
                        endpos = entry[1]
                        if self.verbosity>1:
                            print("Adding to annotation "+str(annotation)+" contig "+str(startpos)+":"+str(endpos))
                        MySQLcursorObj2.execute("INSERT INTO DeduplicatedContigs (annotation, sequence, start, end) VALUES ("+str(annotation)+", '"+sequence[startpos:endpos]+"',"+str(startpos+start)+", "+str(endpos+start)+")")
                        self.FURdb.commit()
    # This function allows a table to be reset, to allow the content to be regenerated.
    def deleteTableRows(self, tablename):
        """Function to remove all content from a table"""
        MySQLcursorObj = self.FURdb.cursor()
        MySQLcursorObj.execute("DELETE FROM "+str(tablename))
        self.FURdb.commit()
    # General database information functions:
    # Function to return information on each table
    def tablesizes(self):
        """Returns a list of table names, number of entries and size in bps"""
        MySQLcursorObj = self.FURdb.cursor()
        # Add annotation information:
        MySQLcursorObj.execute("SELECT count(*) FROM annotations")
        for (count) in MySQLcursorObj:
            tableinfo=[['annotations',count[0],0]]
        # Add sequence containing tables:
        seqtables = ["flanking","UnmaskedContigs","DeduplicatedContigs"]
        for table in seqtables:
            MySQLcursorObj.execute("SELECT count(*) FROM "+table)
            for (count) in MySQLcursorObj:
                count=count[0]
            basepairs = 0
            MySQLcursorObj.execute("SELECT sequence FROM "+table)
            for (sequence) in MySQLcursorObj:
                basepairs = basepairs+len(sequence[0])
            # Add to tableinfo list
            tableinfo=tableinfo+[[table, count, basepairs]]
        return tableinfo
    def databaseInfo(self):
        """Returns general database information"""
        # Check database schema.
        MySQLcursorObj = self.FURdb.cursor()
        MySQLcursorObj.execute("SELECT tableschema,flankingsize,flankingoffset,mincontigsize FROM info")
        for (tableschema,flankingsize,flankingoffset,mincontigsize) in MySQLcursorObj:
            dbschema = tableschema
            regionsize = flankingsize
            regionoffset = flankingoffset
            contigsize = mincontigsize
        return([dbschema,regionsize,regionoffset,contigsize])

### Function to parse the BLAT created PSL file
class dedupFile(object):
    """Deduplication file object"""
    def __init__(self, fileobj):
        """Setup deduplication object"""
        self.fileobj = fileobj
        self.setColumnsPSL()
        self.setDataStart()
    # Set the columns order - in a separate function incase other filetypes are added later
    def setColumnsPSL(self):
        """Setup the column order for a PSL file"""
        self.queryNameCol = 9
        self.querySizeCol = 10
        self.matchSizeCol = 0
        self.matchStartCol = 11
        self.matchEndCol = 12
        self.targetName = 13
    def setDataStart(self):
        """Identify the position where the header ends and the data starts"""
        self.fileobj.seek(0)
        line = self.fileobj.readline()
        matchedbases = line.split('\t')[self.matchSizeCol]
        while not matchedbases.isdigit():
            line = self.fileobj.readline()
            matchedbases = line.split('\t')[self.matchSizeCol]
        self.dataStartPos = self.fileobj.tell() - len(line)
    def processFile(self, minsize, ignorealt = 0):
        # Return: Dictionary[ID]=[NumLargeMatches,[[start,end],[start,end]]]
        self.fileobj.seek(self.dataStartPos)
        contigResults = {}
        for line in self.fileobj.readlines():
            fields = line.split('\t')
            if ignorealt and fields[self.targetName].strip()[-4:]=="_alt":
                # Ignoring entry on alternative chromosome sequence
                pass
            else:
                # Check if this a long duplicate
                if int(fields[self.matchSizeCol]) + minsize > int(fields[self.querySizeCol]):
                    largeduplicate = 1
                    positions = None
                else:
                    largeduplicate = 0
                    positions = [int(fields[self.matchStartCol]), int(fields[self.matchEndCol])]
                # If a smaller duplicate store the positions
                if fields[self.queryNameCol] not in contigResults:
                    # Create new entry
                    if positions:
                        contigResults[fields[self.queryNameCol]] = [largeduplicate,[positions]]
                    else:
                        contigResults[fields[self.queryNameCol]] = [largeduplicate,[]]
                else:
                    # Update existing
                    currentvalues = contigResults.get(fields[self.queryNameCol])
                    if positions:
                        contigResults[fields[self.queryNameCol]] = [currentvalues[0]+largeduplicate,currentvalues[1]+[positions]]
                    else:
                        contigResults[fields[self.queryNameCol]] = [currentvalues[0]+largeduplicate,currentvalues[1]]
        return contigResults

# Current process: Read each match entry.
# Current process: If match entry qname and tname are not identical add to list (along with start end and matched bases)
# Add: If whole genome if qname present more than once.
# Next function:
# Current process: If

# Function to separate out contigs from a given softmapped sequence.
# INPUT: Sequence and minimum contig size.
# OUTPUT: List of unmasked seqence positions - start, end
def findUnmaskedSeq(sequence, minsize):
    """Identifies regions which are unmasked (uppercase) and above the minimum size and returns those positions."""
    counter = 0
    startpos=-1
    endpos=-1
    remainSeqList = []
    for i in sequence:
        if i.isupper() and startpos<0:
            startpos=counter
        elif i.islower() and startpos>-1:
            endpos=counter
            if endpos-startpos>=minsize:
                # Add contig to database
                remainSeqList.append([startpos, endpos])
            # Reset start and end
            startpos=-1
            endpos=-1
        counter=counter+1
    return remainSeqList

### Functions to load genomic sequences

# This function goes through the provided genome file and creates an index of chromosome start positions to speed up the loadChr function.
# Input: Human Genome filename
# Output: Dictionary of chromosome start positions
def indexFASTA(fileobj):
	"""Creates a dictionary of chromosome start positions."""
	line = fileobj.readline()
	name = ""
	position = 0
	indexDict = {}
	while line:
		if line[0] == ">":
			name = line[1:].strip()
			position = fileobj.tell()-len(line)
			indexDict[name]=position
		line=fileobj.readline()
	return indexDict

# This function loads into memory the specified chromosome
# Input: Human Genome as a single fasta file and name of chromosome
# Output: Chromosome sequence as a string
def loadChr(fileobj, chromosome="", index={}):
    """Loads into memory the sequence for a single chromosome."""
    identifier = ""
    sequence = ""
    if chromosome in index:
        fileobj.seek(index.get(chromosome))	# If an index dictionary is passed and contains the chromosome value skip to this point
        line = fileobj.readline()
        while line:
            if line[0] == ">":
                if identifier==chromosome:
                    break
                identifier = line[1:].strip()
            elif identifier == chromosome:
                sequence = sequence + line.strip()
            line=fileobj.readline()
    return sequence

######## Work In Progress Code #######

# Create an object which can store, process and return everything related to an annotation flanking region
# INPUT: Flanking region
# OUTPUT: Unique sequences
class flankingobj(object):
    """Datatypes and functions relating to producing unique sequences from a larger sequence"""
    def __init__(self, genomeobj, chr, start=0, size=5000, verbosity=0):
        """Setup the flanking object"""
        self.size = size
        self.start = start
        self.verbosity = verbosity
    def filterUnmasked(self):
        """Removes the lowercase characters representing known repeats"""
        pass
    def loadSequence(self):
        """Load the genomic sequence"""
        pass

# Sequence objects
# Simple objects used for the logical temporary storage of sequence related variables
class sequenceobj(object):
    """A sequence with related variables"""
    def __init__(self, sequence, start, end):
        """Input the values to store in the object"""
        self.sequence = sequence
        self.start = start
        self.end = end

# An object which stores all the methods and variables to enable quick access to genomic sequence data
# Requires genome file object
# Returns genome sequence from chromosome start and end positions
# This method is unable to process genomes with inconsistant use of white space. Use with caution.
class genomeobj(object):
    """Load a genome and provide an index for quick sequence retrival"""
    def __init__(self, fileobj, verbosity=0):
        self.genomeobj = fileobj
        if verbosity:
            print("Indexing genome")
        self.indexGenome()
        if verbosity:
            print("Checking genome")
        self.checkGenome()
        if verbosity:
            for chr in self.chrCheck:
                if self.chrCheck.get(chr)==0:
                    print(chr+" failed the genome consistancy check.")
    def indexGenome(self):
        """Creates an index of chromosome start and end positions"""
        self.genomeobj.seek(0)
        name = ""
        position = 0
        indexStart = {}
        indexEnd = {}
        line = self.genomeobj.readline()
        while line:
            if line[0] == ">":
                posEnd = fileobj.tell()-len(line)
                if name!="":
                    indexEnd[name]=posEnd
                name = line[1:].strip()
                posStart = self.genomeobj.tell()
                indexStart[name] = posStart
            line=self.genomeobj.readline()
        self.chrStartPositions = indexStart
        self.chrEndPositions = indexEnd
    def checkGenome(self):
        """Checks the FASTA file for consistant use of whitespace. Note this method is not fool proof."""
        # Check for each chromosome
        lineLengths = {}
        lineWhiteSpaces = {}
        lineWhiteSpaceContents = {}
        chrCheck = {}
        for chr in self.chrStartPositions:
            # Get line length with and without whitespace.
            self.genomeobj.seek(self.chrStartPositions.get(chr))
            line = self.genomeobj.readline()
            lineLengths[chr] = len(line)
            lineWhiteSpaces[chr] = lineLengths.get(chr)-len(line.strip())
            lineWhiteSpaceContents[chr] = line[lineWhiteSpaces.get(chr):]
            # Calculate the expected length of the last line
            expectedLength = self.chrEndPositions.get(chr) % lineLengths.get(chr)
            # Check if the last line is this length, if not the line lengths must be inconsistant.
            self.genomeobj.seek(self.chrEndPositions.get(chr)-(lineLengths.get(chr)+lineWhiteSpaces.get(chr)))
            lastLine = self.genomeobj.read(expectedLength+lineWhiteSpaces.get(chr))
            if lastLine[:lineWhiteSpaces.get(chr)] == lineWhiteSpaceContents.get(chr):
                # Passed: Penultimate line break where it was expected.
                chrCheck[chr] = 1
            else:
                # Failed: Penultimate line break not present where expected.
                chrCheck[chr] = 0
        # Make the data available outside this function
        self.chrLineLengths = lineLengths
        self.chrLineWhiteSpaces = lineWhiteSpaces
        self.chrLineWhiteSpaceContents = lineWhiteSpaceContents
        self.chrCheck = chrCheck
        # Reset file pointer
        self.genomeobj.seek(0)
    def getSequence(self, chr, start, end):
        """Returns the requested region of the genome"""
        if self.chrCheck.get(chr)==1:
            # Calculate the file start position
            numLines = start//self.chrLineLengths.get(chr)
            startpos = self.chrStartPositions.get(chr)+start+(numLines*self.chrLineWhiteSpaces.get(chr))
            # Calculate the file end position
            numLines = end//self.chrLineLengths.get(chr)
            endpos = self.chrStartPositions.get(chr)+end+(numLines*self.chrLineWhiteSpaces.get(chr))
            readlength = endpos - startpos
            # Read the sequence
            self.genomeobj.seek(startpos)
            sequence = self.genomeobj.read(readlength)
        else:
            sequence = ""
            if self.verbosity:
                print("WARNING: Check failed for "+chr+". Unable to retrieve sequence.")
        return sequence
