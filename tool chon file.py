import sys
from PyQt6 import uic, QtWidgets
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
import os
import re
import shutil
import enum

VERSION = "1.3.1"

class MyType (enum.Enum):
    Copy = 1
    Move = 2
    
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        self.setWindowTitle("Tool chọn file " + VERSION)
        uic.loadUi("gui.ui",self)
        self.browse.clicked.connect(self.browsefiles)
        self.btn_Copy.clicked.connect(self.Copy)
        self.btn_Cancel.clicked.connect(self.Cancel)
        self.actionInfo.triggered.connect(self.menu)
        self.btn_Move.clicked.connect(self.Move)

    #browse đến thư mục chứa ảnh gốc
    def browsefiles(self):
        fname = QFileDialog.getExistingDirectory(self)
        self.m_url.setText(fname)
        self.setComboBox()


    def selectFile(self):
        fileName = self.plainTextEdit.toPlainText()
        m_select = re.findall(r'\d+', fileName)
        return m_select


    def getFileExtension(self, m_list):
        myset = set()
        for i in m_list:
            if "." in i:
                file_extension = i.split(".")[-1]
                if file_extension not in myset:
                    myset.add(file_extension)
        return list(myset)


    def getAllFileList(self):
        dir = self.m_url.text()
        if not dir:
            self.errLog("Vui lòng chọn đường dẫn")
            return []
        fileList = os.listdir(dir)
        return fileList


    def getFileList(self, m_list):
        m_extension = self.comboBox.currentText()
        return [i for i in m_list if m_extension in i]


    def setComboBox(self):
        allFile = self.getAllFileList()
        mlist = self.getFileExtension(allFile)
        self.comboBox.addItems(mlist)


    def menu(self):
        dialog = QMessageBox(parent=self)
        dialog.setText(f"Công cụ hỗ trợ lọc file phiên bản {VERSION}\nCopyright by Khoa Nguyen")
        dialog.setWindowTitle("Hỗ trợ")
        dialog.exec()


    def errLog(self, m_text):
        dialog = QMessageBox(parent=self)
        dialog.setText(m_text)
        dialog.setWindowTitle("Lỗi")
        dialog.exec()


    def infoLog(self, m_text):
        dialog = QMessageBox(parent=self)
        dialog.setText(m_text)
        dialog.setWindowTitle("Thông tin")
        dialog.exec()

    def Cancel(self):
        widget.close()

    def Copy(self):
        self.filterFile(MyType.Copy)

    def Move(self):
        self.filterFile(MyType.Move)

    def filterFile(self, type):
        dir = self.m_url.text()
        folder_dir = f"{dir} {self.m_newFolder.text()}"
        if not os.path.isdir(folder_dir):
            os.mkdir(folder_dir)
        m_select = self.selectFile()
        if not m_select:
            self.errLog("Không có file nào được chọn")
            return
        allFile = self.getAllFileList()
        m_list = self.getFileList(allFile)
        count = 0
        for i in m_select:
            for j in m_list:
                if i in j:
                    if type is MyType.Copy:
                        shutil.copyfile(f"{dir}/{j}", f"{folder_dir}/{j}")
                    else:
                        shutil.move(f"{dir}/{j}", f"{folder_dir}/{j}")
                    count += 1
                    break
        if count == 0:
            self.errLog(f"Các file được chọn không tồn tại trong {dir}")
        else:
            if type is MyType.Copy:
                self.infoLog(f"Copy {count} file trong tổng số {len(m_select)} đã chọn \nThư mục: {folder_dir}")
            else:
                self.infoLog(f"Loại bỏ {count} file trong tổng số {len(m_select)} đã chọn \nThư mục chứa file đã loại bỏ: {folder_dir}")

app=QApplication(sys.argv)
mainwindow=MainWindow()
widget=QtWidgets.QStackedWidget()
widget.addWidget(mainwindow)
widget.setFixedWidth(550)
widget.setFixedHeight(400)
widget.show()
sys.exit(app.exec())