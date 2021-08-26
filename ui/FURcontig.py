# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FURcontig.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Contig(object):
    def setupUi(self, Contig):
        Contig.setObjectName("Contig")
        Contig.resize(400, 206)
        self.verticalLayout = QtWidgets.QVBoxLayout(Contig)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(Contig)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.frame_2 = QtWidgets.QFrame(Contig)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_2.setObjectName("frame_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame_2)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.idLab = QtWidgets.QLabel(self.frame_2)
        self.idLab.setObjectName("idLab")
        self.verticalLayout_2.addWidget(self.idLab)
        self.sizeLab = QtWidgets.QLabel(self.frame_2)
        self.sizeLab.setObjectName("sizeLab")
        self.verticalLayout_2.addWidget(self.sizeLab)
        self.locationLab = QtWidgets.QLabel(self.frame_2)
        self.locationLab.setObjectName("locationLab")
        self.verticalLayout_2.addWidget(self.locationLab)
        self.frame = QtWidgets.QFrame(self.frame_2)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.annoLab = QtWidgets.QLabel(self.frame)
        self.annoLab.setObjectName("annoLab")
        self.horizontalLayout.addWidget(self.annoLab)
        self.viewAnnoButton = QtWidgets.QPushButton(self.frame)
        self.viewAnnoButton.setObjectName("viewAnnoButton")
        self.horizontalLayout.addWidget(self.viewAnnoButton)
        self.verticalLayout_2.addWidget(self.frame)
        self.verticalLayout.addWidget(self.frame_2)
        self.exportSeqButton = QtWidgets.QPushButton(Contig)
        self.exportSeqButton.setObjectName("exportSeqButton")
        self.verticalLayout.addWidget(self.exportSeqButton)
        self.closeButton = QtWidgets.QPushButton(Contig)
        self.closeButton.setObjectName("closeButton")
        self.verticalLayout.addWidget(self.closeButton)

        self.retranslateUi(Contig)
        QtCore.QMetaObject.connectSlotsByName(Contig)

    def retranslateUi(self, Contig):
        _translate = QtCore.QCoreApplication.translate
        Contig.setWindowTitle(_translate("Contig", "FUR - Contig"))
        self.label.setText(_translate("Contig", "Contig details"))
        self.idLab.setText(_translate("Contig", "Contig ID: <ID>"))
        self.sizeLab.setText(_translate("Contig", "Size: <size>bp"))
        self.locationLab.setText(_translate("Contig", "Location: <chr>:<start>-<end>"))
        self.annoLab.setText(_translate("Contig", "Parent annotation: <annoid>"))
        self.viewAnnoButton.setText(_translate("Contig", "View"))
        self.exportSeqButton.setText(_translate("Contig", "Export Sequence"))
        self.closeButton.setText(_translate("Contig", "Close"))
