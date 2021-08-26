# Code to implement the functionality of the connect to database ui

from ui.startscreen import Ui_Connect
from ui.SetupDB import Ui_ConfigureDB
from ui.MainView import Ui_MainWindow
from ui.FURanno import Ui_Annotation
from ui.FURcontig import Ui_Contig
from ui.AnalysisCheck import Ui_AnalysisCheck
from lib import libFURdatabase
from lib import libFURinspect
from lib import libFURshared
from lib import libFURanalysis

from PyQt5 import QtCore, QtGui, QtWidgets
import subprocess
import os

## Database connection screen
class ConnectDB(QtWidgets.QWidget):
    """Connect to Database UI functions"""

    def __init__(self):
        super().__init__()
        # Populate QWidget with UI design
        self.connect = Ui_Connect()
        self.connect.setupUi(self)
        # Connect buttons (signals)
        self.connect.LoadButton.clicked.connect(self.connectDB)
        self.connect.CreateButton.clicked.connect(self.newDB)

        self.connect.UseSQLiteradio.toggled.connect(self.radioFunction)
        self.connect.UseSQLradio.toggled.connect(self.radioFunction)

    # Functions to control the UI behaviour
    def radioFunction(self,option):
        if self.connect.UseSQLradio.isChecked()==True:
            self.connect.SQLServerEntry.setEnabled(True)
            self.connect.SQLUsernameEntry.setEnabled(True)
            self.connect.SQLPasswordEntry.setEnabled(True)
        else:
            self.connect.SQLServerEntry.setEnabled(False)
            self.connect.SQLUsernameEntry.setEnabled(False)
            self.connect.SQLPasswordEntry.setEnabled(False)

    # Functions to perform tasks
    def connectDB(self):
        # Get the variables from the ui
        database = self.connect.DatabaseNameEntry.text()
        if self.connect.UseSQLradio.isChecked()==True:
            server = self.connect.SQLServerEntry.text()
            username = self.connect.SQLUsernameEntry.text()
            password = self.connect.SQLPasswordEntry.text()
        else:
            server = ""
            username = ""
            password = ""
        # Create a FUR database object
        ### TODO: Check database field is not empty
        ### TODO: Check if the database connection was successful
        databaseobj = libFURdatabase.database(username,password,server,database,0)
        # Display the main database window
        self.main = MainWindow(databaseobj)
        self.main.show()
        self.close()

    def newDB(self):
        database = self.connect.DatabaseNameEntry.text()
        if self.connect.UseSQLradio.isChecked()==True:
            server = self.connect.SQLServerEntry.text()
            username = self.connect.SQLUsernameEntry.text()
            password = self.connect.SQLPasswordEntry.text()
        else:
            server = ""
            username = ""
            password = ""
        # Display the create database settings window
        self.main = CreateDB(database,server,username,password)
        self.main.show()
        self.close()

## Create database window
class CreateDB(QtWidgets.QWidget):
    """Create the database UI functions"""

    def __init__(self,database="",server="",username="",password=""):
        super().__init__()
        # Populate QWidget with UI design
        self.create = Ui_ConfigureDB()
        self.create.setupUi(self)
        # Connect buttons (signals)
        self.create.loadButton.clicked.connect(self.loadConfig)
        self.create.saveButton.clicked.connect(self.saveConfig)
        self.create.backButton.clicked.connect(self.backAction)
        self.create.createButton.clicked.connect(self.createAction)
        self.create.AnnoFileButton.clicked.connect(self.annoFind)
        self.create.GenomeFileButton.clicked.connect(self.genomeFind)
        self.create.BLATFileButton.clicked.connect(self.blatFind)
        #
        self.create.BLATInstNoRB.toggled.connect(self.BLATrbFunc)
        self.create.BLATInstYesRB.toggled.connect(self.BLATrbFunc)
        self.create.DedupLocalRB.toggled.connect(self.DedupMethodrbFunc)
        self.create.DedupGenomeRB.toggled.connect(self.DedupMethodrbFunc)
        self.create.DedupBothRB.toggled.connect(self.DedupMethodrbFunc)

        # Program variables
        self.server = server
        self.username = username
        self.password = password
        self.database = database
        self.DedupMethod=1

        self.updateUI()

    # Set default UI:
    def updateUI(self):
        # If the BLAT executable is found in the same directory prefill the BLATEntry field.
        if os.path.exists("blat"):
            self.create.BLATInstNoRB.setChecked(True)
            self.create.BLATInstYesRB.setChecked(False)
            self.create.BLATEntry.setText('./blat')

    # Interface Function
    def BLATrbFunc(self):
        if self.create.BLATInstNoRB.isChecked()==True:
            self.create.BLATEntry.setEnabled(True)
        else:
            self.create.BLATEntry.setEnabled(False)

    def DedupMethodrbFunc(self):
        if self.create.DedupLocalRB.isChecked()==True:
            self.DedupMethod=1
        elif self.create.DedupGenomeRB.isChecked()==True:
            self.DedupMethod=2
        else:
            self.DedupMethod=3

    # Button actions
    def annoFind(self):
        annoLoc = QtWidgets.QFileDialog.getOpenFileName(self, 'Locate annotation file','','')
        self.create.AnnoFileEntry.setText(annoLoc[0])

    def genomeFind(self):
        genomeLoc = QtWidgets.QFileDialog.getOpenFileName(self, 'Locate genome file','','')
        self.create.GenomeFileEntry.setText(genomeLoc[0])

    def blatFind(self):
        blatLoc = QtWidgets.QFileDialog.getOpenFileName(self, 'Locate BLAT executable','','')
        self.create.BLATEntry.setText(blatLoc[0])

    def loadConfig(self):
        # Display a file chooser window
        # Load values into text fields
        self.create.ConnectionStatus.setText("Load function not available")

    def saveConfig(self):
        # Display a file chooser window
        # Get avalues from text fields and save to file
        self.create.ConnectionStatus.setText("Save function not available")

    def backAction(self):
        # Return to previous window
        self.main = ConnectDB()
        self.main.show()
        self.close()

    def createAction(self):
        # Gather required information for database setup
        AnnoFileLoc = self.create.AnnoFileEntry.text()
        GenomeFileLoc = self.create.GenomeFileEntry.text()
        FlankingSize = self.create.FlankingSizeEntry.text()
        FlankingOffset = self.create.FlankingOffsetEntry.text()
        BLATFileLoc = self.create.BLATEntry.text()
        MinContigSize = self.create.MinContigSizeEntry.text()
        # Setup database
        # TODO - CREATE LOADING SCREEN
        self.create.ConnectionStatus.setText("Creating database...")
        self.create.ConnectionStatus.repaint()
        # TODO - Does not warn of existing database
        libFURdatabase.createDB(self.username,self.password,self.server,self.database, 1)               # Create
        databaseobj = libFURdatabase.database(self.username,self.password,self.server,self.database,0)  # Connect
        self.create.ConnectionStatus.setText("Populating database with annotations...")
        self.create.ConnectionStatus.repaint()
        inputfile = open(AnnoFileLoc,'r')
        filetype = libFURshared.detectFileType(inputfile)
        databaseobj.populateAnnotations(inputfile, filetype)
        self.create.ConnectionStatus.setText("Populating database with flanking regions...")
        self.create.ConnectionStatus.repaint()
        genomefile = open(GenomeFileLoc,'r')
        databaseobj.populateFlankingRegions(genomefile, int(FlankingSize), int(FlankingOffset))
        self.create.ConnectionStatus.setText("Removing softmasked sequence...")
        self.create.ConnectionStatus.repaint()
        databaseobj.populateUnmaskedContigs(int(MinContigSize))
        self.create.ConnectionStatus.setText("Exporting flanking regions for deduplication...")
        self.create.ConnectionStatus.repaint()
        exportfileName = "UnmaskedContigs.fasta"
        exportfile = open(exportfileName,'w')
        tablename = "UnmaskedContigs"
        databaseobj.exportStoredSequences(exportfile, tablename)
        self.create.ConnectionStatus.setText("Running BLAT match identification...")
        self.create.ConnectionStatus.repaint()
        commandtmp = "{} {} {} blatmatches.psl"
        if self.DedupMethod==2:
            commandstr = commandtmp.format(BLATFileLoc, GenomeFileLoc, exportfileName)
        else:
            commandstr = commandtmp.format(BLATFileLoc, exportfileName, exportfileName)
        print(commandstr)
        subprocess.call(commandstr, shell=True)
        if self.DedupMethod==3:
            commandtmp2 = "{} {} {} blatmatchesPt2.psl -noHead"
            commandstr2 = commandtmp2.format(BLATFileLoc, GenomeFileLoc, exportfileName)
            subprocess.call(commandstr2, shell=True)
            command = "cat blatmatches.psl blatmatchesPt2.psl > blatmatchesBoth.psl"
            subprocess.call(command, shell=True)
        self.create.ConnectionStatus.setText("Importing BLAT results and performing deduplication...")
        self.create.ConnectionStatus.repaint()
        if self.DedupMethod==3:
            importfile = open("blatmatchesBoth.psl",'r')
            databaseobj.populateDeduplicatedContigs(importfile, int(MinContigSize), 0, 2)
        else:
            importfile = open("blatmatches.psl",'r')
            databaseobj.populateDeduplicatedContigs(importfile, int(MinContigSize), 0, 1)
        # TODO: Remove temporary files
        # Open next window
        self.main = MainWindow(databaseobj)
        self.main.show()
        self.close()

## Create main program window
class MainWindow(QtWidgets.QMainWindow):
    """Main interface for interacting with the database"""

    def __init__(self, databaseobj=None):
        super().__init__()
        self.databaseobj = None
        # Populate QWidget with UI design
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        ### Inspect tab
        # Connect buttons (signals)
        self.ui.actionConnect_to_database.triggered.connect(self.newConnection)
        self.ui.actionQuit.triggered.connect(self.quitProgram)
        self.ui.annoButton.clicked.connect(self.viewAnno)
        self.ui.contigButton.clicked.connect(self.viewContig)
        # Update the interface with values from the database object
        if databaseobj:
            # Store essential values from the databaseobj (MAYBE MAKE LOCAL)
            self.databaseobj = databaseobj
            self.server = self.databaseobj.SQLhost
            self.username = self.databaseobj.SQLuser
            self.password = self.databaseobj.SQLpass
            self.database = self.databaseobj.SQLdb
            # Update the general information tab
            self.populateInfo()
            # Close the database connection
            #databaseobj.close()
        # Reconnect to the database using the inspection object
        self.populateInspect()
        ### Analysis tab
        # Connect buttons
        self.ui.TransButton.clicked.connect(self.transFind)
        self.ui.AnalysisOutFindButton.clicked.connect(self.analysisOutFind)
        self.ui.SizeAllRB.toggled.connect(self.sizeUIToggle)
        self.ui.SizeLargestRB.toggled.connect(self.sizeUIToggle)
        self.ui.SizeClosestRB.toggled.connect(self.sizeUIToggle)
        self.ui.SizeFixedRB.toggled.connect(self.sizeUIToggle)
        self.ui.EndBothRB.toggled.connect(self.endUIToggle)
        self.ui.EndSenseRB.toggled.connect(self.endUIToggle)
        self.ui.EndAntiRB.toggled.connect(self.endUIToggle)
        self.ui.CheckButton.clicked.connect(self.checkSettings)
        self.ui.AnalyseButton.clicked.connect(self.startAnalysis)
        self.ui.CalcQualButton.clicked.connect(self.calcQuality)
    # Interface functions
    def newConnection(self):
        self.main = ConnectDB()
        self.main.show()
        self.close()

    def quitProgram(self):
        self.close()

    def viewAnno(self):
        # Pass the ID number and inspectionobj:
        inspectobj = libFURinspect.inspect(self.username,self.password,self.server,self.database,0)
        id = int(self.ui.idEntry.text())
        self.annoview = AnnoWindow(id, inspectobj)
        self.annoview.show()
        inspectobj.close()

    def viewContig(self):
        # Pass the ID number and inspectionobj:
        inspectobj = libFURinspect.inspect(self.username,self.password,self.server,self.database,0)
        id = int(self.ui.idEntry.text())
        self.contigview = ContigWindow(id, inspectobj)
        self.contigview.show()
        inspectobj.close()

    def populateInfo(self):
        """Populate the text fields with the database information"""
        if self.databaseobj.SQLhost != "":
            self.ui.DBNameLab.setText(self.databaseobj.SQLdb+" at "+self.databaseobj.SQLhost)
        else:
            self.ui.DBNameLab.setText(self.database+" using local SQLite file.")
        tableinfo = self.databaseobj.tablesizes()
        for table in tableinfo:
            if table[0]=="annotations":
                newtext = self.ui.numAnnoLab.text()
                newtext = newtext.replace('<annonum>',str(table[1]))
                self.ui.numAnnoLab.setText(newtext)
            if table[0]=="flanking":
                newtext = self.ui.FlankingTabLab.text()
                newtext = newtext.replace('<entries>',str(table[1]))
                newtext = newtext.replace('<basepair>',str(table[2]))
                self.ui.FlankingTabLab.setText(newtext)
            if table[0]=="UnmaskedContigs":
                newtext = self.ui.UnmaskTabLab.text()
                newtext = newtext.replace('<entries>',str(table[1]))
                newtext = newtext.replace('<basepair>',str(table[2]))
                self.ui.UnmaskTabLab.setText(newtext)
            if table[0]=="DeduplicatedContigs":
                newtext = self.ui.DedupTabLab.text()
                newtext = newtext.replace('<entries>',str(table[1]))
                newtext = newtext.replace('<basepair>',str(table[2]))
                self.ui.DedupTabLab.setText(newtext)
        databaseinfo = self.databaseobj.databaseInfo()  # Maybe run this and store within object on creation
        regiontext = self.ui.RegionConfigLab.text()
        regiontext = regiontext.replace('<offset>',str(databaseinfo[2]))
        regiontext = regiontext.replace('<size>',str(databaseinfo[1]))
        self.ui.RegionConfigLab.setText(regiontext)
        deduptext = self.ui.DedupConfigLab.text()
        deduptext = deduptext.replace('<mincontig>',str(databaseinfo[3]))
        self.ui.DedupConfigLab.setText(deduptext)
        # Get more detailed information on the database (currently via inspect class)
        self.regionCounts = None
        self.overlappingRegions = None

    def populateInspect(self):
        """Populate the inspect tab with the list of available annotations"""
        # Connect
        inspectobj = libFURinspect.inspect(self.username,self.password,self.server,self.database,0)
        # Run commands
        annoTableRaw = inspectobj.annoDetails("ALL")
        # If the information is available add additional columns on the flanking regions
        if self.regionCounts:
            newannoTableRaw = []
            for item in annoTableRaw:
                regionInfo = self.regionCounts.get(item[0])
                newannoTableRaw.append(item+[regionInfo[0],regionInfo[1],regionInfo[2],regionInfo[3]])
            annoTableRaw = newannoTableRaw
        if self.overlappingRegions:
            # Convert the overlappingRegions info into a dictionary
            overlappingDict = {}
            for item in self.overlappingRegions:
                if item[0] in overlappingDict:
                    overlappingDict[item[0]] = "Both"
                else:
                    if item[1]==1:
                        overlappingDict[item[0]] = "Before"
                    else:
                        overlappingDict[item[0]] = "After"
            # Add to the existing table
            newannoTableRaw = []
            for item in annoTableRaw:
                if item[0] in overlappingDict:
                    if (item[5]=="+" and overlappingDict.get(item[0])=="Before") or (item[5]=="-" and overlappingDict.get(item[0])=="After"):
                        newannoTableRaw.append(item+["Antisense"])
                    else:
                        newannoTableRaw.append(item+["Sense"])
                    #newannoTableRaw.append(item+[overlappingDict.get(item[0])])    # Uncomment in place of previous 4 lines for genomic position
                else:
                    newannoTableRaw.append(item+["None"])
            annoTableRaw = newannoTableRaw
        # Display the results in the UI
        self.ui.tableWidget.setRowCount(len(annoTableRaw))
        self.ui.tableWidget.setColumnCount(len(annoTableRaw[0]))
        curRow = 0
        for entry in annoTableRaw:
            curCol = 0
            for column in entry:
                newField = QtWidgets.QTableWidgetItem(str(column))
                self.ui.tableWidget.setItem(curRow,curCol,newField)
                curCol = curCol+1
            curRow=curRow+1
        header = ["ID","Type","Chromosome","Alignment Start","Alignment End","Strand","Score","Match start","Match End"]
        if self.regionCounts:
            header = header+["Num Sense Contigs","Largest Sense Contig","Num Antisense Contigs","Largest Antisense Contig"]
        if self.overlappingRegions:
            header = header+["Overlapping:"]
        self.ui.tableWidget.setHorizontalHeaderLabels(header)
        self.ui.tableWidget.resizeColumnsToContents()
        # Update the selected ID field
        self.ui.tableWidget.itemSelectionChanged.connect(self.updateInspectID)
        # Close connection
        inspectobj.close()
        # Set selection behaviour to select the entire row.
        self.ui.tableWidget.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        # Store the table, so we can add an export function later
        self.InspectTableViewHeader = header
        self.InspectTableViewData = annoTableRaw
    def updateInspectID(self):
        ID = self.ui.tableWidget.selectedItems()
        self.ui.idEntry.setText(ID[0].text())

    ## Analysis tab functions:
    # Interface
    def transFind(self):
        TransLoc = QtWidgets.QFileDialog.getOpenFileName(self, 'Locate transcription file','','')
        self.ui.TransEntry.setText(TransLoc[0])
    def analysisOutFind(self):
        outLoc = QtWidgets.QFileDialog.getSaveFileName(self, 'Analysis output filepath','','')
        self.ui.AnalysisOutEntry.setText(outLoc[0])
    def sizeUIToggle(self):
        if self.ui.SizeFixedRB.isChecked()==True:
            self.ui.FixedSizeEntry.setEnabled(True)
        else:
            self.ui.FixedSizeEntry.setEnabled(False)
    def endUIToggle(self):
        if self.ui.EndBothRB.isChecked()==True:
            self.ui.SizeEqualBox.setEnabled(True)
        else:
            self.ui.SizeEqualBox.setEnabled(False)
    # Functionality
    def calcQuality(self):
        """When the calculate button is pressed update the program with additional information on contig placement"""
        QualButtonText = self.ui.CalcQualButton.text()
        self.ui.CalcQualButton.setText(QualButtonText+" - Calculating...")
        self.ui.CalcQualButton.repaint()
        # Use the inspection functions to generate the database quality details
        # WARNING: This significantly slows application startup!
        inspectobj = libFURinspect.inspect(self.username,self.password,self.server,self.database,0)
        overlappingRegions = inspectobj.overlappingAnnos()
        # To calculate the number of affected annotations:
        annosAffected = []
        for entry in overlappingRegions:
            annosAffected.append(entry[0])
        annosAffected = list(dict(dict.fromkeys(annosAffected)))
        overlaptext = self.ui.OverlappingLab.text()
        overlaptext = overlaptext.replace('<overlapRegions>',str(len(overlappingRegions)))
        overlaptext = overlaptext.replace('<overlapAnno>',str(len(annosAffected)))
        self.ui.OverlappingLab.setText(overlaptext)
        self.ui.OverlappingLab.repaint()    # Added so this field displays as soon as this process is finished
        # Display information on the annotations with no regions:
        regionCounts = inspectobj.regionCount()
        inspectobj.close()
        senseNullCount = 0
        antiNullCount = 0
        bothNullCount = 0
        for key in regionCounts:
            if (regionCounts.get(key)[0]==0) and (regionCounts.get(key)[2]!=0):
                senseNullCount = senseNullCount+1
            if (regionCounts.get(key)[0]!=0) and (regionCounts.get(key)[2]==0):
                antiNullCount = antiNullCount+1
            if (regionCounts.get(key)[0]==0) and (regionCounts.get(key)[2]==0):
                bothNullCount=bothNullCount+1
        sensetext = self.ui.totalAnnoSenseLab.text()
        sensetext = sensetext.replace('<senseNull>',str(senseNullCount))
        self.ui.totalAnnoSenseLab.setText(sensetext)
        antitext = self.ui.totalAnnoAntiLab.text()
        self.ui.totalAnnoSenseLab.repaint()    # Added so this field displays as soon as this process is finished
        antitext = antitext.replace('<antiNull>',str(antiNullCount))
        self.ui.totalAnnoAntiLab.setText(antitext)
        self.ui.totalAnnoAntiLab.repaint()    # Added so this field displays as soon as this process is finished
        bothtext = self.ui.totalAnnoAbsentLab.text()
        bothtext = bothtext.replace('<bothNull>',str(bothNullCount))
        self.ui.totalAnnoAbsentLab.setText(bothtext)
        self.ui.totalAnnoAbsentLab.repaint()    # Added so this field displays as soon as this process is finished
        # Store values for future use without rerunning database query
        self.regionCounts = regionCounts
        self.overlappingRegions = overlappingRegions
        # Update the inspect tab view to include the additional information
        self.populateInspect()
        # Display the process update
        self.ui.CalcQualButton.setText(QualButtonText)
        self.ui.CalcQualButton.repaint()
    def checkSettings(self):
        # Checks the settings and reports how many annotations do not meet the criteria
        # IMPORTANT NOTE: Technically using largest an annotation with the largest value of 0 is valid!
        # Collect contig information for each annotation (if not already present)
        OriginalStatusMsg = self.ui.AnalysisStatusLab.text()
        self.ui.AnalysisStatusLab.setText("Collecting information on unique regions...")
        self.ui.AnalysisStatusLab.repaint()
        if not self.regionCounts:
            self.calcQuality()
        # Collect user inputs relating to region definition (duplicated from actual analysis function below)
        if self.ui.EndSenseRB.isChecked()==True:
            end = "S"
        elif self.ui.EndAntiRB.isChecked()==True:
            end = "A"
        else:
            end = "B"
        if self.ui.SizeFixedRB.isChecked()==True:
            fixed=int(self.ui.FixedSizeEntry.text())
        else:
            fixed=0
        # Compare user configured settings to the available unique regions
        self.ui.AnalysisStatusLab.setText("Checking annotations against set criteria...")
        self.ui.AnalysisStatusLab.repaint()
        incompatibleAnnos = []
        for annotation in self.InspectTableViewData:
            valid = 1
            senseEnd = 1
            antiEnd = 1
            senseLargest = self.regionCounts.get(annotation[0])[1]
            antiLargest = self.regionCounts.get(annotation[0])[3]
            # TODO: Currently considers no data from one end to cause an annotation to be invalid. If equal unchecked this is not the case.
            # Check fixed size and for ends with out a region:
            if end=="S" or end=="B":
                if senseLargest<fixed:
                        valid=0
            if end=="A" or end=="B":
                if antiLargest<fixed:
                        valid=0
            # Above is fixed==0 then largest regions of '0' is valid (one end permitted)
            if valid==0:
                incompatibleAnnos.append(annotation[0])
        # Temporarily print to the terminal to check function
        #print(str(len(incompatibleAnnos))+" annotations do not meet the criteria and will not be included.")
        #print(incompatibleAnnos)
        # Reset status message
        self.ui.AnalysisStatusLab.setText(OriginalStatusMsg)
        self.ui.AnalysisStatusLab.repaint()
        # Display the results:
        self.checkWin = AnalysisCheckWindow(incompatibleAnnos)
        self.checkWin.show()
    def startAnalysis(self):
        ### Start the analysis and produce the report
        ## Export the sequences for alignment:
        self.ui.AnalysisStatusLab.setText("Extracting sequences from database...")
        self.ui.AnalysisStatusLab.repaint()
        exportFileLoc = "analysisexport.fa"
        exportFile = open(exportFileLoc,"w")
        # Collect information from UI
        if self.ui.OriSenseRB.isChecked()==True:
            orientation = "S"
        elif self.ui.OriAntiRB.isChecked()==True:
            orientation = "A"
        elif self.ui.OriBiRB.isChecked()==True:
            orientation = "B"
        else:
            orientation = "G"
        if self.ui.EndSenseRB.isChecked()==True:
            end = "S"
        elif self.ui.EndAntiRB.isChecked()==True:
            end = "A"
        else:
            end = "B"
        if self.ui.SizeEqualBox.isChecked()==True:
            equal=1
        else:
            equal=0
        if self.ui.SizeLargestRB.isChecked()==True:
            largest=1
        else:
            largest=0
        if self.ui.SizeClosestRB.isChecked()==True:
            closest=1
        else:
            closest=0
        if self.ui.SizeFixedRB.isChecked()==True:
            fixed=int(self.ui.FixedSizeEntry.text())
        else:
            fixed=0
        # Export the sequences
        analysisobj = libFURanalysis.analysis(self.username,self.password,self.server,self.database,0)
        tablename = "DeduplicatedContigs"
        analysisobj.setTableVar(tablename)
        analysisobj.exportSequencesAdv(exportFile,orientation, end, equal, largest, fixed, closest)
        exportFile.close()
        ## Perform alignment
        self.ui.AnalysisStatusLab.setText("Aligning transcriptome to FURdb sequences...")
        self.ui.AnalysisStatusLab.repaint()
        # Collect user input
        TranscriptName = self.ui.TransEntry.text()
        PreCommandTemplate = self.ui.AlignPreEntry.text()
        CommandTemplate = self.ui.AlignCommandEntry.text()
        # Pre command (if present)
        if PreCommandTemplate!="":
            PreCommand = PreCommandTemplate.replace('<seqfile>',exportFileLoc)
            print(PreCommand)
            subprocess.call(PreCommand, shell=True)
        # Run the command (optionally on all files in the folder)
        count = 1
        transcripts = []
        if self.ui.RecursiveBox.isChecked()==True:
            fileNames = os.listdir(TranscriptName)
            for name in fileNames:
                if name[-6:]==".fastq":
                    transcripts.append(TranscriptName+name)
            for TranscriptNameRecursive in transcripts:
                self.ui.AnalysisStatusLab.setText("Aligning transcriptome to FURdb sequences ("+str(count)+")...")
                self.ui.AnalysisStatusLab.repaint()
                count = count+1
                Command = CommandTemplate.replace('<transcriptfile>',TranscriptNameRecursive)
                SamName = TranscriptNameRecursive.split('.')[0]+".sam"
                Command = Command.replace('<samfile>',SamName)
                Command = Command.replace('<seqfile>',exportFileLoc)
                print(Command)
                subprocess.call(Command, shell=True)
        else:
            Command = CommandTemplate.replace('<transcriptfile>',TranscriptName)
            SamName = TranscriptName.split('.')[0]+".sam"
            Command = Command.replace('<samfile>',SamName)
            Command = Command.replace('<seqfile>',exportFileLoc)
            print(Command)
            subprocess.call(Command, shell=True)
        ## Produce the report
        self.ui.AnalysisStatusLab.setText("Producing the report...")
        self.ui.AnalysisStatusLab.repaint()
        # Collect user input
        all = 1 # Include in UI
        header = 1
        regions = 0 # GTF- [0] Entry per annotation [1] Entry per flanking region
        count = 1
        Quality = int(self.ui.AlignQualityEntry.text())
        OutputName = self.ui.AnalysisOutEntry.text()
        if self.ui.RecursiveBox.isChecked()==True:
            for name in transcripts:
                self.ui.AnalysisStatusLab.setText("Producing the report ("+str(count)+")...")
                self.ui.AnalysisStatusLab.repaint()
                count = count+1
                SamName = name.split('.')[0]+".sam"
                name = os.path.split(name)[1]
                OutputName = OutputName+name.split('.')[0]+".tsv"  # Not configurable atm
                OutputFile = open(OutputName,'w')
                samalignobj = libFURanalysis.alignfile(analysisobj,open(SamName),Quality,all)
                extension = OutputName.split('.')[-1]
                if extension.lower() == "gtf":      # Further extend for .count
                    libFURanalysis.reportGTF(samalignobj,OutputFile,header)
                else:
                    libFURanalysis.reportAll(samalignobj,OutputFile,header)
        else:
            OutputFile = open(OutputName,'w')
            samalignobj = libFURanalysis.alignfile(analysisobj,open(SamName),Quality,all)
            extension = OutputName.split('.')[-1]
            if extension.lower() == "gtf":      # Further extend for .count
                libFURanalysis.reportGTF(samalignobj,OutputFile,header)
            else:
                libFURanalysis.reportAll(samalignobj,OutputFile,header)
        analysisobj.close()
        # Close database connection and tidy up
        self.ui.AnalysisStatusLab.setText("Analysis completed")
        self.ui.AnalysisStatusLab.repaint()



## TODO: Allow the table to be toggled between Unmasked and Deduplicated
## Create annotation window
class AnnoWindow(QtWidgets.QWidget):
    """Annotation detailed view"""

    def __init__(self, id=0, inspectobj=None):
        super().__init__()
        # Populate QWidget with UI design
        self.annoui = Ui_Annotation()
        self.annoui.setupUi(self)
        # Connect buttons
        self.annoui.closeButton.clicked.connect(self.closeWindow)
        # Update displayed information
        self.id = id
        self.inspectobj = inspectobj
        self.updateInfo()

    # Interface functions
    def closeWindow(self):
        self.close()

    def updateInfo(self):
        # Update the ID number
        idText = self.annoui.idLab.text()
        idText = idText.replace("<ID>",str(self.id))
        self.annoui.idLab.setText(idText)
        # Update the number of contigs present
        contigList = []
        if self.inspectobj:
            contigList = self.inspectobj.annoContigs(self.id)
        contigText = self.annoui.contigLab.text()
        contigText = contigText.replace("<contignum>",str(len(contigList)))
        self.annoui.contigLab.setText(contigText)
        # Update the table view
        self.annoui.tableWidget.setRowCount(len(contigList))
        if len(contigList)>0:
            self.annoui.tableWidget.setColumnCount(len(contigList[0]))
        else:
            self.annoui.tableWidget.setColumnCount(3)   # No rows in data to get the number of columns from
        curRow = 0
        for entry in contigList:
            curCol = 0
            for column in entry:
                newField = QtWidgets.QTableWidgetItem(str(column))
                self.annoui.tableWidget.setItem(curRow,curCol,newField)
                curCol = curCol+1
            curRow=curRow+1
        header = ["ID","Start","End"]
        self.annoui.tableWidget.setHorizontalHeaderLabels(header)
        self.annoui.tableWidget.resizeColumnsToContents()

## Create contig window
class ContigWindow(QtWidgets.QWidget):
    """Contig detailed view"""

    def __init__(self, id=0, inspectobj=None):
        super().__init__()
        # Populate QWidget with UI design
        self.contigui = Ui_Contig()
        self.contigui.setupUi(self)
        # Connect buttons,
        self.contigui.closeButton.clicked.connect(self.closeWindow)
        self.contigui.viewAnnoButton.clicked.connect(self.viewAnno)
        self.contigui.exportSeqButton.clicked.connect(self.exportAnno)
        # Update displayed information
        try:                    # Check if a correctly formatted ID number has been issued
            self.id = int(id)
            if self.id<0:
                self.id = None  # Negative ID numbers ignored
            # TODO: Check if ID number is valid (ie entry exists within database)
        except:
            self.id = None
        self.inspectobj = inspectobj
        self.updateInfo()

    # Interface functions
    def closeWindow(self):
        self.close()
    def viewAnno(self):
        if self.id:
            inspectobj = libFURinspect.inspect(self.inspectobj.SQLuser,self.inspectobj.SQLpass,self.inspectobj.SQLhost,self.inspectobj.SQLdb,0)
            self.annoview = AnnoWindow(self.AnnoID,inspectobj)   # Open annotation window (Requires updateInfo to be run first)
            self.annoview.show()
            inspectobj.close()
    def updateInfo(self):
        # Update the ID number
        idText = self.contigui.idLab.text()
        idText = idText.replace("<ID>",str(self.id))
        self.contigui.idLab.setText(idText)
        # Lookup the associated annotation ID number
        AnnoID = "Unknown"
        if self.inspectobj:
            AnnoID = self.inspectobj.contigAnno(int(self.id))   # Leaving tablename as default
        annoText = self.contigui.annoLab.text()
        annoText = annoText.replace("<annoid>",str(AnnoID))
        self.contigui.annoLab.setText(annoText)
        self.AnnoID = AnnoID
        # Lookup the location and size of the contig
        if self.inspectobj:
            # Query the database to get the values
            AnnoContigsEntries = self.inspectobj.annoContigs(int(self.AnnoID))   # Leaving tablename as default
            for Contig in AnnoContigsEntries:
                if int(Contig[0]) == self.id:
                    startpos = Contig[1]
                    endpos = Contig[2]
            AnnoDetails = self.inspectobj.annoDetails(int(self.AnnoID))   # Leaving tablename as default
            chromosome = AnnoDetails[2]
            # TODO: Add sense/antisense and distance from LINE1
            # Update labels
            locText = self.contigui.locationLab.text()
            locText = locText.replace("<chr>",chromosome)
            locText = locText.replace("<start>",str(startpos))
            locText = locText.replace("<end>",str(endpos))
            self.contigui.locationLab.setText(locText)
            sizeText = self.contigui.sizeLab.text()
            sizeText = sizeText.replace("<size>",str(int(endpos)-int(startpos)))
            self.contigui.sizeLab.setText(sizeText)

    # Functions
    def exportAnno(self):
        tablename = "DeduplicatedContigs"
        # Save the sequence
        if self.id:
            # Prompt for the save location
            outLoc = QtWidgets.QFileDialog.getSaveFileName(self, 'Save sequence as...','','')
            if outLoc[0]:      # Probably incorrect way to prevent further code execution if the dialog box is cancelled.
                # Get the sequence
                inspectobj = libFURinspect.inspect(self.inspectobj.SQLuser,self.inspectobj.SQLpass,self.inspectobj.SQLhost,self.inspectobj.SQLdb,0)
                sequence = inspectobj.exportSequenceSingle(self.id,tablename)
                inspectobj.close()
                # Write out the sequence
                saveFile = open(outLoc[0],'w')
                libFURshared.exportFASTAEntry(saveFile,str(self.id),sequence)
                saveFile.close()

## Create check analysis config dialog
class AnalysisCheckWindow(QtWidgets.QWidget):
    """Dialog checking the analysis settings"""

    def __init__(self, excludedAnnos = []):
        super().__init__()
        # Populate QWidget with UI design
        self.checkDiag = Ui_AnalysisCheck()
        self.checkDiag.setupUi(self)
        # Update the label:
        self.excludedAnnos = excludedAnnos
        totaltext = self.checkDiag.totalNumLab.text()
        totaltext = totaltext.replace('<num>',str(len(self.excludedAnnos)))
        self.checkDiag.totalNumLab.setText(totaltext)
        # Connect the export button
        self.checkDiag.saveButton.clicked.connect(self.exportList)
        self.checkDiag.closeButton.clicked.connect(self.closeWindow)
    def closeWindow(self):
        self.close()
    def exportList(self):
        # Save the list of annotations
        outLoc = QtWidgets.QFileDialog.getSaveFileName(self, 'Excluded annotations export','','')
        if outLoc[0]:
            fileout = open(outLoc[0],'w')
            for item in self.excludedAnnos:
                fileout.write(str(item)+"\n")
            fileout.close()

# Start UI
if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = ConnectDB()
    widget.show()

    app.exec_()
