import sys
import os
import shutil
import glob
import enum
import re
from PyQt6 import uic, QtWidgets, QtCore
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QTabWidget
from PyQt6.QtCore import QUrl, QDir

VERSION = "1.3.3"

class MyType(enum.Enum):
    Copy = 1
    Move = 2

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        self.setWindowTitle("Tool chọn file " + VERSION)
        uic.loadUi("gui2.ui",self)
        self.tabWidget.tabBarClicked.connect(self.handle_tabbar_clicked)
        #panel 1
        self.browse.clicked.connect(self.browsefiles)
        self.btn_Copy.clicked.connect(self.Copy)
        self.btn_Cancel.clicked.connect(self.Cancel)
        self.actionInfo.triggered.connect(self.menu)
        self.btn_Move.clicked.connect(self.Move)
        #panel 2
        self.browse_2.clicked.connect(self.browseJPG)
        self.browse_3.clicked.connect(self.browseRAW)
        self.btn_OK_2.clicked.connect(self.OK)

    def handle_tabbar_clicked(self, index):
        print("page index: ", index)
# Panel 1 function
    def browsefiles(self):
        dir = QFileDialog.getExistingDirectoryUrl(self)
        self.m_url.setText(dir.toLocalFile())
        self.setComboBox()

    def selectFile(self):
        fileName = self.plainTextEdit.toPlainText()
        m_select = re.findall(r'\d+', fileName)
        return m_select

    def getFileList(self, m_list):
        m_extension = self.comboBox.currentText()
        return glob.glob(os.path.join(m_list, f"*.{m_extension}"))

    def setComboBox(self):
        dir = self.m_url.text()
        if not dir:
            self.errLog("Vui lòng chọn đường dẫn")
            return
        m_list = glob.glob(os.path.join(dir, "*"))
        m_extension = set()
        for file in m_list:
            if os.path.isfile(file):
                file_extension = os.path.splitext(file)[1][1:]
                if file_extension:
                    m_extension.add(file_extension)
        self.comboBox.clear()
        self.comboBox.addItems(list(m_extension))

    def menu(self):
        dialog = QMessageBox(parent=self)
        dialog.setText(f"Công cụ hỗ trợ lọc file phiên bản {VERSION}\nCopyright by Khoa Nguyen")
        dialog.setWindowTitle("Hỗ trợ")
        dialog.exec()

    def errLog(self, m_text):
        QMessageBox.critical(self, "Lỗi", m_text)

    def infoLog(self, m_text):
        QMessageBox.information(self, "Thông tin", m_text)

    def Cancel(self):
        widget.close()

    def Copy(self):
        self.filterFile(MyType.Copy)

    def Move(self):
        self.filterFile(MyType.Move)

    def filterFile(self, type):
        dir = self.m_url.text()
        folder_dir = os.path.join(dir, self.m_newFolder.text())
        if not os.path.isdir(folder_dir):
            os.mkdir(folder_dir)

        log_file_path = os.path.join(folder_dir, "log.txt")
        with open(log_file_path, "w") as f:
            f.write("-------------------------Log file-------------------------\n")

        m_select = self.selectFile()
        if not m_select:
            self.errLog("Không có file nào được chọn")
            return
        m_list = self.getFileList(dir)
        not_copied = []
        m_remain = m_select
        count = 0
        total_file = len(m_select)
        for i in m_select:
            found = False
            for j in m_list:
                if i in j:
                    try:
                        if type is MyType.Copy:
                            shutil.copyfile(j, os.path.join(folder_dir, os.path.basename(j)))
                        else:
                            shutil.move(j, os.path.join(folder_dir, os.path.basename(j)))
                        count += 1
                        m_remain.remove(i)
                        found = True
                    except:
                        not_copied.append(j)
                        with open(log_file_path, "a") as f:
                            if type is MyType.Copy:
                                f.write(f"{j} - Fail to copy\n")
                            else:
                                f.write(f"{j} - Fail to move\n")
                    break
            if not found:
                not_copied.append(i)
                with open(log_file_path, "a") as f:
                    f.write(f"{i} - File not found or duplicated\n")

        if not_copied:
            with open(log_file_path, "a") as f:
                f.write("The following files cannot be copied or moved\n")
                for i in not_copied:
                    f.write(f"{i}\n")

        if count == 0:
            self.errLog(f"Các file được chọn không tồn tại trong {dir}")
        else:
            if type is MyType.Copy:
                self.infoLog(f"Copy {count} file trong tổng số {total_file} đã chọn\nThư mục: {folder_dir}\nKiểm tra chi tiết trong thư mục log.txt")
            else:
                self.infoLog(f"Di chuyển {count} file trong tổng số {total_file} đã chọn\nThư mục chứa file đã di chuyển: {folder_dir}\nKiểm tra chi tiết trong thư mục log.txt")
# Panel 2 function
    def get_all_filenames(directory):
        filenames = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                filenames.append(file)
        return filenames
    
    def browseJPG(self):
        dir = QFileDialog.getExistingDirectoryUrl(self)
        self.m_url_2.setText(dir.toLocalFile())

    def browseRAW(self):
        dir = QFileDialog.getExistingDirectoryUrl(self)
        self.m_url_3.setText(dir.toLocalFile())
    
    def OK(self):
        dir_JPG = self.m_url_2.text()
        dir_RAW = self.m_url_3.text()
        list_JPG = self.get_all_filenames(dir_JPG)
        list_RAW = self.get_all_filenames(dir_RAW)
        folder_dir = os.path.join(dir_RAW, self.m_newFolder.text())
        JPG_list_without_extension = [os.path.splitext(file)[0]for file in list_JPG]
        for i in JPG_list_without_extension:
            for j in list_RAW:
                if i in j:
                    try:
                        shutil.copyfile(j, os.path.join(folder_dir, os.path.basename(j)))
                    except:
                        print("fail to copy ", i)
        
    
app=QApplication(sys.argv)
mainwindow=MainWindow()
widget=QtWidgets.QStackedWidget()
widget.addWidget(mainwindow)
widget.setFixedWidth(650)
widget.setFixedHeight(550)
widget.show()
sys.exit(app.exec())
