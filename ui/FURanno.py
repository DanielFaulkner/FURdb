# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FURanno.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Annotation(object):
    def setupUi(self, Annotation):
        Annotation.setObjectName("Annotation")
        Annotation.resize(400, 312)
        self.verticalLayout = QtWidgets.QVBoxLayout(Annotation)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(Annotation)
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
        self.frame = QtWidgets.QFrame(Annotation)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame.setObjectName("frame")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.idLab = QtWidgets.QLabel(self.frame)
        self.idLab.setObjectName("idLab")
        self.verticalLayout_2.addWidget(self.idLab)
        self.contigLab = QtWidgets.QLabel(self.frame)
        self.contigLab.setObjectName("contigLab")
        self.verticalLayout_2.addWidget(self.contigLab)
        self.label_4 = QtWidgets.QLabel(self.frame)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_2.addWidget(self.label_4)
        self.verticalLayout.addWidget(self.frame)
        self.tableWidget = QtWidgets.QTableWidget(Annotation)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.verticalLayout.addWidget(self.tableWidget)
        self.closeButton = QtWidgets.QPushButton(Annotation)
        self.closeButton.setObjectName("closeButton")
        self.verticalLayout.addWidget(self.closeButton)

        self.retranslateUi(Annotation)
        QtCore.QMetaObject.connectSlotsByName(Annotation)

    def retranslateUi(self, Annotation):
        _translate = QtCore.QCoreApplication.translate
        Annotation.setWindowTitle(_translate("Annotation", "FUR - Annotation"))
        self.label.setText(_translate("Annotation", "Annotation details"))
        self.idLab.setText(_translate("Annotation", "Annotation ID: <ID>"))
        self.contigLab.setText(_translate("Annotation", "Number of contigs: <contignum>"))
        self.label_4.setText(_translate("Annotation", "Contig detaills:"))
        self.closeButton.setText(_translate("Annotation", "Close"))
