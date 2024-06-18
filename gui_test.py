import sys
import re
from PyQt5 import QtCore, QtGui, QtWidgets
import pandas as pd
from match_test import find_matches
import threading

#CTRL+Click to display the row's data
class CustomTableWidget(QtWidgets.QTableWidget):
    ctrlClicked = QtCore.pyqtSignal(QtWidgets.QTableWidgetItem)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and QtWidgets.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier:
            item = self.itemAt(event.pos())
            if item is not None:
                self.ctrlClicked.emit(item)
        super().mousePressEvent(event)

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
        self.color_match = {}
        self.pairs_matched = {}
        self.new_background = {}
        self.old_background = {}
        
        # Connect the signal to the slot
        self.update_ui_signal.connect(self.show_popup)
        self.is_matched = False
              
    def setupUi(self, Dialog):
        Dialog.setObjectName("Test")
        Dialog.resize(1000, 700)

        #Save the Dialog
        self.Dialog = Dialog
        # Create a central widget and set it for the MainWindow
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        MainWindow.setCentralWidget(self.centralWidget)

        # Create a main layout
        self.mainLayout = QtWidgets.QVBoxLayout(self.centralWidget)
        
        #Layout schemes for buttons, tables, and combo box
        self.topLayout = QtWidgets.QHBoxLayout()
        self.leftLayout = QtWidgets.QVBoxLayout()
        self.rightLayout = QtWidgets.QVBoxLayout()
        self.tableLayout= QtWidgets.QHBoxLayout()

        # Button to select first Excel file
        self.pushButton1 = QtWidgets.QPushButton(Dialog)
        self.pushButton1.setText("Select Excel File")
        self.leftLayout.addWidget(self.pushButton1)

        # Dropdown to select metadata form
        self.comboBox = QtWidgets.QComboBox(Dialog)
        self.comboBox.addItem("NBISC Intake Form") 
        self.comboBox.addItem("ODIC")  
        self.rightLayout.addWidget(self.comboBox)

        
        # Table to display data of the second file
        self.table2 = QtWidgets.QTableWidget(Dialog)
        self.table2.setMinimumSize(400, 200)
        self.table2.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.tableLayout.addWidget(self.table2)

        # Table to display data of the first file
        self.table1 = CustomTableWidget(Dialog)
        self.table1.setMinimumSize(400, 200)
        self.table1.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.tableLayout.addWidget(self.table1)
                           
        # Button to trigger the matching and highlighting process
        self.pushButton4 = QtWidgets.QPushButton(Dialog)
        self.pushButton4.setText("Highlight Matches")
        self.topLayout.addWidget(self.pushButton4)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

         #Update Excel file with new information
        self.pushButton3 = QtWidgets.QPushButton(Dialog)
        self.pushButton3.setText("Update Excel File")
        self.topLayout.addWidget(self.pushButton3)
        self.pushButton3.clicked.connect(self.replace_excel)


        # Connecting buttons to their respective slots
        self.pushButton1.clicked.connect(self.select_first_file)
        self.pushButton4.clicked.connect(self.highlight_matches)


        self.mainLayout.addLayout(self.topLayout)
        self.mainLayout.addLayout(self.leftLayout)
        self.mainLayout.addLayout(self.rightLayout)
        self.mainLayout.addLayout(self.tableLayout)

        

        #CTRL+Click to display the row's data
        # self.table1.ctrlClicked.connect(self.handle_table1_click)

        #Click once to display dropdown other potential matches of the selected item
        self.connect_table1_events()
            
        
        #Default dropdown selection
        #path/to/[X].xlsx
        file = "C:/Users/kayvo/Semantic-List-Matching-with-LLMs/output.xlsx"
        df = pd.read_excel(file)
        self.data2 = df 
        self.list2 = df.columns.astype(str).tolist()
        self.display_data(self.table2, self.data2, False)
        #Select metadata file
        self.comboBox.currentIndexChanged.connect(self.select_metadata)
        

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Test", "Test"))

    def select_first_file(self):
        file, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Select unverified Excel file", "", "Excel file (*.xlsx)")
        if file:
            df = pd.read_excel(file)
            self.data1 = df  
            self.list1 = df.columns.astype(str).tolist()
            self.display_data(self.table1, self.data1, True)
        #Ensure Popup file is cleared if new file is selected
        self.replace_text = pd.DataFrame()            
        #Reset the highlighting process for first file
        if self.is_matched:
            for i in range(self.table2.rowCount()):
                for j in range(self.table2.columnCount()):
                    item = self.table2.item(i, j)
                    if item:
                        item.setBackground(QtGui.QColor("white"))
            self.is_matched = False

    def select_metadata(self):
         #All metadata files
         #path/to/[X].xlsx
        metadata_files = {
            "NBISC Intake Form": "C:/Users/kayvo/Semantic-List-Matching-with-LLMs/output.xlsx",
            "ODIC": "C:/Users/kayvo/Semantic-List-Matching-with-LLMs/test_output.xlsx",
        }
        #Reset the highlighting process for first file
        for i in range(self.table1.rowCount()):
            for j in range(self.table1.columnCount()):
                item = self.table1.item(i, j)
                if item:
                    item.setBackground(QtGui.QColor("white"))

        selected_metadata = self.comboBox.currentText()
        self.adding_different_data = True
        if selected_metadata in metadata_files:
            file = metadata_files[selected_metadata]
            df = pd.read_excel(file)
            self.data2 = df 
            self.list2 = df.columns.astype(str).tolist()
            self.display_data(self.table2, self.data2, False)

    def display_data(self, table, data, check):
        max_length = 50  # Maximum length of header to display
        table.clear()
        table.setRowCount(data.shape[1])
        table.setColumnCount(1)
        if check:
            table.setHorizontalHeaderLabels(["Headers that Need Matching"])
        else:
            table.setHorizontalHeaderLabels(["MetaData"])

        #Populate the table with the data
        for i, header in enumerate(data.columns.tolist()):
            # truncated_header = (header[:max_length] + '...') if len(header) > max_length else header
            item = QtWidgets.QTableWidgetItem(header)
            item.setToolTip(header)  # Set the full header as the tooltip
            table.setItem(i, 0, item)
        
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

        #Generate random colors for each match and mappings for each
        self.match_to_color = {}
        for match in match_set:
            if match not in self.match_to_color:
                self.match_to_color[match] = QtGui.QColor(QtCore.qrand() % 256, QtCore.qrand() % 256, QtCore.qrand() % 256)
        self.highlight_text_lines(self.table1, match_set, check=True)
        self.highlight_text_lines(self.table2, match_set, check=False)
        
        self.is_matched = True

        #Reorder the matched highlighted data
        self.realign_data()

    def highlight_text_lines(self, table, match_set, check):
        # highlighted_items = set()  # Set to track already highlighted items
        for i in range(table.rowCount()):
            for j in range(table.columnCount()):
                item = table.item(i, j)
                if item:
                    text = item.text()
                    # if check and (i, j) in highlighted_items:
                    #     continue
                    matched = False
                    # Check each word and its substrings against the match set
                    for word in match_set:
                        #If metadata, check against what was matched
                        if check: norm_best_match = self.dict_matches.get(item.toolTip())
                        else: norm_best_match = item.toolTip()
                        
                        # Normalize the word and line to lowercase for case-insensitive comparison
                        if norm_best_match == word:
                            matched = True
                            # Highlight the matched word
                            item.setBackground(self.match_to_color[word])
                            if check and word not in self.store:
                                self.new_background[item.text()] = word
                                self.store.add(word)
                                #Merge matched words to the updated Excel file
                                self.replace_text = pd.concat([self.replace_text, pd.DataFrame({text: self.data1[item.toolTip()].iloc[:].to_list()})], axis=1)
                                #replace nans with empty strings
                                self.replace_text = self.replace_text.replace({pd.NA: ''}) 
                            # if check:
                            #     highlighted_items.add((i,j))
                            break
                            
                    #Add the list to the updated Excel file if no match.
                    if not matched and check:
                        item.setBackground(QtGui.QColor("white"))  
                        self.match_to_color[item.text()] = QtGui.QColor("white")
                        self.replace_text = pd.concat([self.replace_text, pd.DataFrame({text: self.data1[item.toolTip()].iloc[:].to_list()})], axis=1)
                        #replace nans with empty strings
                        self.replace_text = self.replace_text.replace({pd.NA: ''})
                    if not matched and not check:
                        item.setBackground(QtGui.QColor("white"))  
                        self.match_to_color[item.text()] = QtGui.QColor("white")
                        
        self.adding_different_data = True 
        #O(n) to clear set
        self.store.clear()
    def show_popup(self):
        dialog = QtWidgets.QDialog()
        dialog.setWindowTitle("Updated Excel Contents")
        dialog.resize(800, 600)

        # Create a main layout and table layout
        layout = QtWidgets.QVBoxLayout(dialog)
        self.table = QtWidgets.QTableWidget(dialog)

        #Save the updated Excel file
        self.saveCopy = QtWidgets.QPushButton(dialog)
        self.saveCopy.setText("Download Updated Excel File")
        self.saveCopy.clicked.connect(lambda: self.replace_text.to_excel("Updated_Excel.xlsx", index=False))

        # Set the number of rows and columns
        self.table.setRowCount(self.replace_text.shape[0])
        self.table.setColumnCount(self.replace_text.shape[1])

        # Set the table headers
        self.table.setHorizontalHeaderLabels(self.replace_text.columns.tolist())
        layout.addWidget(self.table)
        layout.addWidget(self.saveCopy)

        #Populate the table with the data
        for i in range(self.replace_text.shape[0]):
            for j in range(self.replace_text.shape[1]):
                self.table.setItem(i, j, QtWidgets.QTableWidgetItem(str(self.replace_text.iat[i, j])))

        # Adjust the table to fit the content
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)

        dialog.exec_()

    def replace_excel(self):
        # Threading for computational process to handle background tasks without suspending GUI
        threading.Thread(target=self.run_replace_excel).start()

    def run_replace_excel(self):
        if (self.data1.empty or self.data2.empty or self.replace_text.empty):
            return
        #Display recent new data and update the UI thread
        self.update_ui_signal.emit()

    def show_column_data(self, item, data):
        # Get the full header from the tooltip
        header = item.toolTip()
        column_data = data[header].tolist()
        dialog = QtWidgets.QDialog()
        dialog.setWindowTitle(f"Data for column '{header}'")
        dialog.resize(800, 600)

        layout = QtWidgets.QVBoxLayout(dialog)
        table = CustomTableWidget(dialog)
        table.setRowCount(len(column_data))
        table.setColumnCount(1)
        table.setHorizontalHeaderLabels([f"{header}"])
        layout.addWidget(table)
        seen_once = set()
        #Populate the table with the data
        for i, col_header in enumerate(column_data):
            item = QtWidgets.QTableWidgetItem(str(col_header))
            item.setToolTip(str(col_header))  # Set the full header as the tooltip
            #Filter out the nan values and duplicates
            if item.text() != 'nan' and item.text() not in seen_once:
                seen_once.add(item.text())
                table.setItem(i, 0, item)
        
        # Adjust the table to fit the content
        table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        dialog.exec_()


    # Update data to reflect the correct match
    def update_matches(self, item):
        # Create a dialog for the dropdown menu
        dialog = QtWidgets.QDialog()
        dialog.setWindowTitle("Select Match")
        layout = QtWidgets.QVBoxLayout(dialog)

        # Create the QComboBox and add relevant matches
        self.select_matching = QtWidgets.QComboBox(dialog)
        self.select_matching.addItem("Select a match")  # Default item
        for match in self.matches:
            if match.match is not None and match.match != item.text():
                self.select_matching.addItem(match.match)

        layout.addWidget(self.select_matching)

        # Position the dialog relative to the item
        rect = self.table1.visualItemRect(item)
        point = self.table1.viewport().mapToGlobal(rect.topLeft())
        dialog.move(point)

        # Connect the selection change signal
        self.select_matching.currentIndexChanged.connect(lambda: self.choose_match(item))
        dialog.exec_()
        dialog.close()

    def choose_match(self, item):
        match = self.select_matching.currentText()
        if match == "Select a match":
            return
        else:
            # Update the match in the matches list
            for match_obj in self.matches:
                if match_obj == item.text():
                    match_obj = match
                    break
            
            # Update the item's background color to match the new selection
            item.setBackground(self.match_to_color[match])

            # Realign the data in the tables
            self.realign_data()
            self.select_matching.parent().close()

    def realign_data(self):
        match_rows, unmatched_items, unmatched_items2, unmatched_item_color = self.collect_rows_by_background()

        new_table1_data, new_table2_data = self.prepare_new_data(match_rows, unmatched_items, unmatched_items2, unmatched_item_color)

        # Create new table1 with the new data in the main thread
        QtCore.QMetaObject.invokeMethod(self, "update_table1", QtCore.Qt.QueuedConnection,
                                        QtCore.Q_ARG(object, new_table1_data),
                                        QtCore.Q_ARG(object, new_table2_data))

    def collect_rows_by_background(self):
        match_rows = {}
        unmatched_items = []
        unmatched_items2 = []
        unmatched_items2_color = []

        # Collect rows by background color from table1
        for i in range(self.table1.rowCount()):
            item = self.table1.item(i, 0)
            if item and item.background().color() != QtGui.QColor("white"):
                bg_color = item.background().color().name()
                if bg_color not in match_rows:
                    match_rows[bg_color] = {'table1': [], 'table2': []}
                match_rows[bg_color]['table1'].append(item)
            else:
                unmatched_items.append(item)

        # Collect rows by background color from table2
        for i in range(self.table2.rowCount()):
            item = self.table2.item(i, 0)
            if item and item.background().color() != QtGui.QColor("white"):
                bg_color = item.background().color().name()
                if bg_color not in match_rows:
                    match_rows[bg_color] = {'table1': [], 'table2': []}
                match_rows[bg_color]['table2'].append(item)
                #Collect all non-white background colors in table2 that are not in table1
                if match_rows[bg_color]['table1'] == []:
                    unmatched_items2_color.append(item)
            else:
                unmatched_items2.append(item)


        return match_rows, unmatched_items, unmatched_items2, unmatched_items2_color

    def prepare_new_data(self, match_rows, unmatched_items, unmatched_items2, unmatched_items2_color):
        new_table1_data = []
        new_table2_data = []

        # Sort match rows by the background color to align exact matches together
        sorted_bg_colors = sorted(match_rows.keys())

        for bg_color in sorted_bg_colors:
            items = match_rows[bg_color]
            table1_items = items['table1']
            table2_items = items['table2']

            if table2_items and table1_items:
                # Align all items from table1 with the items from table2
                new_table1_data.extend(table1_items)
                new_table2_data.extend([table2_items[0]])

        # Append unmatched items at the end of new_table1_data
        new_table1_data.extend(unmatched_items)
        new_table2_data.extend(unmatched_items2_color)
        new_table2_data.extend(unmatched_items2)
        # new_table2_data.extend([QtWidgets.QTableWidgetItem()] * len(unmatched_items))

        return new_table1_data, new_table2_data

    @QtCore.pyqtSlot(object, object)
    def update_table1(self, new_table1_data, new_table2_data):
        new_table1 = CustomTableWidget(self.Dialog)
        new_table1.setMinimumSize(400, 200)
        new_table1.setColumnCount(1)
        new_table1.setRowCount(len(new_table1_data))
        for i, item in enumerate(new_table1_data):
            new_item = QtWidgets.QTableWidgetItem(item.text())
            new_item.setToolTip(item.toolTip())
            new_item.setBackground(item.background())
            new_table1.setItem(i, 0, new_item)
        new_table1.setHorizontalHeaderLabels([self.table1.horizontalHeaderItem(i).text() for i in range(self.table1.columnCount())])
        new_table1.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        new_table1.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        new_table1.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)

        new_table2 = CustomTableWidget(self.Dialog)
        new_table2.setMinimumSize(400, 200)
        new_table2.setColumnCount(1)
        new_table2.setRowCount(len(new_table2_data))
        for i, item in enumerate(new_table2_data):
            new_item = QtWidgets.QTableWidgetItem(item.text())
            new_item.setToolTip(item.toolTip())
            new_item.setBackground(item.background())
            new_table2.setItem(i, 0, new_item)
        new_table2.setHorizontalHeaderLabels([self.table2.horizontalHeaderItem(i).text() for i in range(self.table2.columnCount())])
        new_table2.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        new_table2.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        new_table2.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)

        # Clear the old layout and add the new tables
        self.tableLayout.removeWidget(self.table2)
        self.table2.deleteLater()
        self.table2 = CustomTableWidget(self.Dialog)
        self.table2.setParent(None)
        self.table2 = new_table2
        self.tableLayout.addWidget(self.table2)

        self.tableLayout.removeWidget(self.table1)
        self.table1.deleteLater()
        self.table1 = CustomTableWidget(self.Dialog)
        self.table1.setParent(None)
        self.table1 = new_table1
        self.tableLayout.addWidget(self.table1)

        self.connect_table1_events()

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

    def connect_table1_events(self):
        self.table1.ctrlClicked.connect(self.handle_table1_ctrl_click)


    def handle_table1_ctrl_click(self, item):
        self.update_matches(item)


    def connect_table1_events(self):
        self.table1.itemClicked.connect(self.handle_table1_cell_click)
        self.table1.ctrlClicked.connect(self.handle_table1_ctrl_click)

    def handle_table1_ctrl_click(self, item):
        self.update_matches(item)

    def handle_table1_cell_click(self, item):
        self.show_column_data(item, self.data1)
        



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_Dialog()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())