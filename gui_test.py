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

#Worker thread and slots in class for processing the matchings
class Worker(QtCore.QObject):
    progress_signal  = QtCore.pyqtSignal(int)
    is_finished = QtCore.pyqtSignal()
    emit_data = QtCore.pyqtSignal(tuple)
    def __init__(self, data1, data2, list1, list2, table1, table2, replace_text):
        super().__init__()
        self.data1 = data1
        self.data2 = data2
        self.list1 = list1
        self.list2 = list2
        self.table1 = table1
        self.table2 = table2
        self.matches = []
        self.replace_text = replace_text
        self.store = set()
        self.color_match = {}

    #Emit Data signal
    def process(self):
        #Returns the updated class data to the main thread
        self.emit_data.emit((self.table1, self.table2, self.replace_text, self.match_to_color, self.dict_matches, self.is_matched, self.matches))

    #Run the worker thread
    def run(self):
        self.run_highlighting()
        self.process()
    def run_highlighting(self):
        # Highlight the matches between the two files
        if self.data1.empty or self.data2.empty:
            self.is_finished.emit()
            return
        # Find matches between the twso file lists using LLM
        self.matches, self.dict_matches = find_matches(self.list1, self.list2, self.progress_signal)
        
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
        
        # Emit the signal to notify the main thread that the process is finished
        self.is_finished.emit()

    def highlight_text_lines(self, table, match_set, check):
            counter = 0 #Counter for position in table3
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
                                    self.insert_item_into_table(self.table2, counter, 1, item)
                                    counter += 1
                                    self.store.add(word)
                                    #Merge matched words to the updated Excel file
                                    self.replace_text = pd.concat([self.replace_text, pd.DataFrame({text: self.data1[item.toolTip()].iloc[:].to_list()})], axis=1)
                                    #replace nans with empty strings
                                    self.replace_text = self.replace_text.replace({pd.NA: ''}) 
                                break
                                
                        #Add the list to the updated Excel file if no match.
                        if not matched and check:
                            item.setBackground(QtGui.QColor("white"))  
                            # self.match_to_color[item.text()] = QtGui.QColor("white")
                            self.replace_text = pd.concat([self.replace_text, pd.DataFrame({text: self.data1[item.toolTip()].iloc[:].to_list()})], axis=1)
                            #replace nans with empty strings
                            self.replace_text = self.replace_text.replace({pd.NA: ''})
                        if not matched and not check:
                            item.setBackground(QtGui.QColor("white"))  
                            # self.match_to_color[item.text()] = QtGui.QColor("white")
                    # Processing events to update the UI
                    QtWidgets.QApplication.processEvents()    
            self.adding_different_data = True 
            #O(n) to clear set
            self.store.clear()

    def insert_item_into_table(self, table2, row, col, source):
        new_item = QtWidgets.QTableWidgetItem(source.text())
        new_item.setToolTip(source.toolTip())
        new_item.setBackground(source.background())
        table2.setItem(row, col, new_item)
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
        
        # Connect the signal to the slot
        self.update_ui_signal.connect(self.show_popup)
        self.is_matched = False
    def handle_data_emit(self, data):
        self.table1, self.table2, self.replace_text, self.match_to_color, self.dict_matches, self.is_matched, self.matches = data         
    def setupUi(self, Dialog):
        Dialog.setObjectName("Test")
        Dialog.resize(1000, 700)
        self.data_emit = QtCore.pyqtSignal(tuple) #Signal to emit data to the main thread
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

        #Add spacing
        self.tableLayout.addSpacing(100)

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

        #Progress Bar Widget
        self.progressBar = QtWidgets.QProgressBar(self.Dialog)
        self.progressBar.setValue(0)
        self.topLayout.addWidget(self.progressBar)


        self.mainLayout.addLayout(self.topLayout)
        self.mainLayout.addLayout(self.leftLayout)
        self.mainLayout.addLayout(self.rightLayout)
        self.mainLayout.addLayout(self.tableLayout)

            
        
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
        #Choose the new selected metadata file from the dropdown list
        if selected_metadata in metadata_files:
            file = metadata_files[selected_metadata]
            df = pd.read_excel(file)
            self.data2 = df 
            self.list2 = df.columns.astype(str).tolist()
            self.display_data(self.table2, self.data2, False)

    def display_data(self, table, data, check):
        table.clear()
        table.setRowCount(data.shape[1])
        if check:
            table.setHorizontalHeaderLabels(["Headers that Need Matching"])
            table.setColumnCount(1)
        else:
            table.setHorizontalHeaderLabels(["MetaData", "LLM Matches"])
            table.setColumnCount(2)

        #Populate the table with the data
        for i, header in enumerate(data.columns.tolist()):
            item = QtWidgets.QTableWidgetItem(header)
            item.setToolTip(header)  # Set the full header as the tooltip
            table.setItem(i, 0, item)
        
        #Adjusting the tables headers in case they don't appear
        if check:
            table.setHorizontalHeaderLabels(["Headers that Need Matching"])
            table.setColumnCount(1)
        else:
            table.setHorizontalHeaderLabels(["MetaData", "LLM Matches"])
            table.setColumnCount(2)

        # Adjust the table to fit the content
        table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

    def highlight_matches(self):
        #Creating a worker object and QThread
        self.worker = Worker(self.data1, self.data2, self.list1, self.list2, self.table1, self.table2, self.replace_text)
        self.thread = QtCore.QThread()
        self.worker.moveToThread(self.thread)

        #Connecting the signals and slots
        self.worker.progress_signal.connect(self.progressBar.setValue)
        self.worker.is_finished.connect(self.thread.quit)
        self.worker.is_finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.progressBar.close)
        #Reorder the matched highlighted data after thread is finished
        self.thread.finished.connect(self.realign_data)
        #Restart the progress bar after highlighting matches
        self.thread.finished.connect(self.restart_progress)

        #Run the worker object and thread while emitting_data to the main thread
        self.worker.emit_data.connect(self.handle_data_emit)
        self.thread.started.connect(self.worker.run)
        self.thread.start()
        
    #Restart the progress bar after highlighting matches
    def restart_progress(self):
        self.progressBar = QtWidgets.QProgressBar(self.Dialog)
        self.progressBar.setValue(0)
        self.topLayout.addWidget(self.progressBar)

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

        # Create the QComboBox and all possible matches
        self.select_matching = QtWidgets.QComboBox(dialog)
        self.select_matching.addItem("Select a match")  # Default item
        
        for i in range(self.table2.rowCount()):
            table2_item = self.table2.item(i, 0)
            self.select_matching.addItem(table2_item.text())
       

        layout.addWidget(self.select_matching)

        # Position the dialog relative to the item
        rect = self.table1.visualItemRect(item)
        point = self.table1.viewport().mapToGlobal(rect.topLeft())
        dialog.move(point)

        # Connect the selection change signal
        self.select_matching.currentIndexChanged.connect(lambda: self.choose_match(item))
        dialog.exec_()

    def choose_match(self, item):
        match = self.select_matching.currentText()
        if match == "Select a match":
            return
        else:
            # Update the item's background color to match the new selection
            rand = QtGui.QColor(QtCore.qrand() % 256, QtCore.qrand() % 256, QtCore.qrand() % 256)
            #Regenerate new seed if color already exists
           
            if self.match_to_color.get(match) == QtGui.QColor("white") or self.match_to_color.get(match) == None:
                for temp in self.match_to_color:
                    while rand == self.match_to_color[temp]:
                        rand = QtGui.QColor(QtCore.qrand() % 256, QtCore.qrand() % 256, QtCore.qrand() % 256)
                self.match_to_color[match] = rand
            else:
                rand = self.match_to_color[match]
            self.match_to_color[item.text()] = rand
            self.table2.item(self.select_matching.currentIndex()-1, 0).setBackground(self.match_to_color[match])
            item.setBackground(self.match_to_color[match])

            # Realign the data in the tables
            self.realign_data()
            # Close the dialog for selecting a match
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
                    self.match_to_color.pop(item.text())
                    item.setBackground(QtGui.QColor("white"))
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
        new_table1.setHorizontalHeaderLabels(["Headers that Need Matching"])
        new_table1.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        new_table1.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        new_table1.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)

        new_table2 = CustomTableWidget(self.Dialog)
        new_table2.setMinimumSize(400, 200)
        new_table2.setColumnCount(2)
        new_table2.setRowCount(len(new_table2_data))
        for i, item in enumerate(new_table2_data):
            new_item = QtWidgets.QTableWidgetItem(item.text())
            new_item.setToolTip(item.toolTip())
            new_item.setBackground(item.background())
            new_table2.setItem(i, 0, new_item)
        new_table2.setHorizontalHeaderLabels(["MetaData", "LLM Matches"])
        new_table2.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        new_table2.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        new_table2.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)

        # Clear the old tables and replace them with the new tables
        self.tableLayout.removeWidget(self.table1)
        self.tableLayout.removeWidget(self.table2)
        self.table1.deleteLater()
        self.table2.deleteLater()

        # Clear any spacing in the layout
        while self.tableLayout.count():
            item = self.tableLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.table2.setParent(None)
        self.table2 = new_table2
        
        #Set new_table1 data to the second column of table2 and populate table2
        self.populate_table2_col1(new_table1_data)
        self.tableLayout.addWidget(self.table2)
        
        #Add spacing
        self.tableLayout.addSpacing(50)
        self.table1.setParent(None)
        self.table1 = new_table1
        self.tableLayout.addWidget(self.table1)
        
        #Clear table1 background colors
        for i in range(self.table1.rowCount()):
            for j in range(self.table1.columnCount()):
                item = self.table1.item(i, j)
                if item:
                    item.setBackground(QtGui.QColor("white"))

        #Click once to display dropdown other potential matches of the selected item and ctrl + click for the matches
        self.connect_table1_events()


    def populate_table2_col1(self, data):
        for i, item in enumerate(data):
            new_item = QtWidgets.QTableWidgetItem(item.text())
            new_item.setToolTip(item.toolTip())
            new_item.setBackground(item.background())
            self.table2.setItem(i, 1, new_item)


    def handle_table1_ctrl_click(self, item):
        #Restore Table1 item's background color
        self.restore_table1_from_table3_colors()
        self.update_matches(item)
    


    def connect_table1_events(self):
        self.table1.itemClicked.connect(self.handle_table1_cell_click)
        self.table1.ctrlClicked.connect(self.handle_table1_ctrl_click)

    def handle_table1_cell_click(self, item):
        self.show_column_data(item, self.data1)

    #Restore Table1 from Table3 colors without deleting objects
    def restore_table1_from_table3_colors(self):
        for i in range(self.table2.rowCount()):
            for j in range(1, 2):
                source_item = self.table2.item(i, j)
                if source_item and source_item != QtGui.QColor("white"):
                    self.table1.item(i, j-1).setBackground(source_item.background())
        

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_Dialog()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())