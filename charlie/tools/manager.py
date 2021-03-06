# -*- coding: utf-8 -*-
__version__ = 1.0
__author__ = 'Sam Mathias'


import sys
from datetime import date
import charlie.tools.data as data
import charlie.tools.batch as batch
import charlie.tools.instructions as instructions
import charlie.tools.arguments as arguments
try:
    from PySide import QtGui, QtCore
    from PySide.QtSql import QSqlQueryModel, QSqlDatabase, QSqlQuery
    from PySide.QtGui import QTableView, QApplication
except ImportError:
    from PyQt4 import QtGui, QtCore
    from PyQt4.QtSql import QSqlQueryModel, QSqlDatabase, QSqlQuery
    from PyQt4.QtGui import QTableView, QApplication


class HomeWidget(QtGui.QWidget):

    """
    Main window widget.
    """

    def __init__(self, parent=None):
        super(HomeWidget, self).__init__(parent=parent)
        # data.populate_probands_table()
        self.args = arguments.get_args()
        self.instr = instructions.read_instructions('manager', self.args.lang)
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

        tabs = QtGui.QTabWidget()
        setup_tab = SetupTab(self)
        tabs.addTab(setup_tab, self.tr(self.instr[2]))
        # test_tab = TestTab(self)
        # tabs.addTab(test_tab, self.tr(self.instr[26]))
        vbox.addWidget(tabs)

        self.setLayout(vbox)
        self.show()


class SetupTab(QtGui.QWidget):

    """
    First tab in the GUI. Allows the user to view, select, and edit the
    project, user, and proband information.
    """

    def __init__(self, parent=None):
        super(SetupTab, self).__init__(parent=parent)
        self.instr = self.parent().instr
        args = self.parent().args
        self.proband_id = args.proband_id
        self.user_id = args.user_id
        self.proj_id = args.proj_id
        _, self.user_list, self.proj_list = data.get_probands_users_projects()

        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(data.LOCAL_DB_F)
        self.db.open()
        self.model = QSqlQueryModel()
        self.model.setQuery("select * from probands", self.db)
        self.view = QTableView()
        self.view.setModel(self.model)
        self.view.setSortingEnabled(True)
        self.view.setSelectionMode(self.view.SingleSelection)
        self.view.setSelectionBehavior(self.view.SelectRows)

        self.setup_ui()

    def setup_ui(self):

        widgets = []  # for easier layout management, all widgets in this list
        a = QtGui.QLabel(self.instr[3])
        widgets.append(a)

        # project and user boxes
        b = QtGui.QGroupBox(self.instr[4])
        grid = QtGui.QGridLayout()
        grid.addWidget(QtGui.QLabel(self.instr[5]), 0, 0)
        proj_list = QtGui.QComboBox()
        proj_list.setItemText(0, self.proj_id)
        proj_list.addItems(self.proj_list)
        proj_list.setInsertPolicy(proj_list.NoInsert)
        proj_list.setEditable(True)
        proj_list.activated.connect(self.set_proj)
        proj_list.editTextChanged.connect(self.set_proj)
        proj_list.setCurrentIndex(0)
        grid.addWidget(proj_list, 1, 0)

        grid.addWidget(QtGui.QLabel(self.instr[6]), 0, 1)
        exp_list = QtGui.QComboBox()
        exp_list.setItemText(0, self.user_id)
        exp_list.addItems(self.user_list)
        exp_list.setInsertPolicy(exp_list.NoInsert)
        exp_list.setEditable(True)
        exp_list.activated.connect(self.set_user)
        exp_list.editTextChanged.connect(self.set_user)
        exp_list.setCurrentIndex(0)
        grid.addWidget(exp_list, 1, 1)
        grid.addWidget(QtGui.QLabel(self.instr[7]), 2, 0, 1, 2)
        b.setLayout(grid)
        widgets.append(b)

        # proband box
        c = QtGui.QGroupBox(self.instr[8])
        cols = 5
        grid = QtGui.QGridLayout()
        grid.addWidget(QtGui.QLabel(self.instr[9]), 0, 0, 1, cols)
        grid.addWidget(QtGui.QLabel(self.instr[10]), 1, 0)
        self.proband_id_label = QtGui.QLabel()
        self.set_text()
        grid.addWidget(self.proband_id_label, 1, 1, 1, cols-1)
        # self.view.setFont(QtGui.QFont("Courier New", 14))
        # self.view.resizeColumnsToContents()

        grid.addWidget(self.view, 2, 0, 1, cols)
        funcs = [
            self.select_proband, self.deselect_proband, self.edit_proband,
            self.new_proband, self.test_proband
        ]
        for i, func in enumerate(funcs):
            button = QtGui.QPushButton(self.instr[11+i])
            button.clicked.connect(func)
            grid.addWidget(button, 3, i)
        c.setLayout(grid)
        widgets.append(c)

        vbox = QtGui.QVBoxLayout()
        [vbox.addWidget(w) for w in widgets]
        self.setLayout(vbox)

    def set_text(self):
        """
        Displays the currently selected proband's ID, in green. Displays
        NONE in red if no proband is selected.
        """
        if self.proband_id:
            s = '<font color="green"><b>%s</b></font>' % self.proband_id
        else:
            s = '<font color="red"><b>None</b></font>'
        self.proband_id_label.setText(s)

    def set_proj(self):
        """
        Sets the project ID.
        """
        self.proj_id = self.sender().currentText()

    def set_user(self):
        """
        Sets the user (experimenter) ID.
        """
        self.user_id = self.sender().currentText()

    def select_proband(self):
        """
        Retrieves a proband from the database.
        """
        if self.check_project_and_experimenter():
            i = self.view.currentIndex()
            j = self.model.data(i, all_row=True)
            self.proband_id = j
            print self.proband_id

    def deselect_proband(self):
        """
        Sets PROBAND to None.
        """
        self.proband_id = ''
        self.set_text()

    def edit_proband(self):
        """
        Creates the proband editor pop-up window.
        """
        if self.check_project_and_experimenter() and self.check_proband():
            self.proband_window(False)

    def new_proband(self):
        """
        Creates the proband editor window with all entries blank.
        """
        if self.check_project_and_experimenter():
            self.proband_window(True)

    def test_proband(self):
        """
        Sets proband to TEST. This is used for debugging test scripts
        without saving data.
        """
        self.proband_id = 'TEST'
        self.set_text()

    def check_project_and_experimenter(self, dialog=True):
        """
        Just checks if project and experimenter IDs have been entered. If
        not, no testing can be done.
        """
        if not self.proj_id:
            if dialog:
                s = self.instr[16]
                a = QtGui.QMessageBox()
                a.setText(s)
                a.exec_()
            return False
        elif not self.user_id:
            if dialog:
                s = self.instr[17]
                a = QtGui.QMessageBox()
                a.setText(s)
                a.exec_()
            return False
        else:
            return True

    def check_proband(self, dialog=True):
        """
        Checks that a proband has been selected.
        """
        if not self.proband_id:
            if dialog:
                s = self.instr[18]
                a = QtGui.QMessageBox()
                a.setText(s)
                a.exec_()
                return False
        elif self.proband_id == 'TEST':
            if dialog:
                s = self.instr[19]
                a = QtGui.QMessageBox()
                a.setText(s)
                a.exec_()
        else:
            return True

    def proband_window(self, new):
        """
        Creates a proband window.
        """
        if new:
            self.deselect_proband()
        self.w = ProbandWindow(self.proband_id, self.model, self.view)
        # self.w.com.update_proband_table.connect(self.model.load_data)
        # self.w.show()


class CustomSignals(QtCore.QObject):
    """
    Container for Qt signal widgets for various purposes.
    """
    update_proband_table = QtCore.Signal()


class ProbandWindow(QtGui.QWidget):

    """
    Proband edit/creation window. This pops up as a separate window from the
    manager. Includes proband ID, sex, and dob. The project and experimenter
    IDs are inherited from the the main window, so this is impossible if these
    fields are left blank.
    """

    def __init__(self, proband_id, model, view, parent=None):
        super(ProbandWindow, self).__init__(parent=parent)
        print model.data()

        # Load in the proband etc.
    #     db = tools.db
    #     self.proband = proband
    #     self.fields = db.PROBAND_ORDER
    #     self.field_descriptions = [db.FIELD_DESCRIPTIONS[f] \
    #                                for f in self.fields]
    #
    #     # Create a blank proband dict if needed
    #     if not self.proband:
    #         self.proband = dict(zip(self.fields, ['']*len(self.fields)))
    #         self.proband['createdby'] = experimenter
    #         self.proband['project'] = project
    #     self.proband['modifiedby'] = experimenter
    #
    #     self.com = CustomSignals()
    #     self.setup_ui()
    #
    #
    # def setup_ui(self):
    #
    #     self.setWindowTitle(instructions[20])
    #     cols = 3
    #     grid = QtGui.QGridLayout()
    #
    #     # Proband ID (not editable if existing proband loaded)
    #     grid.addWidget(QtGui.QLabel(self.field_descriptions[0]+':'), 0, 0, 1,
    #                    cols)
    #     if not self.proband['id']:
    #         self.proband_id_box = QtGui.QLineEdit(self.proband['id'])
    #         self.proband_id_box.textEdited.connect(self.edit_proband_id)
    #     else:
    #         self.proband_id_box = QtGui.QLabel('<b>%s</b>' %self.proband['id'])
    #     grid.addWidget(self.proband_id_box, 1, 0, 1, cols)
    #
    #     # Sex radio buttons
    #     grid.addWidget(QtGui.QLabel(self.field_descriptions[2]+':'), 2, 0)
    #     self.male = QtGui.QRadioButton('Male')
    #     if self.proband['sex'] == 'male':
    #         self.male.toggle()
    #     self.female = QtGui.QRadioButton('Female')
    #     if self.proband['sex'] == 'female':
    #         self.female.toggle()
    #     grid.addWidget(self.male, 2, 1)
    #     grid.addWidget(self.female, 2, 2)
    #
    #     # Dob calendar
    #     grid.addWidget(QtGui.QLabel(self.field_descriptions[3]+':'), 3, 0, 1,
    #                    cols)
    #     self.calendar = QtGui.QCalendarWidget()
    #     dob = self.proband['dob']
    #     if dob:
    #         date = QtCore.QDate(*[int(d) for d in dob.split('-')])
    #         self.calendar.setSelectedDate(date)
    #     grid.addWidget(self.calendar, 4, 0, 1, cols)
    #     button = QtGui.QPushButton(instructions[22])
    #     button.clicked.connect(self.update_proband)
    #     grid.addWidget(button, 20, 0, 1, cols)
    #
    #     # Otheer fields are displayed just for completeness
    #     grid.addWidget(QtGui.QLabel(self.field_descriptions[4]+':'), 5, 0, 1,
    #                    2)
    #     grid.addWidget(QtGui.QLabel('<b>%s</b>' %self.proband['createdby']), 5,
    #                    2, 1, 1)
    #     grid.addWidget(QtGui.QLabel(self.field_descriptions[5]+':'), 6, 0, 1,
    #                    2)
    #     grid.addWidget(QtGui.QLabel('<b>%s</b>' %self.proband['created']), 6,
    #                    2, 1, 1)
    #     grid.addWidget(QtGui.QLabel(self.field_descriptions[6]+':'), 7, 0, 1,
    #                    2)
    #     grid.addWidget(QtGui.QLabel('<b>%s</b>' %self.proband['modifiedby']),
    #                    7, 2, 1, 1)
    #     grid.addWidget(QtGui.QLabel(self.field_descriptions[7]+':'), 8, 0, 1,
    #                    2)
    #     grid.addWidget(QtGui.QLabel('<b>%s</b>' %self.proband['modified']), 8,
    #                    2, 1, 1)
    #     grid.addWidget(QtGui.QLabel(self.field_descriptions[8]+':'), 9, 0, 1,
    #                    2)
    #     l = self.proband['started'].split(',')
    #     if len(l) > 3:
    #         s = '\n'.join(l[:4]) + '... + %i more' %(len(l)-3)
    #     else:
    #         s = '\n'.join(l)
    #     grid.addWidget(QtGui.QLabel(s), 9, 2, 1, 1)
    #     grid.addWidget(QtGui.QLabel(self.field_descriptions[9]+':'), 10, 0, 1,
    #                    2)
    #     l = self.proband['completed'].split(',')
    #     if len(l) > 3:
    #         s = '\n'.join(l[:4]) + '... + %i more' %(len(l)-3)
    #     else:
    #         s = '\n'.join(l)
    #     grid.addWidget(QtGui.QLabel(s), 10, 2, 1, 1)
    #     self.setLayout(grid)
    #     self.show()
    #
    # def edit_proband_id(self):
    #     """Edits the proband ID (if new proband)."""
    #     self.proband['id'] = self.sender().text()
    #
    # def update_proband(self):
    #     """Updates the proband information in the table."""
    #     if self.check_data():
    #         tools.db.insert('probands', self.proband)
    #         self.com.update_proband_table.emit()
    #         self.close()
    #
    # def check_data(self):
    #     """Check that the proband details are all ok."""
    #     if not self.proband['id']:
    #         s = instructions[23]
    #         a = QtGui.QMessageBox()
    #         a.setText(s)
    #         a.exec_()
    #         return False
    #     if self.male.isChecked():
    #         self.proband['sex'] = 'male'
    #     elif self.female.isChecked():
    #         self.proband['sex'] = 'female'
    #     else:
    #         s = instructions[24]
    #         a = QtGui.QMessageBox()
    #         a.setText(s)
    #         a.exec_()
    #         return False
    #     d = self.calendar.selectedDate().toPython()
    #     dob = self.calendar.selectedDate().toString('yyyy-MM-dd')
    #     age = self.calculate_age(d)
    #     if age < 15:
    #         s = instructions[25]
    #         a = QtGui.QMessageBox()
    #         a.setText(s)
    #         a.exec_()
    #         return False
    #     else:
    #         self.proband['dob'] = dob
    #         return True
    #
    # def calculate_age(self, born):
    #     """Calculates someone's age in years."""
    #     today = date.today()
    #     return today.year - born.year - ((today.month, today.day) < \
    #                                      (born.month, born.day))
    #
    # def closeEvent(self, event):
    #     """Closes the window and updates the table."""
    #     self.com.update_proband_table.emit()
# #
# #
# class ProbandTable(QtCore.QAbstractTableModel):
#
#     """
#     Table model widget for the proband details table. Honestly I'm not 100%
#     sure how or why this model works, but it seems ok for now.
#     """
#
#     def __init__(self, parent=None):
#         super(ProbandTable, self).__init__(parent=parent)
#         data.populate_probands_table()
#         self.proband_df = data.get_probands_table()
#         self.fields = self.proband_df.columns.tolist()
#         self.load_data()
#
#     def rowCount(self, parent):
#         return len(self.contents)
#
#     def columnCount(self, parent):
#         return len(self.fields)
#
#     def data(self, index, role=QtCore.Qt.DisplayRole, all_row=False):
#         if not index.isValid():
#             return None
#         elif role != QtCore.Qt.DisplayRole:
#             return None
#         elif not all_row:
#             return self.contents[index.row()][index.column()]
#         else:
#             return self.contents[index.row()][0]
#
#     def headerData(self, col, orientation, role):
#         if orientation == QtCore.Qt.Horizontal and \
#         role == QtCore.Qt.DisplayRole:
#             return self.fields[col]
#         return None
#
#     def sort(self, col, order):
#         from operator import itemgetter
#         self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
#         self.contents = sorted(self.contents, key=itemgetter(col))
#         if order == QtCore.Qt.DescendingOrder:
#             self.contents.reverse()
#         self.emit(QtCore.SIGNAL("layoutChanged()"))
#     #
#     def load_data(self):
#         self.contents = self.proband_df.T
#         print self.contents
#         self.emit(QtCore.SIGNAL("layoutChanged()"))
#
#
# class TestTab(QtGui.QWidget):
#
#     """Second tab in the main window. Allows the user to run individual tests
#     or batteries of tests."""
#
#     def __init__(self, parent=None):
#         super(TestTab, self).__init__(parent=parent)
#
#         self.current_test = None
#         self.test_names = ['']+[r['id'] for r in tools.db.fetch('tests', None,
#                                                                 'all')]
#         self.test_docs = {}
#         for test in self.test_names[1:]:
#             module = __import__(test)
#             self.test_docs[test] = module.__doc__
#
#         self.setup_ui()
#
#     def setup_ui(self):
#
#         widgets = []
#
#         # Individual tests
#         a = QtGui.QGroupBox(instructions[27])
#         grid = QtGui.QGridLayout()
#         test_list = QtGui.QComboBox()
#         test_list.addItems(self.test_names)
#         test_list.setInsertPolicy(test_list.NoInsert)
#         test_list.setEditable(False)
#         test_list.activated.connect(self.set_current_test)
#         test_list.editTextChanged.connect(self.set_current_test)
#         grid.addWidget(test_list, 0, 0, 1, 3)
#         button = QtGui.QPushButton(instructions[28])
#         button.clicked.connect(self.run_test)
#         grid.addWidget(button, 0, 4)
#         self.doc_box = QtGui.QTextEdit()
#         self.doc_box.insertPlainText(instructions[33])
#         self.test_docs[''] = instructions[33]
#         grid.addWidget(self.doc_box, 1, 0, 4, 5)
#         a.setLayout(grid)
#         widgets.append(a)
#
#         b = QtGui.QGroupBox(instructions[38])
#         grid = QtGui.QGridLayout()
#         placeholder = QtGui.QLabel('Coming soon!')
#         grid.addWidget(placeholder, 0, 0)
#         b.setLayout(grid)
#         widgets.append(b)
#
#         # Add widgets
#         vbox = QtGui.QVBoxLayout()
#         [vbox.addWidget(w) for w in widgets]
#         self.setLayout(vbox)
#
#         self.show()
#
#     def check(self):
#         if not self.current_test:
#             return False
#         elif not PROBAND:
#             s = instructions[29]
#             a = QtGui.QMessageBox()
#             a.setText(s)
#             a.exec_()
#             return False
#         else:
#             return True
#
#     def set_current_test(self):
#         self.current_test = self.sender().currentText()
#         self.doc_box.clear()
#         self.doc_box.insertPlainText(self.test_docs[self.current_test])
#
#     def check_data(self):
# #        print 'checking data'
#         data = tools.data.load_data(PROBAND['id'], self.current_test)
#         if data.test_started and not data.test_done:
#             t = len(data.data) / float(len(data.data + data.control)) * 100
#             t = int(round(t))
#             mb = QtGui.QMessageBox()
#             mb.setText(instructions[34] %(PROBAND['id'], t))
#             mb.setInformativeText(instructions[35])
#             mb.setStandardButtons(mb.Ok | mb.Reset | mb.Abort)
#             r = mb.exec_()
#             if r == mb.Ok:
#                 return True
#             elif r == mb.Reset:
#                 a = QtGui.QMessageBox()
#                 a.setText(instructions[37])
#                 a.setStandardButtons(a.Ok | a.Cancel)
#                 r = a.exec_()
#                 if r == a.Ok:
#                     tools.data.reset_data(PROBAND['id'], self.current_test)
#                     return True
#                 elif r == a.Cancel:
#                     return False
#             elif r == mb.Abort:
#                 return False
#         elif data.test_done:
#             mb = QtGui.QMessageBox()
#             mb.setText(instructions[36] %(PROBAND['id']))
#             mb.setStandardButtons(mb.Reset | mb.Abort)
#             r = mb.exec_()
#             if r == mb.Reset:
#                 a = QtGui.QMessageBox()
#                 a.setText(instructions[37])
#                 a.setStandardButtons(a.Ok | a.Cancel)
#                 r = a.exec_()
#                 if r == a.Ok:
#                     tools.data.reset_data(PROBAND['id'], self.current_test)
#                     return True
#                 elif r == a.Cancel:
#                     return False
#             elif r == mb.Abort:
#                 return False
#         else:
#             return True
#
#     def run_test(self):
#         if self.check() and self.check_data():
#             f = '%s.py' %self.current_test
#             cmd = 'cd %s' %cwd.replace(' ','\ ')
#             os.system(cmd)
#             cmd = 'python %s' %f
#             if PROBAND['id'] != 'TEST':
#                 cmd += ' %s' %PROBAND['id']
#                 os.system(cmd)
#             else:
#                 a = QtGui.QMessageBox()
#                 a.setText(instructions[30])
#                 a.setInformativeText(instructions[31])
#                 a.setStandardButtons(a.Ok | a.Cancel)
#                 r = a.exec_()
#                 if r == a.Ok:
#                     execfile(f)
#
#
def main():
    app = QtGui.QApplication(sys.argv)
    _ = HomeWidget()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()