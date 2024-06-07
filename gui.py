import sys
import re
from PyQt5 import QtCore, QtGui, QtWidgets
import pandas as pd
from match import find_matches
import threading

class Ui_Dialog(QtCore.QObject):  # Inheriting from QObject inorder to use signals and slots for safe threading
    # Signal to notify the main thread to update the UI
    update_ui_signal = QtCore.pyqtSignal()
    def __init__(self):
        super().__init__()
        self.data1 = pd.DataFrame()
        self.data2 = pd.DataFrame()
        self.list1 = ""
        self.list2 = ""
        self.matches = []
        self.replace_text = pd.DataFrame()
        self.store = set()
        # Connect the signal to the slot
        self.update_ui_signal.connect(self.show_popup)
        self.adding_different_data = False
              
    def setupUi(self, Dialog):
        Dialog.setObjectName("Test")
        Dialog.resize(1000, 700)

        # Button to select first Excel file
        self.pushButton1 = QtWidgets.QPushButton(Dialog)
        self.pushButton1.setGeometry(QtCore.QRect(100, 50, 200, 50))
        self.pushButton1.setText("Select Excel File")

        # Button to select second Excel file
        self.pushButton2 = QtWidgets.QPushButton(Dialog)
        self.pushButton2.setGeometry(QtCore.QRect(700, 50, 200, 50))
        self.pushButton2.setText("Select GT Excel File")


        # Table to display data of the first file
        self.table1 = QtWidgets.QTableWidget(Dialog)
        self.table1.setGeometry(QtCore.QRect(50, 150, 400, 500))

        # Table to display data of the second file
        self.table2 = QtWidgets.QTableWidget(Dialog)
        self.table2.setGeometry(QtCore.QRect(550, 150, 400, 500))
                           
        # Button to trigger the matching and highlighting process
        self.pushButton4 = QtWidgets.QPushButton(Dialog)
        self.pushButton4.setGeometry(QtCore.QRect(370, 80, 200, 50))
        self.pushButton4.setText("Highlight Matches")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

        # Connecting buttons to their respective slots
        self.pushButton1.clicked.connect(self.select_first_file)
        self.pushButton2.clicked.connect(self.select_second_file)
        self.pushButton4.clicked.connect(self.highlight_matches)
        
        #Update Excel file with new information
        self.pushButton3 = QtWidgets.QPushButton(Dialog)
        self.pushButton3.setGeometry(QtCore.QRect(370, 20, 200, 50))
        self.pushButton3.setText("Update Excel File")
        self.pushButton3.clicked.connect(self.replace_excel)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Test", "Test"))

    def select_first_file(self):
        file, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Select unverified Excel file", "", "Excel file (*.xlsx)")
        if file:
            df = pd.read_excel(file)
            self.data1 = df  
            self.list1 = df.astype(str).values.flatten().tolist()
            self.display_data(self.table1, self.data1)
        #Ensure Popup file is cleared if new file is selected
        self.replace_text = pd.DataFrame()
        #If the user selects a new file, reset the highlighting process
        if self.adding_different_data:
            for i in range(self.table2.rowCount()):
                for j in range(self.table2.columnCount()):
                    item = self.table2.item(i, j)
                    if item:
                        item.setBackground(QtGui.QColor("white"))
            self.adding_different_data = False

    def select_second_file(self):
        file, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Select verified Excel file", "", "Excel file (*.xlsx)")
        if file:
            df = pd.read_excel(file)
            self.data2 = df 
            self.list2 = df.astype(str).values.flatten().tolist()
            self.display_data(self.table2, self.data2)

    def display_data(self, table, data):
        table.clear()
        table.setRowCount(data.shape[0])
        table.setColumnCount(data.shape[1])
        table.setHorizontalHeaderLabels(data.columns.astype(str).tolist())

        #Populate the table with the data
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                table.setItem(i, j, QtWidgets.QTableWidgetItem(str(data.iat[i, j])))

        
        # Adjust the table to fit the content
        table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

    def highlight_matches(self):
        # Threading for computational process to handle background tasks without suspending GUI
        threading.Thread(target=self.run_highlighting).start()

    def run_highlighting(self):
        # Highlight the matches between the two files
        if self.data1.empty or self.data2.empty:
            return

        # Find matches between the two file lists using LLM
        self.matches, self.dict_matches = find_matches(self.list1, self.list2)
        
        # Convert matches to a set for faster lookup
        match_set = set(match.match for match in self.matches if match.match)
        self.highlight_text_lines(self.table1, match_set, check=True)
        self.highlight_text_lines(self.table2, match_set, check=False)

    def highlight_text_lines(self, table, match_set, check):
        for i in range(table.rowCount()):
            for j in range(table.columnCount()):
                item = table.item(i, j)
                if item:
                    text = item.text()
                    matched = False
                    # Check each word and its substrings against the match set
                    for word in match_set:
                        #If metadata, check against what was matched
                        if check: norm_best_match = self.dict_matches.get(text) 
                        else: norm_best_match = text
                        # Normalize the word and line to lowercase for case-insensitive comparison
                        if norm_best_match == word:
                            item.setBackground(QtGui.QColor("green"))
                            matched = True
                            if check and word not in self.store:
                                self.store.add(word)
                                #Merge matched words to the updated Excel file
                                self.replace_text = pd.concat([self.replace_text, pd.DataFrame({table.horizontalHeaderItem(j).text(): [word]})], ignore_index=True)
                            break
                    #Add the list to the updated Excel file if no match.
                    if not matched and check:
                        self.replace_text = pd.concat([self.replace_text, pd.DataFrame({table.horizontalHeaderItem(j).text(): [text]})], ignore_index=True)
        self.adding_different_data = True
        #O(n) to clear set
        self.store.clear()
    def show_popup(self):
        dialog = QtWidgets.QDialog()
        dialog.setWindowTitle("Updated Excel Contents")
        dialog.resize(800, 600)

        self.table = QtWidgets.QTableWidget(dialog)
        self.table.setGeometry(QtCore.QRect(10, 10, 780, 580))

        # Set the number of rows and columns
        self.table.setRowCount(self.replace_text.shape[0])
        self.table.setColumnCount(self.replace_text.shape[1])

        # Set the table headers
        self.table.setHorizontalHeaderLabels(self.replace_text.columns.astype(str).tolist())

        #Populate the table with the data
        for i in range(self.replace_text.shape[0]):
            for j in range(self.replace_text.shape[1]):
                self.table.setItem(i, j, QtWidgets.QTableWidgetItem(str(self.replace_text.iat[i, j])))

        # Adjust the table to fit the content
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        dialog.exec_()

    def replace_excel(self):
        # Threading for computational process to handle background tasks without suspending GUI
        threading.Thread(target=self.run_replace_excel).start()

    def run_replace_excel(self):
        if (self.data1.empty or self.data2.empty or self.replace_text.empty):
            return
        #Display recent new data and update the UI thread
        self.update_ui_signal.emit()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_Dialog()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

