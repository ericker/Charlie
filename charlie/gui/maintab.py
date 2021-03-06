"""
Front-end GUI for Charlie. Allows the experimenter to enter proband
information, run individual tests and questionnaires, batches of tests, and add
notes to the database. Eventually, the GUI will also contain data backup and
transfer functionality.

"""
__version__ = 0.1
__author__ = 'smathias'


import sys
try:
    from PySide import QtGui, QtCore
except ImportError:
    from PyQt4 import QtGui, QtCore
import charlie.tools.arguments as arguments
import charlie.tools.data as data
import charlie.tools.instructions as instructions
from charlie.gui.setuptab import SetupTab
from charlie.gui.testtab import TestTab
from charlie.gui.qtab import QuestionnaireTab
from charlie.gui.batchtab import BatchTab
from charlie.gui.notestab import NotesTab
from charlie.gui.datatab import DataTab


class HomeWidget(QtGui.QWidget):

    """
    Main window widget. This essentially just holds the various tabs (widgets
    imported from other scripts).
    """

    def __init__(self, parent=None):
        super(HomeWidget, self).__init__(parent=parent)
        sys.argv = sys.argv[:1]  # wipe all sys args
        self.instr = instructions.read_instructions('manager', 'EN')
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle(self.instr[0])
        vbox = QtGui.QVBoxLayout()

        pixmap = QtGui.QPixmap(data.pj(data.PACKAGE_DIR, 'charlie.png'))
        img = QtGui.QLabel()
        img.setPixmap(pixmap)
        img.setAlignment(QtCore.Qt.AlignCenter)
        vbox.addWidget(img)

        txt = QtGui.QLabel(self.instr[1] % __version__)
        txt.setAlignment(QtCore.Qt.AlignCenter)
        vbox.addWidget(txt)

        self.setup_tab = SetupTab(self)
        self.batch_tab = BatchTab(self)
        self.test_tab = TestTab(self)
        self.q_tab = QuestionnaireTab(self)

        self.tabs = QtGui.QTabWidget()
        self.tabs.addTab(self.setup_tab, self.tr('Session setup'))
        self.tabs.addTab(self.batch_tab, self.tr('Batch'))
        self.tabs.addTab(self.test_tab, self.tr('Individual tests'))
        self.tabs.addTab(self.q_tab, self.tr('Questionnaires'))

        # setup_tab = SetupTab(self)
        # tabs.addTab(setup_tab, self.tr('Session setup'))
        #
        # test_tab = TestTab(self)
        # tabs.addTab(test_tab, self.tr('Individual tests'))
        #
        # q_tab = QuestionnaireTab(self)
        # batch_tab = BatchTab(self)
        # tabs.addTab(batch_tab, self.tr('Batch'))
        #
        # tabs.addTab(q_tab, self.tr('Questionnaires'))
        # notes_tab = NotesTab(self)
        # tabs.addTab(notes_tab, self.tr('Notes'))
        # data_tab = DataTab(self)
        # tabs.addTab(data_tab, self.tr('Data transfer'))
        vbox.addWidget(self.tabs)

        self.setLayout(vbox)
        self.show()
        self.raise_()


class CharlieGui:

    def __init__(self):
        self.run()

    def run(self):
        app = QtGui.QApplication(sys.argv)
        app.aboutToQuit.connect(app.deleteLater)
        window = HomeWidget()
        app.exec_()


if __name__ == '__main__':
    pass