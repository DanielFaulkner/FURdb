# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AnalysisCheck.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AnalysisCheck(object):
    def setupUi(self, AnalysisCheck):
        AnalysisCheck.setObjectName("AnalysisCheck")
        AnalysisCheck.resize(400, 168)
        self.verticalLayout = QtWidgets.QVBoxLayout(AnalysisCheck)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(AnalysisCheck)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.label_2 = QtWidgets.QLabel(AnalysisCheck)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.totalNumLab = QtWidgets.QLabel(AnalysisCheck)
        self.totalNumLab.setObjectName("totalNumLab")
        self.verticalLayout.addWidget(self.totalNumLab)
        self.label_4 = QtWidgets.QLabel(AnalysisCheck)
        self.label_4.setObjectName("label_4")
        self.verticalLayout.addWidget(self.label_4)
        self.saveButton = QtWidgets.QPushButton(AnalysisCheck)
        self.saveButton.setObjectName("saveButton")
        self.verticalLayout.addWidget(self.saveButton)
        self.closeButton = QtWidgets.QPushButton(AnalysisCheck)
        self.closeButton.setObjectName("closeButton")
        self.verticalLayout.addWidget(self.closeButton)

        self.retranslateUi(AnalysisCheck)
        QtCore.QMetaObject.connectSlotsByName(AnalysisCheck)

    def retranslateUi(self, AnalysisCheck):
        _translate = QtCore.QCoreApplication.translate
        AnalysisCheck.setWindowTitle(_translate("AnalysisCheck", "Analysis Settings Check"))
        self.label.setText(_translate("AnalysisCheck", "Analysis configuration check:"))
        self.label_2.setText(_translate("AnalysisCheck", "The current database and region settings exclude will exclude:"))
        self.totalNumLab.setText(_translate("AnalysisCheck", "<num> annotations."))
        self.label_4.setText(_translate("AnalysisCheck", "Important: Some settings permit empty regions. (I.e. largest)"))
        self.saveButton.setText(_translate("AnalysisCheck", "Save list"))
        self.closeButton.setText(_translate("AnalysisCheck", "Close"))
