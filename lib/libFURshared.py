# libFURshared
# Code shared between multiple different parts of the program

# Function to write out a FASTA entry to a file object
def exportFASTAEntry(fileobj, ident, sequence):
	"""Writes a FASTA entry to a provided file object."""
	linelength = 80		# Set the line length (specification sets upper limit of 120 chars)
	# Write the identity line:
	fileobj.write(">"+ ident+"\n")
	# Break the sequence into lines of 80 chars and write out.
	Start = 0
	End = linelength
	while Start < len(sequence):
		fileobj.write(sequence[Start:End]+"\n")
		Start = Start+linelength
		End = End+linelength

###
### IMPORTANT NOTE: Following functions are also used in Annotation Utilities project
###

# Return the column number from a name in the header.
# Note: This is case sensitive. An advancement in future maybe to return a dictionary with all header columns.
def columnnum(header, name, default=-1):
    """Returns the column number matching the input string when provided with a tab separated header."""
    column = default
    count = 0
    for item in header.split("\t"):
        if item.strip() == name.strip():
            column = count
        else:
            count = count +1
    return column

# Function to detect file type
# Note: The DFAM and UCSC file endings are not standard, but added as an alternative way to manually identify a file.
def detectFileType(fileobj):
    type = None
    # Check for UCSC or DFAM headers
    header = fileobj.readline()
    start = header.split()[0].strip()
    # Check filetype extensions
    if fileobj.name[-3:].upper()=="BED":
        type = "BED"
    elif fileobj.name[-3:].upper()=="GTF" or fileobj.name[-3].upper()=="GFF":
        type = "GTF"
    elif fileobj.name[-3:].upper()=="FAM": # or fileobj.name[-4:].upper()=="HITS": # Uncomment to allow DFAM .hits extension (not used currently as may not be unique to DFAM)
        type = "DFAM"
    elif fileobj.name[-3:].upper()=="CSC":
        type = "UCSC"
    # If filetype extensions unclear check first line.
    elif start.upper() in ["BIN","#BIN"]:
        type = "UCSC"
    elif start.upper() in ["SEQUENCE","#SEQUENCE"]:
        type = "DFAM"
    fileobj.seek(0)     # Return file pointer to the start
    return type

# Creates an object for an entry in an annotation file and applies basic conversions to make the data consistant
# INPUT: Line from annotation file, the input file format and the header line where available.
# NOTE: Scores are stored as integers. This could be changed to a float for greater accuracy. (Supported by DFAM and GTF)
class Annotation(object):
    """Parses an annotation line and stores key values in a common structure"""
    def __init__(self, line, type, header="", NullString=".", NullInt=-1):
        self.line = line
        self.type = type
        self.header = header
        self.error = None
        self.NullString = NullString
        self.NullInt = NullInt
        if type=="BED":
            self.parseBed()
        elif type=="UCSC":
            self.parseUcsc()
        elif type=="DFAM":
            self.parseDfam()
        elif type=="GTF":
            self.parseGtf()
        else:
            self.error = "Type unsupported "+self.type
    def parseBed(self):
        fields = self.line.split('\t')
        # Variables for external use:
        self.repName = fields[3].strip()
        self.repSize = self.NullInt
        self.chrName = fields[0].strip()
        self.chrSize = self.NullInt
        self.score = int(fields[4])
        self.strand = fields[5].strip()
        self.alignStart = int(fields[1])
        self.alignEnd = int(fields[2])
        self.matchStart = self.NullInt
        self.matchEnd = self.NullInt
        self.repID = self.NullString
    def parseUcsc(self):
        fields = self.line.split('\t')
        # Conversions
        if fields[columnnum(self.header, "strand")] == "-":
            repstart = int(fields[columnnum(self.header, "repLeft")])
            repsize = int(fields[columnnum(self.header, "repEnd")])-int(fields[columnnum(self.header, "repStart")])
        else:
            repstart = int(fields[columnnum(self.header, "repStart")])
            repsize = int(fields[columnnum(self.header, "repEnd")])-int(fields[columnnum(self.header, "repLeft")])
        chrsize = int(fields[columnnum(self.header, "genoEnd")])-int(fields[columnnum(self.header, "genoLeft")])
        # Variables for external use:
        self.repName = fields[columnnum(self.header, "repName")].strip()
        self.repSize = repsize
        self.chrName = fields[columnnum(self.header, "genoName")].strip()
        self.chrSize = chrsize
        self.score = int(fields[columnnum(self.header, "swScore")])
        self.strand = fields[columnnum(self.header, "strand")].strip()
        self.alignStart = int(fields[columnnum(self.header, "genoStart")])
        self.alignEnd = int(fields[columnnum(self.header, "genoEnd")])
        self.matchStart = repstart
        self.matchEnd = int(fields[columnnum(self.header, "repEnd")])
        self.repID = self.NullString
    def parseDfam(self):
        fields = self.line.split('\t')
        # Conversions
        if fields[columnnum(self.header, "strand",8)] == "-":
            start = fields[columnnum(self.header, "alignment end",10)]
            end = fields[columnnum(self.header, "alignment start",9)]
        else:
            start = fields[columnnum(self.header, "alignment start",9)]
            end = fields[columnnum(self.header, "alignment end",10)]
        # Variables for external use:
        self.repName = fields[columnnum(self.header, "model name",2)].strip()
        self.repSize = int(fields[columnnum(self.header, "hmm length",7)])
        self.chrName = fields[columnnum(self.header, "#sequence name",0)].strip()
        self.chrSize = int(fields[columnnum(self.header, "sequence length",13)])
        self.score = int(float(fields[columnnum(self.header, "bit score",3)]))
        self.strand = fields[columnnum(self.header, "strand",8)].strip()
        self.alignStart = int(start)
        self.alignEnd = int(end)
        self.matchStart = int(fields[columnnum(self.header, "hmm start",6)])
        self.matchEnd = int(fields[columnnum(self.header, "hmm end",7)])
        self.repID = self.NullString
    def parseGtf(self):
        fields = self.line.split('\t')
        # Get the name from the other attributes column
        # If following the offical specification the first 'other' attribute should be gene_id
        # NOTE: Gene_id should be a unique id. Using this for the repeat name may cause issues! Therefore its use should be documented.
        # TODO: Check all attributes looking for a repName key before resorting to the first value as a last resort.
        otherAttributes = fields[8]
        firstAttribute = otherAttributes.split(';')[0]
        firstAttribute = firstAttribute.replace('='," ")  # Change = to space if = is used
        repID = firstAttribute.split(' ')[-1].strip()
        repID = repID.replace('"',"")                   # Remove quotes if used
        repID = repID.replace("'","")                   # Remove quotes if used
        # Variables for external use:
        # Uncomment/comment relevant lines depending on which column to use for the repeat name.
        self.repName = fields[2].strip()                  # Feature column as repeat name
        self.repSize = self.NullInt
        self.chrName = fields[0].strip()
        self.chrSize = self.NullInt
        if fields[5]==".":                                # Missing values are replaced with a period
            self.score = self.NullInt
        else:
            self.score = int(fields[5])
        self.strand = fields[6].strip()
        self.alignStart = int(fields[3])
        self.alignEnd = int(fields[4])
        self.matchStart = self.NullInt
        self.matchEnd = self.NullInt
        self.repID = repID                              # Gene name used as a repeat ID
    # Conversion functions specific to certain file types implemented here
    # incase other file type are added later which share these functions
    def getAlignStart53(self):
        if self.strand == "-":
            start = self.alignEnd
        else:
            start = self.alignStart
        return start
    def getAlignEnd53(self):
        if self.strand == "-":
            end = self.alignStart
        else:
            end = self.alignEnd
        return end
    def getChrLeft(self):
        if self.chrSize != self.NullInt:            # Only calculate if chrSize has been parsed
            chrLeft = 0-(self.chrSize-self.alignEnd)
        else:
            chrLeft = self.NullInt
        return chrLeft
    def getMatchLeft53(self):
        if self.type != "BED" and self.type != "GTF":   # BED and GTF formats don't store the required values
            if self.strand == "-":
                matchLeft = self.matchStart
            else:
                matchLeft = 0-(self.repSize-self.matchEnd)
        else:
            matchLeft = self.NullInt
        return matchLeft
    def getMatchStart53(self):
        if self.type != "BED" and self.type != "GTF":
            if self.strand == "-":
                matchStart = 0-(self.repSize-self.matchEnd)
            else:
                matchStart = self.matchStart
        else:
            matchStart = self.NullInt
        return matchStart
