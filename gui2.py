import sys
import re
from PyQt5 import QtCore, QtGui, QtWidgets
import pandas as pd
from match_test import find_matches


class Worker(QtCore.QObject):
    dataReady = QtCore.pyqtSignal(object)

    def __init__(self, file_path):
        super().__init__()
        self.file = file_path

    @QtCore.pyqtSlot()
    def process_data(self):
        self.file = QtWidgets.QFileDialog.getOpenFileName(None, 'Open File', '', 'Excel files (*.xlsx)')[0]
        if self.file:
            df = pd.read_excel(self.file)
            self.dataReady.emit(df)

class DashBoard(QtCore.QObject):

    def __init__(self):
        super().__init__()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.main_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.top_layout = QtWidgets.QHBoxLayout()
        self.table_layout = QtWidgets.QHBoxLayout()

        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(330, 250, 113, 32))
        self.pushButton.setText("Select Excel File")
        self.top_layout.addWidget(self.pushButton)

        # Dropdown to select metadata form
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.addItem("NBISC Intake Form") 
        self.comboBox.addItem("ODIC")  
        self.top_layout.addWidget(self.comboBox)

        
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.table_layout.addWidget(self.tableWidget)

        self.main_layout.addLayout(self.top_layout)
        self.main_layout.addLayout(self.table_layout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.pushButton.clicked.connect(self.select_file)

        #Select multiple columns to find matches
        self.columns = self.tableWidget.itemClicked.connect(self.get_columns)

        #Meta Data 
        file = "C:/Users/kayvo/Semantic-List-Matching-with-LLMs/output.xlsx"
        df = pd.read_excel(file)
        self.data2 = df 
        self.list2 = df.columns.astype(str).tolist()
        self.display_data(self.table2, self.data2, False)
        #Select metadata file
        self.comboBox.currentIndexChanged.connect(self.select_metadata)

        QtCore.QMetaObject.connectSlotsByName(MainWindow)
    
    def select_file(self):
        file_path = QtWidgets.QFileDialog.getOpenFileName(None, 'Open File', '', 'Excel files (*.xlsx)')[0]
        if file_path:
            self.start_thread(file_path)
    
    def start_thread(self, file_path):
        self.worker = Worker(file_path)
        self.thread = QtCore.QThread()
        self.worker.moveToThread(self.thread)
        self.worker.dataReady.connect(self.display_data)
        self.thread.started.connect(self.worker.process_data)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    @QtCore.pyqtSlot(object)
    def display_data(self, df):
        row, col = df.shape
        self.tableWidget.setRowCount(row)
        self.tableWidget.setColumnCount(col)
        self.tableWidget.setHorizontalHeaderLabels(df.columns.tolist())
        for i in range(row):
            for j in range(col):
                item = QtWidgets.QTableWidgetItem(str(df.iat[i, j]))
                item.setToolTip(str(df.iat[i, j]))
                self.tableWidget.setItem(i, j, item)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.tableWidget.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.tableWidget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
    def get_columns(self):
        items = self.tableWidget.selectedItems()
        columns = []
        for item in items:
            columns.append(item.text())
        print(columns)
    
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

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = DashBoard()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
