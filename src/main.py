from PyQt5 import QtWidgets, uic 
from PyQt5.QtWidgets import QCompleter, QMenu, QAction, QPushButton, QMessageBox
from PyQt5.QtGui import QIntValidator
import qtawesome as qta
from PyQt5.QtCore import Qt
import sys
import time
from datetime import datetime as dt

from lib_user import add_lib_user, all_students, all_staff
from book import new_book, all_books, blacklist, unblacklist
from helper import search_lib_user, search_book, list_to_string
from book_borrow import new_borrow, all_borrows, return_book, is_blacklisted

class Ui(QtWidgets.QMainWindow):
	can_borrow = False

	def __init__(self):
		super(Ui, self).__init__()
		self.ui = uic.loadUi('./UI/main2.ui',self)

		#tab navigators
		self.previousButton = self.btnLibSession

		self.activeButton(self.btnLibSession)#default page

		self.ui.btnBooks.clicked.connect(lambda: self.activeButton(self.btnBooks) )
		self.ui.btnLibSession.clicked.connect(lambda: self.activeButton(self.btnLibSession))
		self.ui.btnStudents.clicked.connect(lambda: self.activeButton(self.btnStudents))
		self.ui.btnStaff.clicked.connect(lambda: self.activeButton(self.btnStaff))
		
		#============================== Saving data to the database ===============================
		self.ui.btnSaveStd.clicked.connect(self.new_student)
		self.ui.stfSaveDetails.clicked.connect(self.new_staff)
		self.ui.btnSaveBook.clicked.connect(self.add_new_book)
		self.ui.btnBorrowBook.clicked.connect(self.new_book_borrow)

		#====================populate tables ============================================
		self.populate_student_table()
		self.populate_staff_table()
		self.populate_book_table()
		self.populate_borrow_book_table()

		#================== Some constraints to enable/disable buttons ==================
		self.txtLibNoBorrow.editingFinished.connect(self.validate_lib_user)
		self.txtBookIdBorrow.editingFinished.connect(self.validate_book)

		#================= Minimum date =======================
		self.ui.dtReturnDateBorrow.setMinimumDate(dt.today())
		self.ui.dayBookAdded.setMinimumDate(dt.today())

		#==================== ui text initialization =====================
		self.show_book_borrow_error('')

		#====================== context menu =========================
		self.ui.tblBorrow.customContextMenuRequested.connect(self.borrow_table_menu)
		self.ui.tblBooks.customContextMenuRequested.connect(self.book_table_menu)

		#======================= setting icons =========================
		self.btnBooks.setIcon(self.icon('fa5s.book',scale = 1.3))
		self.btnLibSession.setIcon(self.icon('fa5s.book-reader', scale = 1.3))
		self.btnStudents.setIcon(self.icon('fa5s.user-graduate',scale = 1.3))
		self.btnStaff.setIcon(self.icon('fa5s.user-secret',scale = 1.3))
		spin_icon = qta.icon('fa5s.cog', color='white', animation = qta.Spin(self.btnSettings))
		self.btnSettings.setIcon(spin_icon)

		#====================== additional ui customisation ========================
		self.btnSettings.setStyleSheet('background-color:none;border:none;width:10px')
		self.btnSettings.setText('')
		self.btnSettings.setStatusTip('Settings')

		#====================================================================
		style = open('./UI/style.qss','r').read()
		self.centralwidget.setStyleSheet(style)
		self.showMaximized()

	def new_student(self):
		ui = self.ui

		fname = ui.txtStdFname.text().upper()
		sname = ui.txtStdSname.text().upper()
		oname = ui.txtStdOname.text().upper()
		user_type = 'STUDENT'
		std_class = ui.txtStdClass.text()
		stream = ui.txtStdStream.text().upper()

		details = add_lib_user(fname, sname,oname, user_type , std_class = std_class, stream = stream)

		if details:
			ui.clearStudentDetails.click()
			self.populate_student_table()

	def new_staff(self):
		ui = self.ui 

		fname = ui.stfFirstName.text().upper()
		sname = ui.stfSecondName.text().upper()
		oname = ui.stfOtherName.text().upper()
		user_type = 'STAFF'
		phone_no = ui.stfPhoneNo.text()

		details = add_lib_user(fname,sname,oname,user_type, phone_no = phone_no)

		if details:
			ui.clearStaffDetails.click()
			self.populate_staff_table()

	def add_new_book(self):
			book_id = self.bookIdDetails.text().upper()
			book_name = self.bookNameDetails.text().upper()
			date_added = self.dayBookAdded.date().toPyDate()
			book_category = self.cmbBookCategory.currentText().upper()

			success = new_book(book_id,book_name,date_added,book_category)

			if success:
				self.clearBookDetails.click()
				self.populate_book_table()
			else:
				self.error_message('A book with such details exists','Book exists!')
	def new_book_borrow(self):
		ui = self.ui
		lib_no = ui.txtLibNoBorrow.text().upper()
		book_id = ui.txtBookIdBorrow.text().upper()
		return_date = ui.dtReturnDateBorrow.date().toPyDate()
		today = time.strftime('%Y-%m-%d')

		success = new_borrow(lib_no, book_id, today, return_date)

		if success == 'blacklisted':
			self.error_message('The book is currently blacklisted',"Blacklisted")
		elif success == 'active':
			self.error_message('Return the previous book first',"Invalid")
		else:
			self.populate_borrow_book_table()
			self.btnClearBookBorrow.click()
		
		
	def populate_student_table(self):
		ui = self.ui
		self.clear_table(ui.tblStudent)
		
		students = all_students()

		self.insert_into_table(ui.tblStudent, students)
		
	def populate_staff_table(self):
		ui = self.ui
		self.clear_table(ui.tblStaff)
		staff = all_staff()

		self.insert_into_table(ui.tblStaff, staff)
		self.autocomplete(ui.txtLibNoBorrow,list_to_string(staff,0) )

	def populate_book_table(self):
		ui = self.ui
		self.clear_table(ui.tblBooks)

		books = all_books()
		self.autocomplete(ui.txtBookIdBorrow, list_to_string(books,0) )
		self.insert_into_table(ui.tblBooks,books)
	
	def populate_borrow_book_table(self):
		ui = self.ui
		self.clear_table(ui.tblBorrow)
		borrows = all_borrows()

		self.insert_into_table(ui.tblBorrow, borrows)

	def clear_table(self, table):
		size = table.rowCount() - 1 
		while size >= 0 :
			table.removeRow(size)
			size-=1

	def insert_into_table(self,table,details):
		row = 0
		for detail in details:
			table.insertRow(row)
			column = 0
			for data in detail:
				data = QtWidgets.QTableWidgetItem(data)
				table.setItem(row,column,data)
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

	def autocomplete(self, lineedit,data):
		completer = QCompleter(data)
		completer.setCaseSensitivity(Qt.CaseInsensitive)
		lineedit.setCompleter(completer)

	def borrow_table_menu(self, position):
		
		menu = QMenu()
		menu.setTitle("hello world")
		removeRow = menu.addAction("Set Returned")
		removeIcon = qta.icon('fa5.check-circle')
		removeRow.setIcon(removeIcon)
		removeRow.setShortcut('ctrl+r')
		
		action = menu.exec_(self.ui.tblBorrow.mapToGlobal(position))
		if action == removeRow:
			self.book_return()

	def book_table_menu(self, position):
		menu = QMenu()
		menu.setStyleSheet('font-weight:bold;font-size:13px;')
		removeRow = menu.addAction("Remove Book")
		removeRow.setIcon(qta.icon('fa5.check-circle'))
		editRecord = menu.addAction('Edit details')
		editRecord.setIcon(qta.icon('fa5.edit'))
		menu.addSeparator()
		book_id = self.tblBooks.item(self.tblBooks.currentRow(),0).text()
		if is_blacklisted(book_id):
			menu.addAction(qta.icon('fa5s.lock-open',color = 'red'),"ublacklist",lambda: self.unblacklist(book_id),'ctrl+u')
		else:
			menu.addAction(qta.icon('fa5s.ban',color = 'red'),"blacklist",lambda:self.blacklist(book_id),'ctrl+l')
			
		action = menu.exec_(self.ui.tblBooks.mapToGlobal(position))

		if action == editRecord:
			self.edit_books()

	def blacklist(self,book_id):
		pass
	def unblacklist(self,book_id):
		print("kkk")
		unblacklist(book_id)

	def icon(self, icon_name, color = 'white', scale = 1):
		return qta.icon(icon_name,color = color, scale_factor = scale)
	
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
			pass

		if currentButton.objectName() != 'btnSettings':
			self.previousButton.setStyleSheet('padding-left:10px;\npadding-right:5px;')

			currentButton.setStyleSheet('padding-left:10px;\nborder:none;\npadding-right:5px;')
			self.previousButton = currentButton

	def book_return(self):
		lib_no = self.tblBorrow.item(self.tblBorrow.currentRow(),0).text()
		book_no = self.tblBorrow.item(self.tblBorrow.currentRow(),2).text()
		success = return_book(lib_no, book_no)
		if success:
			self.populate_borrow_book_table()

	def edit_books(self):
		row = self.tblBooks.currentRow()
		book_id = self.tblBooks.item(row,0).text()
		book_name = self.tblBooks.item(row,1).text()
		book_category = self.tblBooks.item(row,2).text()
		date_added = self.tblBooks.item(row,3).text()

		self.bookIdDetails.setText(book_id)
		self.bookNameDetails.setText(book_name)
		self.dayBookAdded.setDate(dt.strptime(date_added, '%Y-%m-%d'))
		self.cmbBookCategory.setCurrentText(book_category.capitalize())

	def error_message(self,message,box_title):
		msg = QMessageBox(QMessageBox.Critical, box_title ,message)
		msg.setStyleSheet('background-color:#800000;color:white;font-size:15px')
		msg.exec_()

app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()
