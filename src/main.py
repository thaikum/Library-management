import hashlib
import string
import sys
import time
import pyqtgraph as pg
import numpy as np

import qtawesome as qta
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from src.book import new_book, blacklist, unblacklist
from src.book_borrow import new_borrow, all_borrows, return_book, is_blacklisted, range_selection, \
    range_selection_by_date, \
    borrowing_history
from src.helper import *
from src.lib_user import *
from src import resources


class ChangePassword(QDialog):
    def __init__(self, *args, **kwargs):
        self.lib_no = kwargs.get('lib_no')
        del kwargs['lib_no']
        super(ChangePassword, self).__init__(*args, **kwargs)
        self.ui = uic.loadUi('../UI/passwordchange.ui', self)
        self.changeConfirmPassword.textChanged.connect(lambda: password_matcher(self.changePasswordError,
                                                                                self.changeNewPassword,
                                                                                self.changeConfirmPassword))
        self.btnChangePassword.clicked.connect(self.pchanger)

    def pchanger(self):
        if not self.changePasswordError.text():
            password1 = self.changeOldPassword.text()
            password2 = self.changeNewPassword.text()
            password1 = password_hasher(self.lib_no, password1)
            password2 = password_hasher(self.lib_no, password2)

            pchange = change_password(self.lib_no, password1, password2)
            if pchange:
                success_message('Password changed successfully', 'Password changed')
                self.accept()
            else:
                error_message('An internal error occurred \n please contact system admin', 'Internal error')
        else:
            error_message('fix the errors displayed above first!', 'Fix errors first')


class UpdateProfile(QDialog):
    def __init__(self, *args, **kwargs):
        self.lib_no = kwargs.get('lib_no')
        del kwargs['lib_no']
        super(UpdateProfile, self).__init__(*args, **kwargs)
        self.ui = uic.loadUi('../UI/updateprofile.ui', self)
        self.btnUpdateProfile.clicked.connect(self.update)
        self.pre_fill()

    def pre_fill(self):
        details = get_staff_details(self.lib_no)
        self.updateFName.setText(details[0].capitalize())
        self.updateSName.setText(details[1].capitalize())
        self.updateOName.setText(details[2].capitalize())
        self.updatePhone.setText(details[3])
        self.lblUserName.setText(
            details[0].capitalize() + ' ' + details[1].capitalize() + ' ' + details[2].capitalize())

    def update(self):
        first_name = self.updateFName.text().upper()
        second_name = self.updateSName.text().upper()
        other_name = self.updateOName.text().upper()
        phone = self.updatePhone.text()

        updated = update_staff(self.lib_no, first_name, second_name, other_name, phone)
        if updated:
            success_message('Profile updated successfully', 'Profile updated')
            self.accept()
        else:
            error_message('Internal error occurred', 'Internal, error')


class BlacklistReason(QDialog):
    def __init__(self, *args, **kwargs):
        super(BlacklistReason, self).__init__(*args, **kwargs)
        self.ui = uic.loadUi('../UI/BlacklistingDialog.ui', self)


def success_message(message, box_title):
    msg = QMessageBox(QMessageBox.Information, box_title, message)
    msg.setStyleSheet('background-color:#800000;color:white;font-size:15px')
    msg.exec_()


def error_message(message, box_title):
    msg = QMessageBox(QMessageBox.Critical, box_title, message)
    msg.setStyleSheet('background-color:#800000;color:white;font-size:15px')
    msg.exec_()


class Login(QDialog):
    def __init__(self, *args, **kwargs):
        super(Login, self).__init__(*args, **kwargs)
        self.ui = uic.loadUi('../UI/login.ui', self)

        # ======================== pages ====================================================
        self.btnLogin.clicked.connect(self.authenticate)
        self.btnToSignup.clicked.connect(lambda: self.pages.setCurrentWidget(self.signupPage))
        self.btnToLogin.clicked.connect(lambda: self.pages.setCurrentWidget(self.loginPage))
        self.btnToLogin.click()

        # ======================= password match checking ====================================
        self.signupConfirmPassword.textChanged.connect(
            lambda: password_matcher(self.lblSignUpError, self.signupNewPassword, self.signupConfirmPassword))

        # ===================== sign up functionality ======================
        self.signUp.clicked.connect(self.new_sign_up)

    def authenticate(self):
        lib_no = self.loginLibNo.text().upper()
        password = hashlib.pbkdf2_hmac("sha256", self.loginPassword.text().encode(), lib_no.encode(), 100000).hex()
        success = login_admin(lib_no, password)
        if success:
            self.accept()
        else:
            display_label_error(self.errorLabel, 'Invalid login credentials')

    def new_sign_up(self):
        lib_no = self.signupLibNo.text().upper()
        password = hashlib.pbkdf2_hmac("sha256", self.signupNewPassword.text().encode(), lib_no.encode(), 100000).hex()
        result = create_admin(lib_no, password=password)
        if result[0]:
            success_message('Account create successfully. You will be automatically loged in after this', 'Success')
            self.loginLibNo.setText(lib_no)
            self.accept()
        else:
            self.show_sign_up_error(result[1])


class Ui(QtWidgets.QMainWindow):
    can_borrow = False
    global_book_list = []
    global_book_borrow_list = []
    global_staff_list = []
    logged_user: string = ''
    logged_user_type: string = ''

    def __init__(self):
        super(Ui, self).__init__()
        self.ui = uic.loadUi('../UI/main2.ui', self)

        # ================================== login ================================
        self.login()

        # ============================= tab navigators ===========================
        self.previousButton = self.btnLibSession

        self.activeButton(self.btnLibSession)  # default page

        self.ui.btnBooks.clicked.connect(lambda: self.activeButton(self.btnBooks))
        self.ui.btnLibSession.clicked.connect(lambda: self.activeButton(self.btnLibSession))
        self.ui.btnStudents.clicked.connect(lambda: self.activeButton(self.btnStudents))
        self.ui.btnStaff.clicked.connect(lambda: self.activeButton(self.btnStaff))
        self.ui.btnSettings.clicked.connect(lambda: self.activeButton(self.btnSettings))
        self.ui.btnReport.clicked.connect(lambda: self.activeButton(self.btnReport))

        # ============================== Saving data to the database ===============================
        self.ui.btnSaveStd.clicked.connect(self.new_student)
        self.ui.stfSaveDetails.clicked.connect(self.new_staff)
        self.ui.btnSaveBook.clicked.connect(self.add_new_book)
        self.ui.btnBorrowBook.clicked.connect(self.new_book_borrow)

        # ================== Some constraints to enable/disable buttons ===========================
        self.txtLibNoBorrow.editingFinished.connect(self.validate_lib_user)
        self.txtBookIdBorrow.editingFinished.connect(self.validate_book)

        # ================= Minimum date =========================================================
        self.ui.dtReturnDateBorrow.setMinimumDate(dt.today())
        self.ui.dayBookAdded.setMinimumDate(dt.today())

        # ==================== ui text initialization ===========================================
        self.show_book_borrow_error('')

        # ====================== context menu ========================================
        self.ui.tblBorrow.customContextMenuRequested.connect(self.borrow_table_menu)
        self.ui.tblBooks.customContextMenuRequested.connect(self.book_table_menu)
        self.ui.tblReport.customContextMenuRequested.connect(self.report_table_menu)
        self.ui.tblStaff.customContextMenuRequested.connect(self.staff_table_menu)
        self.ui.tblStudent.customContextMenuRequested.connect(self.student_table_menu)

        # ======================= setting icons ======================================
        self.btnBooks.setIcon(self.icon('fa5s.book', scale=1.3))
        self.btnLibSession.setIcon(self.icon('fa5s.book-reader', scale=1.3))
        self.btnStudents.setIcon(self.icon('fa5s.user-graduate', scale=1.3))
        self.btnStaff.setIcon(self.icon('fa5s.user-secret', scale=1.3))
        spin_icon = qta.icon('fa5s.cog', color='white', animation=qta.Spin(self.btnSettings))
        self.btnSettings.setIcon(spin_icon)
        self.btnUsers.setIcon(self.icon("fa5s.user"))

        # ====================== additional ui customisation ========================
        self.btnSettings.setText('')
        self.btnSettings.setToolTip('Settings')

        self.btnUsers.setText('')

        # =======================vertical box ======================================
        self.mywidget = QWidget()
        self.graphScroll.setWidget(self.mywidget)
        self.vbox = QVBoxLayout()
        self.mywidget.setLayout(self.vbox)
        self.mywidget.setMaximumHeight(16777215)

        # ====================== search functionallity ==============================
        self.txtBookSearch.setPlaceholderText('Search...')
        self.txtBorrowSearch.setPlaceholderText('Search...')
        self.txtStaffSearch.setPlaceholderText('Search...')
        self.txtStudentSearch.setPlaceholderText('Search...')

        self.txtBookSearch.textChanged.connect(
            lambda: self.insert_into_table(self.tblBooks, search(self.global_book_list, self.txtBookSearch.text())))
        self.txtBorrowSearch.textChanged.connect(lambda: self.insert_into_table(self.tblBorrow,
                                                                                search(self.global_book_borrow_list,
                                                                                       self.txtBorrowSearch.text())))
        self.txtStaffSearch.textChanged.connect(
            lambda: self.insert_into_table(self.tblStaff, search(self.global_staff_list, self.txtStaffSearch.text())))
        self.txtStudentSearch.textChanged.connect(lambda: self.insert_into_table(self.tblStudent,
                                                                                 search(self.global_student_list,
                                                                                        self.txtStaffSearch.tet())))
        # =================================== Menu buttons ===============================
        self.btnUsers.setMenu(self.update_profile_menu())

        # ================================= report =============================================
        self.generateRangeReport.clicked.connect(self.range_report)
        # ============================= Logout =====================================
        self.btnLogout.clicked.connect(self.login)

        # =========================================================================
        self.clearStudentDetails.clicked.connect(lambda: self.btnSaveStd.setText('Save'))

        # ============================== populate tables===============================
        self.populate_book_table()
        self.populate_staff_table()
        self.populate_student_table()
        self.populate_borrow_book_table()

        # ============================== student page buttons ==========================

        self.btnPromoteAll.clicked.connect(self.promote_all)
        self.btnDemoteAll.clicked.connect(self.demote_all)

        # ============================== staff page buttons ============================

        self.clearStaffDetails.clicked.connect(lambda: self.stfSaveDetails.setText('Save'))

        # =================================================================================
        self.showMaximized()

    def new_student(self):
        ui = self.ui
        lib_no = ui.txtNewLibNo.text().upper()
        fname = ui.txtStdFname.text().upper()
        sname = ui.txtStdSname.text().upper()
        oname = ui.txtStdOname.text().upper()
        user_type = 'STUDENT'
        std_class = ui.txtStdClass.text()
        stream = ui.txtStdStream.text().upper()

        if not lib_no:
            details = add_lib_user(fname, sname, oname, user_type, std_class=std_class, stream=stream)

        else:
            details = add_lib_user(fname, sname, oname, user_type, std_class=std_class, stream=stream, lib_no=lib_no)

        if details:
            ui.clearStudentDetails.click()
            self.populate_student_table()

    def new_staff(self):
        ui = self.ui

        lib_no = ui.stfLibNo.text().upper()
        fname = ui.stfFirstName.text().upper()
        sname = ui.stfSecondName.text().upper()
        oname = ui.stfOtherName.text().upper()
        user_type = 'STAFF'
        phone_no = ui.stfPhoneNo.text()

        if lib_no:
            details = add_lib_user(fname, sname, oname, user_type, phone_no=phone_no, lib_no=lib_no)
            if details:
                success_message('staff details updated successfully', 'Details updated')
                self.populate_staff_table()
                self.clearStaffDetails.click()
                self.populate_borrow_book_table()

            else:
                error_message('An internal error occurred \nPlease contact admin for more details', 'Could not update')

        else:
            details = add_lib_user(fname, sname, oname, user_type, phone_no=phone_no)

            if details:
                ui.clearStaffDetails.click()
                self.populate_staff_table()

    def add_new_book(self):
        book_id = self.bookIdDetails.text().upper()
        book_name = self.bookNameDetails.text().upper()
        date_added = self.dayBookAdded.date().toPyDate()
        book_category = self.cmbBookCategory.currentText().upper()

        success = new_book(book_id, book_name, date_added, book_category)

        if success:
            self.clearBookDetails.click()
            self.populate_book_table()
        else:
            error_message('A book with such details exists', 'Book exists!')

    def new_book_borrow(self):
        ui = self.ui
        lib_no = ui.txtLibNoBorrow.text().upper()
        book_id = ui.txtBookIdBorrow.text().upper()
        return_date = ui.dtReturnDateBorrow.date().toPyDate()
        today = time.strftime('%Y-%m-%d')

        success = new_borrow(lib_no, book_id, today, return_date)

        if success == 'blacklisted':
            error_message('The book is currently blacklisted', "Blacklisted")
        elif success == 'active':
            error_message('Return the previous book first', "Invalid")
        else:
            self.populate_borrow_book_table()
            self.btnClearBookBorrow.click()

    # ============================= populate tables functions =========================================

    def populate_student_table(self):
        ui = self.ui

        students = all_students()
        self.global_student_list = students

        self.insert_into_table(ui.tblStudent, students)

    def populate_staff_table(self):
        ui = self.ui
        staff = all_staff(user_type=self.logged_user_type)
        self.global_staff_list = staff

        self.insert_into_table(ui.tblStaff, staff)
        self.autocomplete(ui.txtLibNoBorrow, list_to_string(staff, 0))

    def populate_book_table(self):
        ui = self.ui

        books = all_books()
        self.global_book_list = books

        self.autocomplete(ui.txtBookIdBorrow, list_to_string(books, 0))
        self.insert_into_table(ui.tblBooks, books)

    def populate_borrow_book_table(self):
        ui = self.ui
        borrows = all_borrows()
        self.global_book_borrow_list = borrows
        self.set_min_and_max_date()

        self.insert_into_table(ui.tblBorrow, borrows)

    def clear_table(self, table):
        size = table.rowCount() - 1
        while size >= 0:
            table.removeRow(size)
            size -= 1

    def insert_into_table(self, table, details):
        self.clear_table(table)

        row = 0
        for detail in details:
            table.insertRow(row)
            column = 0
            for data in detail:
                data = QtWidgets.QTableWidgetItem(str(data))
                table.setItem(row, column, data)
                column += 1
            row += 1
        table.resizeColumnsToContents()

    def validate_lib_user(self):
        ui = self.ui
        lib_no = ui.txtLibNoBorrow.text().upper()
        lib_user_exists = search_lib_user(lib_no)
        if lib_user_exists:
            name = lib_user_exists[1]
            ui.txtUserNameBorrow.setText(name)
            self.activate_borrow_button()
        else:
            self.can_borrow = False
            ui.txtUserNameBorrow.clear()
            self.show_book_borrow_error('Please ensure that all data provided is correct!!!')
            ui.btnBorrowBook.setEnabled(False)

    def validate_book(self):
        ui = self.ui
        book_id = ui.txtBookIdBorrow.text().upper()
        book_available = search_book(book_id)
        if book_available:
            ui.txtBookNameBorrow.setText(book_available[1])
            self.activate_borrow_button()
        else:
            self.can_borrow = False
            ui.txtBookNameBorrow.clear()
            self.show_book_borrow_error('Please ensure that all data provided is correct !!!')
            ui.btnBorrowBook.setEnabled(False)

    def activate_borrow_button(self):
        if self.can_borrow:
            self.ui.btnBorrowBook.setEnabled(True)
            self.show_book_borrow_error('')
        else:
            self.show_book_borrow_error('Please ensure that all data provided is correct !!!')
            self.can_borrow = True

    def show_book_borrow_error(self, error):
        if error:
            self.ui.lblBookBorrowError.setStyleSheet('color:red;\nbackground-color:white;\nborder-radius:4px;')
            self.ui.lblBookBorrowError.setText(error)
        else:
            self.ui.lblBookBorrowError.setStyleSheet('')
            self.ui.lblBookBorrowError.setText('')

    def autocomplete(self, lineedit, data):
        completer = QCompleter(data)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        lineedit.setCompleter(completer)

# ================================== menus =============================================
    def update_profile_menu(self):
        menu = QMenu()
        menu.addAction(qta.icon('fa5.edit'), 'Edit profile', self.update_user_profile, 'ctrl+e')
        menu.addAction(qta.icon('fa5s.key'), 'Change password', self.change_user_password)
        return menu

    # ==================================== table menus ====================================

    def borrow_table_menu(self, position):

        menu = QMenu()
        removeRow = menu.addAction("Set Returned")
        removeIcon = qta.icon('fa5.check-circle')
        removeRow.setIcon(removeIcon)
        removeRow.setShortcut('ctrl+r')

        action = menu.exec_(self.ui.tblBorrow.mapToGlobal(position))
        if action == removeRow:
            self.book_return()

    def student_table_menu(self, position):
        menu = QMenu()
        menu.addAction(qta.icon('fa5.edit'), 'Edit details', self.edit_student_details)
        lib_no = self.tblStudent.item(self.tblStudent.currentRow(), 0).text().upper()
        if check_for_user_blacklist(lib_no):
            menu.addAction(qta.icon('fa5s.lock-open', color='red'), "ublacklist", lambda: self.unblacklist_user(lib_no))
        else:
            menu.addAction(qta.icon('fa5s.ban', color='red'), 'Blacklist', lambda: self.blacklist_user(lib_no))
        menu.addAction(qta.icon('fa5s.arrow-up'), 'Promote class', lambda: self.promote_indv_student(lib_no))
        menu.addAction(qta.icon('fa5s.arrow-down'), 'demote class', lambda: self.demote_indv_student(lib_no))
        menu.exec_(self.ui.tblStudent.mapToGlobal(position))

    def book_table_menu(self, position):
        menu = QMenu()
        menu.setStyleSheet('font-weight:bold;font-size:13px;')
        removeRow = menu.addAction("Remove Book")
        removeRow.setIcon(qta.icon('fa5.check-circle'))
        editRecord = menu.addAction('Edit details')
        editRecord.setIcon(qta.icon('fa5.edit'))
        menu.addSeparator()
        book_id = self.tblBooks.item(self.tblBooks.currentRow(), 0).text()
        if is_blacklisted(book_id):
            menu.addAction(qta.icon('fa5s.lock-open', color='red'), "ublacklist", lambda: self.unblacklist(book_id),
                           'ctrl+u')
        else:
            menu.addAction(qta.icon('fa5s.ban', color='red'), "blacklist", lambda: self.blacklist(book_id), 'ctrl+l')

        action = menu.exec_(self.ui.tblBooks.mapToGlobal(position))

        if action == editRecord:
            self.edit_books()

    def staff_table_menu(self, position):
        menu = QMenu()
        user_type = self.tblStaff.item(self.tblStaff.currentRow(), 3).text().lower()
        if user_type == 'super admin':
            pass
        elif user_type == 'admin':
            menu.addAction(self.icon('fa5s.user-minus', color='black'), 'Remove admin', self.remove_admin)
        else:
            menu.addAction(self.icon('fa5s.user-plus', color='black'), 'Add as admin', self.add_admin)
        menu.addAction(self.icon('fa5.edit', color='black'), 'Edit details', self.edit_staff_details)

        menu.exec_(self.ui.tblStaff.mapToGlobal(position))

    def report_table_menu(self, position):
        menu = QMenu()
        menu.addAction('View graph', self.create_book_usage_graph)
        menu.exec_(self.ui.tblReport.mapToGlobal(position))

# ============================== Menu actions ====================================================
    # ===================================== student menu action ===================================
    def edit_student_details(self):
        row = self.tblStudent.currentRow()
        lib_no = self.tblStudent.item(row, 0).text()
        name = self.tblStudent.item(row, 1).text().split(' ')
        student_class = self.tblStudent.item(row, 2).text().split(' ')

        if len(name) == 3:
            fname = name[0]
            sname = name[1]
            oname = name[2]

        else:
            fname = name[0]
            sname = name[1]
            oname = ''

        self.txtNewLibNo.setText(lib_no)
        self.txtStdFname.setText(fname)
        self.txtStdSname.setText(sname)
        self.txtStdOname.setText(oname)
        self.txtStdClass.setText(student_class[0])
        self.txtStdStream.setText(student_class[1])

        self.btnSaveStd.setText('Update')

    def promote_indv_student(self, lib_no):
        result = promote_individal_student(lib_no, 'promote')
        if result:
            success_message(f'Student {lib_no} promoted', 'promoted')
            self.populate_student_table()
        else:
            error_message('Internal errror occured please contact admin for more details', 'Internal error')

    def demote_indv_student(self, lib_no):
        result = promote_individal_student(lib_no, 'demote')
        if result:
            success_message(f'Student {lib_no} demoted', 'promoted')
            self.populate_student_table()
        else:
            error_message('Internal error occurred please contact admin for more details', 'Internal error')

    def promote_all(self):
        result = promote_all_students('promote')
        if result:
            success_message(f'Students promoted', 'Promoted')
            self.populate_student_table()
        else:
            error_message('Internal error occurred please contact admin for more details', 'Internal error')

    def demote_all(self):
        result = promote_all_students('demote')
        if result:
            success_message(f'Students demoted', 'Promoted')
            self.populate_student_table()
        else:
            error_message('Internal error occurred please contact admin for more details', 'Internal error')

    # =================================== student + staff menu action =======================================
    def blacklist_user(self, lib_no):
        dlg = BlacklistReason(self)
        dlg.exec_()

        if dlg.result():
            reason = dlg.blacklistReason.toPlainText()
            if blacklist_user(lib_no, reason):
                success_message(f'User <b>{lib_no}</b> has been blacklisted', 'Success')

    def unblacklist_user(self, lib_no):
        if unblacklist_user(lib_no):
            success_message(f'Use <b>{lib_no}</b> has been removed from blacklisting list', 'Unblacklisted')

    # ================================== update profile actions =====================================
    def update_user_profile(self):
        dlg = UpdateProfile(self, lib_no=self.logged_user.upper())
        dlg.exec_()

    def change_user_password(self):
        dlg = ChangePassword(self, lib_no=self.logged_user.upper())
        dlg.exec_()

    # ================================== staff menu actions ====================================

    def add_admin(self):
        lib_no = self.tblStaff.item(self.tblStaff.currentRow(), 0).text().upper()
        if create_admin(lib_no):
            success_message(f"lib number {lib_no} activated successifully as admin", 'Admin added')
            self.populate_staff_table()
        else:
            error_message('an internal error occurred', 'Fatal')

    def remove_admin(self):
        lib_no = self.tblStaff.item(self.tblStaff.currentRow(), 0).text().upper()
        if de_admin(lib_no):
            success_message(f'Admin {lib_no} was deactivated', 'Admin deactivated')
            self.populate_staff_table()
        else:
            error_message('Internal error occurred', 'Internal error')

    def edit_staff_details(self):
        lib_no = self.tblStaff.item(self.tblStaff.currentRow(), 0).text().upper()
        details = get_staff_details(lib_no)

        self.stfFirstName.setText(details[0].capitalize())
        self.stfSecondName.setText(details[1].capitalize())
        self.stfOtherName.setText(details[2].capitalize())
        self.stfPhoneNo.setText(details[3].capitalize())
        self.stfLibNo.setText(lib_no)

        self.stfSaveDetails.setText('update')

    # ================================ book table menu actions ====================================
    def blacklist(self, book_id):
        dlg = BlacklistReason(self)
        dlg.exec_()

        if dlg.result():
            reason = dlg.blacklistReason.toPlainText()
            if blacklist(book_id, reason):
                success_message(f'Book <b>{book_id}</b> has been blacklisted', 'Success')

    def unblacklist(self, book_id):
        if unblacklist(book_id):
            success_message(f'Book have been <b>{book_id}</b> unblacklisted', 'Success')

    def edit_books(self):
        row = self.tblBooks.currentRow()
        book_id = self.tblBooks.item(row, 0).text()
        book_name = self.tblBooks.item(row, 1).text()
        book_category = self.tblBooks.item(row, 2).text()
        date_added = self.tblBooks.item(row, 3).text()

        self.bookIdDetails.setText(book_id)
        self.bookNameDetails.setText(book_name)
        self.dayBookAdded.setDate(dt.strptime(date_added, '%Y-%m-%d'))
        self.cmbBookCategory.setCurrentText(book_category.capitalize())

    # ================================= book borrowed menu actions ================================
    def book_return(self):
        lib_no = self.tblBorrow.item(self.tblBorrow.currentRow(), 0).text()
        book_no = self.tblBorrow.item(self.tblBorrow.currentRow(), 2).text()
        success = return_book(lib_no, book_no)
        if success:
            self.populate_borrow_book_table()

    # =============================================================================================

    # =================================== menu bar switcher =======================================
    def activeButton(self, currentButton):
        if currentButton.objectName() == 'btnLibSession':
            self.pages.setCurrentWidget(self.pgLibSession)
        elif currentButton.objectName() == 'btnBooks':
            self.pages.setCurrentWidget(self.pgBooks)
        elif currentButton.objectName() == 'btnStudents':
            self.pages.setCurrentWidget(self.pgStudents)
        elif currentButton.objectName() == 'btnStaff':
            self.pages.setCurrentWidget(self.pgStaff)
        elif currentButton.objectName() == 'btnSettings':
            self.pages.setCurrentWidget(self.pgSettings)
        elif currentButton.objectName() == 'btnReport':
            self.pages.setCurrentWidget(self.pgReport)

        self.previousButton.setStyleSheet('padding-left:10px;\npadding-right:5px;')

        currentButton.setStyleSheet('padding-left:10px;border:none;padding-right:5px;')
        self.previousButton = currentButton

    # ================================== Reporting section ==========================================
    def range_report(self):
        from_date = self.fromDate.date().toPyDate()
        to_date = self.toDate.date().toPyDate()

        result = range_selection(from_date, to_date)
        self.createtable(self.tblReport, ['Book Name', 'Category', 'Form or class', 'Times Borrowed'])
        self.insert_into_table(self.tblReport, result)

        self.txtTotalBooks.setText(get_total(result, 3))

    def create_book_usage_graph(self):
        from_date = self.fromDate.date().toPyDate()
        to_date = self.toDate.date().toPyDate()
        row = self.tblReport.currentRow()
        book_name = self.tblReport.item(row, 0).text()
        book_category = self.tblReport.item(row, 1).text()
        form_class = self.tblReport.item(row, 2).text()

        result = range_selection_by_date(book_name, book_category, form_class, from_date, to_date)
        graph_axis = one_to_two_lists(result)
        graph = self.create_graph()

        self.vbox.addStretch()
        self.vbox.insertWidget(self.vbox.count() - 1, graph)
        graph.setMinimumHeight(300)
        pen = pg.mkPen(color=(255, 0, 0))
        graph.plot(pos=np.array(result))
        graph.setBackground('w')
        graph.setTitle(f'<u style = "color: blue; font-size:10em;">Graph for {book_name} class/ form {form_class}</u>')

        graph.setLabel('left', "<span style=\"color:red\">Number of books borrowed (°C)</span>")
        graph.setLabel('bottom', "<span style=\"color:red;\">Dates</span>")
        graph.showGrid(x=True, y=True)

    def create_graph(self):
        graph_widget = pg.PlotWidget()
        return graph_widget

    # ============================ assistive functions =========================================
    def icon(self, icon_name, color='white', scale=1):
        return qta.icon(icon_name, color=color, scale_factor=scale)

    def createtable(self, table, columns):
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)

# ================================= fields customisation ========================================
    # ========================= reporting section =============================================
    def set_min_and_max_date(self):
        date_list = get_date_list(borrowing_history(), 3)
        self.fromDate.setMinimumDate(min(date_list))
        self.toDate.setMinimumDate(min(date_list))
        self.fromDate.setMaximumDate(max(date_list))
        self.toDate.setMaximumDate(max(date_list))
        self.onDate.setMinimumDate(max(date_list))
        self.onDate.setMaximumDate(max(date_list))

# ============================= Authentication ====================================================
    def login(self):
        dlg = Login(self)
        self.setWindowOpacity(0)
        dlg.exec_()

        if not dlg.result():
            exit()

        else:
            self.logged_user = dlg.loginLibNo.text().upper()
            self.logged_user_type = get_admin_type(self.logged_user)

            self.lblLoginName.setText(
                f"logged as: <span style = 'color: blue;font-size:16px;'>{self.logged_user.upper()}</span>")

        self.setWindowOpacity(1)


# =========================== running the app =====================================
def main():
    app = QtWidgets.QApplication(sys.argv)
    Ui()
    app.exec_()


if __name__ == '__main__':
    main()
