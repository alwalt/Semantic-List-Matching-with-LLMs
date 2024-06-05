import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView

class ExcelHeaderReader(QWidget):
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Excel Header Reader')
        self.setGeometry(100, 100, 800, 400)
        
        main_layout = QHBoxLayout()
        
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        
        self.btn = QPushButton('Open Excel File', self)
        self.btn.clicked.connect(self.showDialog)
        
        left_layout.addWidget(self.btn)
        
        self.tableWidget = QTableWidget()
        self.tableWidget.setMinimumSize(400, 200)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        right_layout.addWidget(self.tableWidget)
        
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 3)
        
        self.setLayout(main_layout)
        
    def showDialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Excel File", "", "Excel Files (*.xlsx);;All Files (*)", options=options)
        if fileName:
            self.readHeaders(fileName)
    
    def readHeaders(self, filePath):
        try:
            df = pd.read_excel(filePath)
            headers = df.columns.tolist()
            self.displayHeaders(headers)
        except Exception as e:
            error_dialog = QFileDialog()
            error_dialog.setWindowTitle("Error")
            error_dialog.setLabelText(f"Error: {str(e)}")
            error_dialog.exec_()
    
    def displayHeaders(self, headers):
        max_length = 50  # Maximum length of header to display
        self.tableWidget.setRowCount(len(headers))
        self.tableWidget.setColumnCount(1)
        self.tableWidget.setHorizontalHeaderLabels(['Headers that Need Matching'])
        for i, header in enumerate(headers):
            truncated_header = (header[:max_length] + '...') if len(header) > max_length else header
            item = QTableWidgetItem(truncated_header)
            item.setToolTip(header)  # Set the full header as the tooltip
            self.tableWidget.setItem(i, 0, item)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ExcelHeaderReader()
    ex.show()
    sys.exit(app.exec_())

