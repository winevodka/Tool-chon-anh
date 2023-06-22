import sys
from PyQt6 import uic, QtWidgets
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
import os
import re
import shutil
import enum

VERSION = "1.3.0"

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
        fname=QFileDialog.getExistingDirectory(self)
        self.m_url.setText(str(fname))
        self.setComboBox()

    def selectFile(self):
        fileName = str(self.plainTextEdit.toPlainText())
        m_select = re.findall(r'\d+', str(fileName))
        return m_select

    def getFileExtension(self, m_list):
        myset = []
        for i in m_list:
            if "." in i:
                split_tup = i.split(".")
                file_extension = split_tup[1]
            if file_extension not in myset :
                myset.append(file_extension)
        return myset
    
        #get all file in folder
    def getAllFileList(self):
        dir = self.m_url.text()
        if dir == "" :
            self.errLog("Vui lòng chọn đường dẫn")
            return 0
        # print(dir)
        fileList = os.listdir(dir)
        return fileList
    
    #get file list with extension
    def getFileList(self, m_list):
        mlist = []
        m_extension = self.comboBox.currentText()
        for i in m_list:
            if m_extension in i:
                mlist.append(i)
        return mlist

    def setComboBox(self):
        allFile = self.getAllFileList()
        # print("all file = ", allFile)
        mlist = self.getFileExtension(allFile)
        for a in mlist:
            self.comboBox.addItem(str(a))

    def menu(self):
        dialog = QMessageBox(parent=self, text="Công cụ hỗ trợ lọc file phiên bản " + VERSION + "\nCopyright by Khoa Nguyen")
        dialog.setWindowTitle("Hỗ trợ")
        ret = dialog.exec()

    def errLog(self, m_text):
        dialog = QMessageBox(parent=self, text= m_text)
        dialog.setWindowTitle("Lỗi")
        ret = dialog.exec()

    def infoLog(self, m_text):
        dialog = QMessageBox(parent=self, text= m_text)
        dialog.setWindowTitle("Thông tin")
        ret = dialog.exec()

    def Cancel(self):
        widget.close()

    def Copy(self):
        self.filterFile(MyType.Copy)
    def Move(self):
        self.filterFile(MyType.Move)

    def filterFile(self, type):
        dir = None
        dir = self.m_url.text()
        folder_dir = dir + " " + self.m_newFolder.text()
        isExist = os.path.isdir(folder_dir)
        if isExist == False:
            # print("tạo thư mục")
            os.mkdir(folder_dir)
        m_select = self.selectFile()
        if m_select == []:
            self.errLog("Không có file nào được chọn")
            return 0
        allFile = self.getAllFileList()
        m_list = self.getFileList(allFile)

        if type is MyType.Copy:
            count = 0
            for i in m_select:
                for j in m_list:
                    if i in j:
                        shutil.copyfile(dir+"/"+j, folder_dir+"/"+j)
                        count = count + 1
                        break
            if count == 0:
                self.errLog("Các file được chọn không tồn tại trong " + dir)
            else: 
                self.infoLog("Copy " + str(count) + " file trong tổng số " + str(len(m_select)) + " đã chọn \n" + "Thư mục: " + folder_dir)
        elif type is MyType.Move:
            count = 0
            for i in m_select:
                for j in m_list:
                    if i in j:
                        shutil.move(dir+"/"+j, folder_dir+"/"+j)
                        count = count + 1
                        break
            if count == 0:
                self.errLog("Các file được chọn không tồn tại trong " + dir)
            else: 
                self.infoLog("Loai bo " + str(count) + " file trong tổng số " + str(len(m_select)) + " đã chọn \n" + "Thư mục chua file da loai bo: " + folder_dir)         

app=QApplication(sys.argv)
mainwindow=MainWindow()
widget=QtWidgets.QStackedWidget()
widget.addWidget(mainwindow)
widget.setFixedWidth(550)
widget.setFixedHeight(400)
widget.show()
sys.exit(app.exec())