__author__ = 'smathias'

try:
    from PySide import QtGui, QtCore
    from PySide.QtSql import QSqlTableModel, QSqlDatabase, QSqlQuery
    from PySide.QtGui import QTableView, QApplication
except ImportError:
    from PyQt4 import QtGui, QtCore
    from PyQt4.QtSql import QSqlTableModel, QSqlDatabase, QSqlQuery
    from PyQt4.QtGui import QTableView, QApplication
import pandas
import charlie.tools.data as data
import charlie.tools.instructions as instructions
import numpy as np
from pkgutil import iter_modules
import charlie.tests
from os.path import dirname
import importlib
import sys
import charlie.tools.batch as batch


class NotesTab(QtGui.QWidget):

    """
    Second tab in the GUI. Allows the user to run individual tests or batches
    of tests.
    """

    def __init__(self, parent=None):
        super(NotesTab, self).__init__(parent=parent)
        self.instr = self.parent().instr
        f = dirname(charlie.tests.__file__)
        self.test_names = [None] + [name for _, name, _ in iter_modules([f])]
        self.test_name = None

        self.vbox = QtGui.QVBoxLayout()
        a = QtGui.QGroupBox(self.instr[27])
        grid = QtGui.QGridLayout()
        test_list = QtGui.QComboBox()
        test_list.addItems(self.test_names)
        test_list.setInsertPolicy(test_list.NoInsert)
        test_list.setEditable(False)
        test_list.activated.connect(self.set_current_test)
        test_list.editTextChanged.connect(self.set_current_test)
        grid.addWidget(test_list, 0, 0, 1, 3)
        button = QtGui.QPushButton(self.instr[28])
        button.clicked.connect(self.run_test)
        grid.addWidget(button, 0, 4)
        self.doc_box = QtGui.QTextEdit()
        self.doc_box.insertPlainText(self.instr[33])
        grid.addWidget(self.doc_box, 1, 0, 4, 5)
        a.setLayout(grid)
        self.vbox.addWidget(a)
        self.setLayout(self.vbox)
        self.show()

    def set_current_test(self):
        self.test_name = self.sender().currentText()
        try:
            mod = importlib.import_module('charlie.tests.' + self.test_name)
        except KeyError:
            return None
        self.doc_box.clear()
        self.doc_box.insertPlainText(mod.__doc__)

    def run_test(self):
        print 'hello'
        if self.test_name is not None:
            print 'hello'
            batch.run_a_test(self.test_name, False)