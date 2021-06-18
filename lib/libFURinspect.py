# FURcompare
# Tools to inspect the contents of the FUR database.

from lib import libFURdatabase

class inspect(libFURdatabase.furdbobj):
    """Inspection class which interacts with the FUR database to lookup and export specific information"""
    # Inherited object creation functions
    def __init__(self, SQLuser, SQLpass, SQLhost="localhost", SQLdb="FURdb", verbosity=0):
        """Create the object, set verbosity and connect it to the SQL database."""
        # Inherit the shared functions from a shared parent class
        super().__init__(SQLuser, SQLpass, SQLhost, SQLdb, verbosity)
    # Returns a single sequence for display or export
    def exportSequenceSingle(self, id=0, table="DeduplicatedContigs"):
        """Retrieve and return a single sequence"""
        Seq=""
        MySQLcursorObj = self.FURdb.cursor()
        MySQLcursorObj.execute("SELECT sequence FROM "+table+" WHERE id="+str(id))
        for (sequence) in MySQLcursorObj:
            Seq = sequence[0]
        return Seq
    # Returns which contigs relate to an annotation (and number of alignments if the file is passed)
    def annoContigs(self, id=0, table="DeduplicatedContigs"):
        """Returns the contigs related to an annotation"""
        MySQLcursorObj = self.FURdb.cursor()
        contiglist = []
        MySQLcursorObj.execute("SELECT id, start, end FROM "+table+" WHERE annotation="+str(id))
        for (id, start, end) in MySQLcursorObj:
            contiglist.append([id,start,end])
        return contiglist
    # Returns which annotation a contig belongs to.
    def contigAnno(self, id=0, table="DeduplicatedContigs"):
        """Returns the annotation related to an contig"""
        MySQLcursorObj = self.FURdb.cursor()
        MySQLcursorObj.execute("SELECT annotation FROM "+table+" WHERE id="+str(id))
        for (annotation) in MySQLcursorObj:
            anno = annotation[0]
        return anno
    # Returns information on an annotation
    def annoDetails(self, id=0):
        """Returns the database information on an annotation, or all annotations"""
        MySQLcursorObj = self.FURdb.cursor()
        if id=="ALL":
            # Iterate and return all annotations
            # Get all ID numbers:
            annoids = []
            MySQLcursorObj.execute("SELECT id FROM annotations")
            for id in MySQLcursorObj:
                annoids.append(id[0])
            # Add each entry into a list of lists
            anno=[]
            for id in annoids:
                MySQLcursorObj.execute("SELECT repName,chrName,alignStart,alignEnd,strand,score,matchStart,matchEnd FROM annotations WHERE id="+str(id))
                for (repName,chrName,alignStart,alignEnd,strand,score,matchStart,matchEnd) in MySQLcursorObj:
                    anno.append([id,repName,chrName,alignStart,alignEnd,strand,score,matchStart,matchEnd])
        else:
            # Return just the requested annotation
            MySQLcursorObj.execute("SELECT repName,chrName,alignStart,alignEnd,strand,score,matchStart,matchEnd FROM annotations WHERE id="+str(id))
            for (repName,chrName,alignStart,alignEnd,strand,score,matchStart,matchEnd) in MySQLcursorObj:
                anno = [id,repName,chrName,alignStart,alignEnd,strand,score,matchStart,matchEnd]
        return anno
    # ** NOTE: Function to return all information on a contig may also be useful (currently done in interface code)
    # Function to return a list of overlapping annotations (and by how much)
    # TODO: REWRITE - return a dictionary with number of overlapping bp sense/antisense.
    def overlappingAnnos(self):
        """Returns a list of overlapping annotations and by how many basepairs"""
        # Variables to return
        OverlappingResults = []
        # Get the database settings. NOTE: Could move database settings into shared parent object and call that function!
        MySQLcursorObj = self.FURdb.cursor()
        MySQLcursorObj2 = self.FURdb.cursor()
        MySQLcursorObj.execute("SELECT flankingsize,flankingoffset FROM info")
        for (flankingsize,flankingoffset) in MySQLcursorObj:
            regionsize = int(flankingsize)
            regionoffset = int(flankingoffset)
        RegionWithOffset = regionsize+regionoffset
        # Get the needed details of each annotation
        MySQLcursorObj.execute("SELECT id,chrName,alignStart,alignEnd,strand FROM annotations")
        for (Qid,QchrName,QalignStart,QalignEnd,Qstrand) in MySQLcursorObj:
            QStart1 = QalignStart-RegionWithOffset
            QEnd1 = QalignStart-regionoffset
            QStart2 = QalignEnd+regionoffset
            QEnd2 = QalignEnd+RegionWithOffset
            # For each entry compare regions with other annotations
            MySQLcursorObj2.execute("SELECT id,chrName,alignStart,alignEnd,strand FROM annotations WHERE NOT id="+str(Qid))
            for (id,chrName,alignStart,alignEnd,strand) in MySQLcursorObj2:
                if QchrName==chrName:   # Ignore annotations on different chromosomes
                    # Calculate the regions locations:
                    Start1 = alignStart-RegionWithOffset
                    End2 = alignEnd+RegionWithOffset
                    # Ignore annotations which are not close to each other:
                    if (Start1>QEnd2) or (End2<QStart1):
                        # These annotations are far enough apart there is no chance of overlapping
                        pass
                    else:
                        # These annotations are likely to overlap (depending on the offset value)
                        End1 = alignStart-regionoffset
                        Start2 = alignEnd+regionoffset
                        # Compare with the query annotation:
                        if (Start1>QStart1 and Start1<QEnd1) or (End1>QStart1 and End1<QEnd1):
                            # First region overlaps query first region
                            # TODO: Calculate the number of overlapping bp
                            OverlappingResults.append([id,1])
                        elif (Start1>QStart2 and Start1<QEnd2) or (End1>QStart2 and End1<QEnd2):
                            # First region overlaps query second region
                            OverlappingResults.append([id,1])
                        elif (Start2>QStart1 and Start2<QEnd1) or (End2>QStart1 and End2<QEnd1):
                            # Second region overlaps query first region
                            OverlappingResults.append([id,2])
                        elif (Start2>QStart1 and Start2<QEnd1) or (End2>QStart1 and End2<QEnd1):
                            # Second region overlaps query second region
                            OverlappingResults.append([id,2])
                        #print(str(Qid)+"-"+QchrName+":"+str(id)+chrName)
        return OverlappingResults
    def regionCount(self):
        """Counts the number of regions at each end of an annotation along with the largest size"""
        # Return id={SenseNum,SenseLargest,AntiNum,AntiLargest}
        table = "DeduplicatedContigs"
        regionInfo = {}
        MySQLcursorObj = self.FURdb.cursor()
        MySQLcursorObj2 = self.FURdb.cursor()
        MySQLcursorObj.execute("SELECT id,alignStart,alignEnd,strand FROM annotations")
        for (Aid,AalignStart,AalignEnd,Astrand) in MySQLcursorObj:
            senseCount = 0
            antiCount = 0
            senseLargest = 0
            antiLargest = 0
            MySQLcursorObj2.execute("SELECT id, start, end FROM "+table+" WHERE annotation="+str(Aid))
            for (id,start,end) in MySQLcursorObj2:
                # Check which list we belong to:
                if (int(start)<=int(AalignStart) and Astrand=="+") or (int(start)>int(AalignStart) and Astrand=="-"):
                    # Antisense (Technically this also includes regions inside the annotation but they should not exist)
                    antiCount = antiCount+1
                    size = int(end)-int(start)
                    if size>antiLargest:
                        antiLargest=size
                else:
                    # Sense
                    senseCount = senseCount+1
                    size = int(end)-int(start)
                    if size>senseLargest:
                        senseLargest=size
            regionInfo[int(Aid)] = [senseCount,senseLargest,antiCount,antiLargest]
        return regionInfo

    # Function to combine regionCount and overlap info? (Unsure)
