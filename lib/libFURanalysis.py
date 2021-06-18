# libFURanalysis
#
# Contains functions and classes related to processing and exporting
# information from the FUR database.

from lib import libFURdatabase
from lib import libFURshared
import operator

class analysis(libFURdatabase.furdbobj):
    """Analysis class which interacts with the FUR database to export and lookup information"""
    # Inherited object creation functions
    def __init__(self, SQLuser, SQLpass, SQLhost="localhost", SQLdb="FURdb", verbosity=0):
        """Create the object, set verbosity and connect it to the SQL database."""
        # Inherit the shared functions from a shared parent class
        super().__init__(SQLuser, SQLpass, SQLhost, SQLdb, verbosity)
        self.setTableVar()
        self.calcContigEnds()   # These values are needed frequently so calculate once on creation
    ### Functions relating to the setting of commonly used object variables which are unlikely to change between object calls
    def setTableVar(self, table="DeduplicatedContigs"):
        """Set the table to use for analysis"""
        self.table = table
    # Returns two lists which can be used to identify if a contig is at the sense or antisense end of an annotation
    def calcContigEnds(self):
        """Returns a list of contigs at the sense end and a list of those at the antisense end of their annotations"""
        senseList = []
        antisenseList = []
        annotationdict = {}
        MySQLcursorObj = self.FURdb.cursor()
        # Construct a dictionary of annotation strands and start positions
        MySQLcursorObj.execute("SELECT id, alignStart, strand FROM annotations")
        for (id, alignStart, strand) in MySQLcursorObj:
            annotationdict[id]=[int(alignStart),strand]
        # Get the contig ids and positions and assign them to one of the two lists
        MySQLcursorObj.execute("SELECT id, annotation, start FROM "+self.table)
        for (id, annotation, start) in MySQLcursorObj:
            if isSense(annotationdict.get(annotation)[0],annotationdict.get(annotation)[1],int(start)):
                senseList = senseList+[id]
            else:
                antisenseList = antisenseList+[id]
        self.senseContigIDs = senseList
        self.antisenseContigIDs = antisenseList
    ### Functions related to the exporting of sequence information.
    # Internal function used by exportSequenceAdv.
    # INPUT: File object, ContigList[id,sequence,sequence length], convert to complementary strand, largest contig only, fixed contig size
    def exportEnd(self, fileoutobj, contiglist, complementary=0, fixed=0):
        """Internal use, processes one end of the annotation contigs, checking sequence size and if it needs converting to the complementary strand"""
        # Iterate through each contig, making any adjustments and exporting:
        exportCount = 0
        for item in contiglist:
            # Check orientation
            if complementary>0:
                sequence = swapStrand(item[1])
            else:
                sequence = item[1]
            # Check sequence is long enough
            if len(sequence)>=fixed:
                if fixed>0:
                    sequence = sequence[:fixed]  # Uses the first part of the sequence (after orientation so position relative to annotation is similar where possible)
                # Write out to file
                libFURshared.exportFASTAEntry(fileoutobj, str(item[0]), sequence)
                exportCount = exportCount+1
        return exportCount  # Return the number of sequences exported for reporting back to the user (via calling function)
    # Advanced export function, required to produce the files to align with.
    # INPUT: Orientation (5-3/Genome/Sense/Antisense), End (Both, Sense, Antisense), Largestonly (Single largest contig on/off), Fixed (Set exact size for exported contigs, 0=off)
    # TODO: Report number of annotations (/regions) exported to terminal prompt
    def exportSequencesAdv(self, fileoutobj, orientation="G", end="B", equal=0, largestonly=0, fixed=0, closest=0):
        """Advanced export of the sequences within a table."""
        # Construct a list of annotations referenced in the table
        MySQLcursorObj = self.FURdb.cursor()
        annotations=[]
        MySQLcursorObj.execute("SELECT DISTINCT annotation FROM "+self.table)
        for (annotation) in MySQLcursorObj:
            annotations=annotations+[annotation[0]]
        # Iterate through each annotation exporting the contigs
        self.excludedAnnos = []
        for item in annotations:
            # Check which contigs are sense and antisense and get the information from the database
            senseContigs=[]
            antisenseContigs=[]
            MySQLcursorObj.execute("SELECT id, sequence, start FROM "+self.table+" WHERE annotation="+str(item))
            for (id, sequence, start) in MySQLcursorObj:
                if id in self.senseContigIDs:
                    senseContigs=senseContigs+[[id,sequence,len(sequence), start]]
                else:
                    antisenseContigs=antisenseContigs+[[id,sequence,len(sequence), start]]
            # Set complementary value and annotation position
            alignStart = 0
            MySQLcursorObj.execute("SELECT alignStart, strand FROM annotations WHERE id="+str(item))
            for (alignStart, strand) in MySQLcursorObj:
                if closest:
                    alignStart = int(alignStart)
                strand = strand[0]
            antisenseComplementary=0
            senseComplementary=0
            # - Sense promoter (read through)
            if orientation=="S" and strand=="-":
                antisenseComplementary=1
                senseComplementary=1
            # - Antisense promoter (read through)
            elif orientation=="A" and strand=="+":
                antisenseComplementary=1
                senseComplementary=1
            # - Bidirectional promoter
            elif orientation=="B":
                # Only swap to the complementary strand either the sense or antisense regions
                if strand=="+":
                    antisenseComplementary=1
                elif strand=="-":
                    senseComplementary=1
            # Trim the contig lists to just the largest:
            if largestonly>0:
                if senseContigs:
                    senseContigs=[max(senseContigs, key=operator.itemgetter(2))]   # Return just the largest contig in the list
                if antisenseContigs:
                    antisenseContigs=[max(antisenseContigs, key=operator.itemgetter(2))]   # Return just the largest contig in the list
            # Trim the contig lists to just the closest:
            elif closest>0:
                # Loop through the list and return the closest contig only
                ClosestSenseContig = []
                ClosestAntisenseContig = []
                distance = 10000000000  # Arbitary high starting value (probably better way to do this)
                for contig in senseContigs:
                    # Calc difference:
                    difference = max([contig[3],alignStart])-min([contig[3],alignStart])
                    if difference<distance:
                        ClosestSenseContig=[contig]
                        distance = difference
                distance = 10000000000  # Arbitary high starting value (probably better way to do this)
                for contig in antisenseContigs:
                    # Calc difference:
                    difference = max([contig[3],alignStart])-min([contig[3],alignStart])
                    if difference<distance:
                        ClosestAntisenseContig=[contig]
                        distance = difference
                senseContigs = ClosestSenseContig
                antisenseContigs = ClosestAntisenseContig
            # Set fixed value based on equal property
            # CHANGE: Currently equal also combines largest. Needs to change to iterate through each region from largest to smallest
            if equal>0:
                if len(senseContigs)>1 or len(antisenseContigs)>1:
                    # Equal option is being used with multiple contigs present
                    # If fixed length is used remove any contigs under the fixed value
                    senseContigsNew = []
                    antisenseContigsNew = []
                    for contig in senseContigs:
                        if contig[2]>=fixed:
                            senseContigsNew.append(contig)
                    for contig in antisenseContigs:
                        if contig[2]>=fixed:
                            antisenseContigsNew.append(contig)
                    senseContigs = senseContigsNew
                    antisenseContigs = antisenseContigsNew
                    # Sort list by size:
                    senseContigs = sorted(senseContigs, key=operator.itemgetter(2),reverse=True)
                    antisenseContigs = sorted(antisenseContigs, key=operator.itemgetter(2),reverse=True)
                    # Trim the lists to contain the same number of unique regions
                    numContigs=min(len(senseContigs),len(antisenseContigs))
                    senseContigs = senseContigs[:numContigs]
                    antisenseContigs = antisenseContigs[:numContigs]
                    ## By this point the lists should be of equal length and contain only valid contigs
                elif len(senseContigs)==0 or len(antisenseContigs)==0:
                    # If one end has no unique regions and equal setting is used, set both ends to empty lists
                    senseContigs = []
                    antisenseContigs = []
            if fixed==0 and equal>0:
                # Equal ends required, but without a fixed length.
                # Loop through each item setting the fixed value accordingly
                if len(senseContigs)==0:    # Note, assuming antisenseContig list is the same length by this point
                    # Keep a record of the annotations with no annotations
                    self.excludedAnnos.append(item)
                else:
                    while senseContigs:
                        currentSense = senseContigs.pop(0)
                        currentAnti = antisenseContigs.pop(0)
                        # Set the fixed length value accordingly:
                        fixedval=min(currentSense[2],currentAnti[2])
                        aCount = self.exportEnd(fileoutobj, [currentSense], senseComplementary, fixedval)
                        sCount = self.exportEnd(fileoutobj, [currentAnti], antisenseComplementary, fixedval)
                        if aCount==0 and sCount==0:
                            # This shouldn't occur (but here just in case)
                            self.excludedAnnos.append(item)
            else:
                # Using a fixed value, or returning unequal length results
                aCount=0
                sCount=0
                # Process each set
                if end!="A":
                    aCount = self.exportEnd(fileoutobj, senseContigs, senseComplementary, fixed)
                if end!="S":
                    sCount = self.exportEnd(fileoutobj, antisenseContigs, antisenseComplementary, fixed)
                # Record which annotations failed to meet the export criteria
                if aCount==0 and sCount==0:
                    self.excludedAnnos.append(item)

    # Function to compare the individual contig counts to the relevant annotations
    # INPUT: Dictionary of contig alignments
    # OUTPUT: Two dictionaries (sense/antisense) referenced by annotation with: num aligns and number of contigs with hits
    def countAnnoAligns(self, conAligns):
        """Creates a dictionary of sense/antisense counts from an individual contig count"""
        MySQLcursorObj = self.FURdb.cursor()
        senseAnnoAligns = {}
        antiAnnoAligns = {}
        for contig in conAligns:
            annotation = None
            MySQLcursorObj.execute("SELECT annotation FROM "+self.table+" WHERE id="+str(contig))
            for (annotation) in MySQLcursorObj:
                anno = annotation[0]
            if int(contig) in self.senseContigIDs and anno in senseAnnoAligns:
                # Update sense dict
                senseAnnoAligns[anno] = [senseAnnoAligns.get(anno)[0]+conAligns.get(contig),senseAnnoAligns.get(anno)[1]+1]
            elif int(contig) in self.senseContigIDs and anno not in senseAnnoAligns:
                # Create new sense dict entry
                senseAnnoAligns[anno] = [conAligns.get(contig),1]
            elif int(contig) in self.antisenseContigIDs and anno not in antiAnnoAligns:
                # Update antiAnnoAligns entry
                antiAnnoAligns[anno] = [conAligns.get(contig),1]
            elif int(contig) in self.antisenseContigIDs and anno in antiAnnoAligns:
                # Create antiAnnoAligns entry
                antiAnnoAligns[anno] = [antiAnnoAligns.get(anno)[0]+conAligns.get(contig),antiAnnoAligns.get(anno)[1]+1]
            else:
                # Contig not in database:
                if self.verbosity:
                    print("ERROR: Contig "+str(contig)+" not found in table "+self.table+". Check correct table and database are being used.")
        return senseAnnoAligns, antiAnnoAligns
    # Function to return information on the annotations, which can be combined into producing a report
    def getAnnoTable(self):
        """Export the annotation information as a dictionary"""
        annoinfodict = {}
        MySQLcursorObj = self.FURdb.cursor()
        MySQLcursorObj.execute("SELECT id, repName, chrName, alignStart, alignEnd, strand, score, matchStart, matchEnd FROM annotations")
        for (id, repName, chrName, alignStart, alignEnd, strand, score, matchStart, matchEnd) in MySQLcursorObj:
            annoinfodict[id]=[repName, chrName, alignStart, alignEnd, strand, score, matchStart, matchEnd]
        return annoinfodict
    # Get the required information for normalisation of each annotation:
    def getRegionSizes(self):
        """Calculate the number of bases and contigs each annotation has, per end."""
        regionSenseSize = {}
        regionAntiSize = {}
        MySQLcursorObj = self.FURdb.cursor()
        MySQLcursorObj.execute("SELECT id, annotation, sequence FROM "+self.table)
        for (id, annotation, sequence) in MySQLcursorObj:
            if id in self.senseContigIDs:
                if annotation in regionSenseSize:
                    size = regionSenseSize.get(annotation)[0]+len(sequence)
                    contigs = regionSenseSize.get(annotation)[1]+1
                    regionSenseSize[annotation] = [size,contigs]
                else:
                    regionSenseSize[annotation] = [len(sequence),1]
            else:
                if annotation in regionAntiSize:
                    size = regionAntiSize.get(annotation)[0]+len(sequence)
                    contigs = regionAntiSize.get(annotation)[1]+1
                    regionAntiSize[annotation] = [size,contigs]
                else:
                    regionAntiSize[annotation] = [len(sequence),1]
        return regionSenseSize, regionAntiSize
    # Returns information on the flanking positions
    def getFlankingSize(self, flankingsize=5000):
        """Returns the size of the flanking regions"""
        MySQLcursorObj = self.FURdb.cursor()
        MySQLcursorObj.execute("SELECT flankingsize FROM info")
        for (flankingsize) in MySQLcursorObj:
            flankingsize=int(flankingsize[0])
        return flankingsize
    def getFlankingOffset(self, flankingoffset=0):
        """Returns the offset used when importing the flanking regions"""
        MySQLcursorObj = self.FURdb.cursor()
        MySQLcursorObj.execute("SELECT flankingoffset FROM info")
        for (flankingoffset) in MySQLcursorObj:
            flankingoffset=int(flankingoffset[0])
        return flankingoffset
    # TODO: Add function which will determine which annotations meet/don't meet analysis criteria



### Class for the alignment file (SAM)
class alignfile(object):
    """An object for alignment files, storing related functions and variables"""
    def __init__(self, analysisobj, fileobj, quality=40, incAll=0, type="SAM"):
        """Create the object"""
        self.analysisobj = analysisobj
        self.fileobj = fileobj
        self.filetype = type
        self.setAnnoQualityVar(quality)
        self.fileDataStart()
        self.collectDatabaseInfo()
        self.processAlignments()
        self.createAnnoDataObjs(incAll)
    # Set variables
    def setAnnoQualityVar(self, quality=40):
        """Set minimum annotation quality threshold"""
        self.annoquality = quality
    # Get information from the database and process the file
    def collectDatabaseInfo(self):
        """Get the general annotation information needed to build a report from the database"""
        self.annoinfo = self.analysisobj.getAnnoTable()               # Collect detailed information on all annotations in the datbase
        self.sensesize, self.antisize = self.analysisobj.getRegionSizes()  # Size of the flanking regions (after deduplication)
    # Alignment file start position
    def fileDataStart(self):
        """Returns the start position of the data."""
        self.fileobj.seek(0)
        if self.filetype=="SAM":
            # SAM files contain header information on lines which start with the @ symbol
            line = self.fileobj.readline()
            while line[0]=="@":
                line = self.fileobj.readline()
            position = self.fileobj.tell()-len(line)
        else:
            # Type unknown - so look for common comment line indicators
            line = self.fileobj.readline()
            while line[0]=="@" or line[0]=="#":
                line = self.fileobj.readline()
            position = self.fileobj.readline()-len(line)
        self.fileobj.seek(0)
        self.posDataStart = position
    # Function which processes an alignment file and returns the count numbers
    # OUTPUT: Dictionary of contig alignment counts.
    def processAlignments(self):
        """Counts the number of alignments within an alignment file."""
        aligncount = {}
        # Move to the start of the alignments
        self.fileobj.seek(self.posDataStart)
        # Produce a count for each contig
        totalAlignments = 0
        line = self.fileobj.readline()
        while line:
            align = alignment(line, self.filetype)
            if align.quality>self.annoquality:
                if align.conName not in aligncount:
                    aligncount[align.conName]=1
                else:
                    aligncount[align.conName]=aligncount.get(align.conName)+1
                totalAlignments = totalAlignments+1
            line = self.fileobj.readline()
        self.contigAlignments = aligncount
        self.numTotalAlignments = totalAlignments
        # Run the contig alignments through the database to group by annotation
        sensealigns, antialigns = self.analysisobj.countAnnoAligns(self.contigAlignments)
        self.annoAlignmentsSense = sensealigns
        self.annoAlignmentsAnti = antialigns
    # Create a dictionary of annotation objects with all the information combined
    def createAnnoDataObjs(self, incAll=0):
        """Creates a dictionary populated with objects which contain all available information on each annotation"""
        # Compile a list of annotations to process (all or all which have matched alignments)
        processlist=[]
        if incAll>0:
            for item in self.annoinfo:
                processlist.append(item)
        else:
            for item in self.annoAlignmentsSense:
                processlist.append(item)
            for item in self.annoAlignmentsAnti:
                if item not in processlist:
                    processlist.append(item)
        # Create objects and add the annotation information
        self.annoDataList = {}
        for item in processlist:
            annodataobj = annotationData(item, self.annoinfo.get(item), self.sensesize.get(item), self.antisize.get(item))
            annodataobj.calcFlankingPositions(self.analysisobj.getFlankingSize(), self.analysisobj.getFlankingOffset())
            if item in self.annoAlignmentsSense:
                annodataobj.setSenseMatches(self.annoAlignmentsSense.get(item))
            if item in self.annoAlignmentsAnti:
                annodataobj.setAntiMatches(self.annoAlignmentsAnti.get(item))
            annodataobj.setRPKM(self.numTotalAlignments)
            self.annoDataList[item]=annodataobj
    def getMultiMatching(self):
        # Check the file for reads with multiple alignments (WIP) - Deduplication using SAM file itself.
        # Varies depending on software:
        # - Extreamly low quality score.
        # - Multiple entries of the QNAME (read id)
        # - Use of the secondary alignment flag (256) or supplementary alignment (2048)
        # -- Note: Flags can be combined so 256-511 and 2048+
        # - Optional tag NH:<int> (number of alignments)
        pass

### Report recreating functions utilising the object list approach

# Export count for each individual contig
def reportContigCount(alignfileobj, fileoutobj, header=0, sampleid=""):
    """Export the contig alignments as a count file"""
    # Get information from object:
    contigobjlist = alignfileobj.contigAlignments
    # Write header
    if header>0:
        headline = "id\t"+sampleid+"\n"
        fileoutobj.write(headline)
    # Write content
    for item in contigobjlist:
        contigcount = contigobjlist.get(item)
        fileoutobj.write(str(item)+"\t"+str(contigcount)+"\n")

# Export count files for the sense or antisense ends. Or a combined count.
# Setting an input to None will result in no output for that file.
def reportCount(alignfileobj, sensefile, antifile, totalfile, header=0, sampleid=""):
    """Export the alignments as count files"""
    # Get information from object:
    annoobjlist = alignfileobj.annoDataList
    # Write header
    if header>0:
        headline = "id\t"+sampleid
        if sensefile:
            sensefile.write(headline+"_S\n")
        if antifile:
            antifile.write(headline+"_A\n")
        if totalfile:
            totalfile.write(headline+"_B\n")
    # Write content
    for item in annoobjlist:
        annoobj = annoobjlist.get(item)
        if annoobj.senseNumMatches>0 and sensefile:
            sensefile.write(str(item)+"\t"+str(annoobj.senseNumMatches)+"\n")
        if annoobj.antiNumMatches>0 and antifile:
            antifile.write(str(item)+"\t"+str(annoobj.antiNumMatches)+"\n")
        if totalfile:
            totalfile.write(str(item)+"\t"+str(annoobj.senseNumMatches+annoobj.antiNumMatches)+"\n")

# Export all information on each annotation as a large tab seperated file
def reportAll(alignfileobj, fileoutobj, header=0):
    """Export all information on an annotation"""
    # Get information from object:
    annoobjlist = alignfileobj.annoDataList
    # Write header
    if header>0:
        fileoutobj.write("Chr\tSoftware\tItem\tStart\tEnd\tScore\tStrand\tFrame\tID\trepType\tMatchStart\tMatchEnd\tS_Start\tS_End\tS_SizeBP\tS_Contigs\tS_Matches\tS_MatchedContigs\tS_RPKM\tA_Start\tA_End\tA_SizeBP\tA_Contigs\tA_Matches\tA_MatchedContigs\tA_RPKM\n")
    # Compile the line:
    for item in annoobjlist:
        # Annotation information - First 8 columns follow GTF column order to allow for easy conversion using annotation utilties
        annoobj = annoobjlist.get(item)
        annotemplate = "{}\tFURdb\tAnnotation\t{}\t{}\t{}\t{}\t.\t{}\t{}\t{}\t{}\t"
        annostr = annotemplate.format(annoobj.chrName,annoobj.alignStart,annoobj.alignEnd,annoobj.annoScore,annoobj.strand,annoobj.id,annoobj.repName,annoobj.matchStart,annoobj.matchEnd)
        # Flanking region information
        sensetemplate = "{}\t{}\t{}\t{}\t{}\t{}\t{}\t"
        sensestr = sensetemplate.format(annoobj.senseStart,annoobj.senseEnd,annoobj.senseSizeBP,annoobj.senseSizeContigs,annoobj.senseNumMatches,annoobj.senseNumMatchedContigs,annoobj.senseRPKM)
        antitemplate = "{}\t{}\t{}\t{}\t{}\t{}\t{}\n"
        antistr = antitemplate.format(annoobj.antiStart,annoobj.antiEnd,annoobj.antiSizeBP,annoobj.antiSizeContigs,annoobj.antiNumMatches,annoobj.antiNumMatchedContigs,annoobj.antiRPKM)
        fileoutobj.write(annostr+sensestr+antistr)

# Export the annotation information in a GTF compatible format (either per annotation or per flanking region)
def reportGTF(alignfileobj, fileoutobj, regions=0, header=0):
    """Export information in GTF format"""
    # Get information from object:
    annoobjlist = alignfileobj.annoDataList
    # Write header
    if header>0:
        gtfhead="Chr\tSoftware\tItem\tStart\tEnd\tScore\tStrand\tFrame\tOther attributes\n"
        fileoutobj.write(gtfhead)
    # Compile an entry per flanking region or annotation
    if regions==0:
        gtftemplate="{}\tFURdb\tAnnotation\t{}\t{}\t{}\t{}\t.\t"
        gtfextratemplate="FURid={};repType={};senseCount={};antisenseCount={};senseRPKM={};antiRPKM={}\n"
    else:
        gtftemplate="{}\tFURdb\tFlankingRegion\t{}\t{}\t{}\t{}\t.\t"
        gtfextratemplate="FURid={};repType={};RPKM={}\n"
    for item in annoobjlist:
        annoobj = annoobjlist.get(item)
        if regions==0:
            score = annoobj.senseNumMatches-annoobj.antiNumMatches
            gtfstr=gtftemplate.format(annoobj.chrName,annoobj.alignStart,annoobj.alignEnd,score,annoobj.strand)
            gtfextrastr=gtfextratemplate.format(annoobj.id,annoobj.repName,annoobj.senseNumMatches,annoobj.antiNumMatches,annoobj.senseRPKM,annoobj.antiRPKM)
            fileoutobj.write(gtfstr+gtfextrastr)
        else:
            Sgtfstr=gtftemplate.format(annoobj.chrName,annoobj.senseStart,annoobj.senseEnd,annoobj.senseNumMatches,annoobj.strand)
            Sgtfextrastr=gtfextratemplate.format(annoobj.id,annoobj.repName,annoobj.senseRPKM)
            fileoutobj.write(Sgtfstr+Sgtfextrastr)
            Agtfstr=gtftemplate.format(annoobj.chrName,annoobj.antiStart,annoobj.antiEnd,annoobj.antiNumMatches,annoobj.strand)
            Agtfextrastr=gtfextratemplate.format(annoobj.id,annoobj.repName,annoobj.antiRPKM)
            fileoutobj.write(Agtfstr+Agtfextrastr)

### Functions for normalisation

# Calculate RPKM (Reads Per Kilobase = Region Reads/regionsize(kb); RPKM = Reads Per Kilobase / (total reads/1000000))
def calcRPKM(reads, totalreads, regionsize):
    """Calculate the RPKM value"""
    if regionsize>0 and totalreads>0:
        rpk = reads/(regionsize/1000)
        rpkm = rpk/(totalreads/1000000)
    else:
        rpkm=0
    return rpkm

# Check which end of the annotation a contig is.
# INPUT: Annotation start position, strand and the contig start position.
# OUTPUT: Returns true (1) if the contig is at the sense end of the annotation
def isSense(annostart, strand, constart):
    """Checks if a contig starts at the sense end of an annotation"""
    Sense = None
    if strand == "+" and constart>annostart:
        Sense=1
    elif strand == "-" and constart<annostart:
        Sense=1
    return Sense

# Returns the complementary strand of a given sequence (preserving case)
# INPUT: sequence
# OUTPUT: complementary sequence
def swapStrand(sequence):
	"""Converts the sequence order and bases to reflect the complementary strand."""
	# + strand 5' to 3' (default) - ASP on the + strand will transcript the - strand (hence the need for this function)
	# Produce complementary bases:
	newseq = ""
	for i in sequence:
		if i=='a':
			newseq+='t'
		elif i=='t':
			newseq+='a'
		elif i=='g':
			newseq+='c'
		elif i=='c':
			newseq+='g'
		elif i=='A':
			newseq+='T'
		elif i=='T':
			newseq+='A'
		elif i=='G':
			newseq+='C'
		elif i=='C':
			newseq+='G'
		else:
			newseq+=i
	sequence=newseq
	# Reverse sequence:
	return sequence[::-1]

### Simple classes for organising data

# Separate information relating to an annotation
class annotationData(object):
    """Processed annotation data"""
    def __init__(self, id, annodata, sensesize, antisize):
        """Setup the variables for data present in every annotation"""
        # Annotation information
        self.id = id
        self.repName = annodata[0]
        self.chrName = annodata[1]
        self.alignStart = annodata[2]
        self.alignEnd = annodata[3]
        self.strand = annodata[4]
        self.annoScore = annodata[5]
        self.matchStart = annodata[6]   # Could be set to None
        self.matchEnd = annodata[7]     # Could be set to None
        if self.matchStart and self.matchEnd:
            self.matchSize = self.matchEnd-self.matchStart
        else:
            self.matchSize = None
        # Variables on the size of the flanking regions
        if sensesize:
            self.senseSizeBP = sensesize[0]
            self.senseSizeContigs = sensesize[1]
        else:
            self.senseSizeBP = 0
            self.senseSizeContigs = 0
        if antisize:
            self.antiSizeBP = antisize[0]
            self.antiSizeContigs = antisize[1]
        else:
            self.antiSizeBP = 0
            self.antiSizeContigs = 0
        # Variables for dealing with alignments:
        self.senseNumMatches = 0
        self.senseNumMatchedContigs = 0
        self.antiNumMatches = 0
        self.antiNumMatchedContigs = 0
        self.senseRPKM = 0
        self.antiRPKM = 0
        # Flanking start and end positions
        self.senseStart = 0
        self.senseEnd = 0
        self.antiEnd = 0
        self.antiStart = 0
    def calcFlankingPositions(self, flankingsize, flankingoffset):
        """Calculate the positions of the flanking regions"""
        if self.strand=="+":
            # Sense end after, antisense end before
            self.senseStart = self.alignEnd+flankingoffset
            self.senseEnd = self.senseStart+flankingsize
            self.antiEnd = self.alignStart-flankingoffset
            self.antiStart = self.antiEnd-flankingsize
        else:
            # Sense end before, antisense end after
            self.senseEnd = self.alignStart-flankingoffset
            self.senseStart = self.senseEnd-flankingsize
            self.antiStart = self.alignEnd+flankingoffset
            self.antiEnd = self.antiStart+flankingsize
    def setSenseMatches(self, senseAligns):
        """Set the values for the number of matches at the sense end"""
        self.senseNumMatches = senseAligns[0]
        self.senseNumMatchedContigs = senseAligns[1]
    def setAntiMatches(self, antiAligns):
        """Set the values for the number of matches at the antisense end"""
        self.antiNumMatches = antiAligns[0]
        self.antiNumMatchedContigs = antiAligns[1]
    def setRPKM(self, totalAlignments):
        """Set the RPKM values for the annotation"""
        self.senseRPKM = calcRPKM(self.senseNumMatches, totalAlignments, self.senseSizeBP)
        self.antiRPKM = calcRPKM(self.antiNumMatches, totalAlignments, self.antiSizeBP)

# Parse an entry from an alignment file (ie. .SAM)
class alignment(object):
    """Align file object for parsing alignment files."""
    def __init__(self, line, type="SAM"):
        self.line = line
        if type=="SAM":
            self.parseSAM()
    def parseSAM(self):
        entry = self.line.split('\t')
        self.conName = entry[2]     # Name of the matching contig
        self.quality = int(entry[4])     # Alignment quality score
