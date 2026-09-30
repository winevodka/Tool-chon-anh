import sys
import os
import shutil
import glob
import enum
import re
from PyQt6 import uic, QtWidgets, QtCore
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QTabWidget
from PyQt6.QtCore import QUrl, QDir

VERSION = "1.4.1"

class MyType(enum.Enum):
    Copy = 1
    Move = 2

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        self.setWindowTitle("Tool chọn file " + VERSION)
        uic.loadUi("gui2.ui",self)
        # self.tabWidget.tabBarClicked.connect(self.handle_tabbar_clicked)
        #panel 1
        self.browse.clicked.connect(self.browsefiles)
        self.browse_4.clicked.connect(self.browseSaveFolder1)
        self.btn_Copy.clicked.connect(self.Copy)
        self.btn_Cancel.clicked.connect(self.Cancel)
        self.actionInfo.triggered.connect(self.menu)
        self.btn_Move.clicked.connect(self.Move)
        #panel 2
        self.browse_2.clicked.connect(self.browseJPG)
        self.browse_3.clicked.connect(self.browseRAW)
        self.browse_5.clicked.connect(self.browseSaveFolder2)
        self.btn_OK_2.clicked.connect(self.OK)

    # def handle_tabbar_clicked(self, index):
        # print("page index: ", index)

    def menu(self):
        dialog = QMessageBox(parent=self)
        dialog.setText(f"Công cụ hỗ trợ lọc file phiên bản {VERSION}\nCopyright by Khoa Nguyen")
        dialog.setWindowTitle("Hỗ trợ")
        dialog.exec()

    def errLog(self, m_text):
        QMessageBox.critical(self, "Lỗi", m_text)

    def infoLog(self, m_text):
        QMessageBox.information(self, "Thông tin", m_text)

# Panel 1 function
    def browsefiles(self):
        dir = QFileDialog.getExistingDirectoryUrl(self)
        self.m_url.setText(dir.toLocalFile())
        self.setComboBox()

    def browseSaveFolder1(self):
        dir = QFileDialog.getExistingDirectoryUrl(self)
        if dir.toLocalFile():
            self.m_newFolder.setText(dir.toLocalFile())

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

    def Cancel(self):
        widget.close()

    def Copy(self):
        self.filterFile(MyType.Copy)

    def Move(self):
        self.filterFile(MyType.Move)

    def filterFile(self, type):
        dir = self.m_url.text()
        if not dir or not os.path.isdir(dir):
            self.errLog("Vui lòng chọn đường dẫn thư mục gốc hợp lệ")
            return
        folder_dir = self.m_newFolder.text().strip()
        if not folder_dir:
            self.errLog("Vui lòng chọn thư mục lưu")
            return

        if not os.path.isdir(folder_dir):
            os.makedirs(folder_dir)

        log_file_path = os.path.join(folder_dir, "log.txt")
        with open(log_file_path, "w", encoding="utf-8") as f:
            f.write("-------------------------Panel 1-------------------------\n")

        m_select = self.selectFile()
        if not m_select:
            self.errLog("Không có file nào được chọn")
            return
        m_list = self.getFileList(dir)
        if not m_list:
            self.errLog("Không tìm thấy file nào với định dạng đã chọn")
            return

        count = 0
        for i in m_select:
            # Chỉ khớp với các số cuối của phần tên file (bỏ phần mở rộng),
            # tránh việc số nhập vào trùng ngẫu nhiên ở giữa tên file hoặc đường dẫn.
            matches = []
            for j in m_list:
                base_name = os.path.splitext(os.path.basename(j))[0]
                digits = re.findall(r'\d+', base_name)
                number_part = digits[-1] if digits else ""
                if number_part.endswith(i):
                    matches.append(j)

            if not matches:
                with open(log_file_path, "a", encoding="utf-8") as f:
                    f.write(f"{i} - Not found\n")
                continue
            if len(matches) > 1:
                names = ", ".join(os.path.basename(m) for m in matches)
                with open(log_file_path, "a", encoding="utf-8") as f:
                    f.write(f"{i} - Duplicate, tìm thấy nhiều file trùng khớp ({names}), vui lòng nhập thêm số để phân biệt\n")
                continue

            j = matches[0]
            try:
                if type == MyType.Copy:
                    shutil.copyfile(j, os.path.join(folder_dir, os.path.basename(j)))
                else:
                    shutil.move(j, os.path.join(folder_dir, os.path.basename(j)))
                with open(log_file_path, "a", encoding="utf-8") as f:
                    f.write(f"{j} - Success \n")
                count += 1
            except Exception as e:
                action = "copy" if type == MyType.Copy else "move"
                with open(log_file_path, "a", encoding="utf-8") as f:
                    f.write(f"{j} - Fail to {action}: {str(e)}\n")

        if type == MyType.Copy:
            self.infoLog(f"Copy hoàn tất {count} / {len(m_select)}\nThư mục: {folder_dir}\nKiểm tra chi tiết trong tệp log.txt")
        else:
            self.infoLog(f"Di chuyển hoàn tất {count} / {len(m_select)}\nThư mục chứa file đã di chuyển: {folder_dir}\nKiểm tra chi tiết trong tệp log.txt")

# Panel 2 function
    JPG_EXTENSIONS = {"jpg", "jpeg"}

    def get_all_files(self, directory, exclude_dir=None):
        """Trả về danh sách đường dẫn đầy đủ của toàn bộ file trong directory (bao gồm thư mục con),
        bỏ qua exclude_dir (thường là thư mục đích vừa tạo để không quét lại file đã copy)."""
        result = []
        exclude_dir = os.path.abspath(exclude_dir) if exclude_dir else None
        for root, dirs, files in os.walk(directory):
            if exclude_dir and os.path.abspath(root) == exclude_dir:
                dirs[:] = []
                continue
            if exclude_dir:
                dirs[:] = [d for d in dirs if os.path.abspath(os.path.join(root, d)) != exclude_dir]
            for file in files:
                result.append(os.path.join(root, file))
        return result

    def browseJPG(self):
        dir = QFileDialog.getExistingDirectoryUrl(self)
        self.m_url_2.setText(dir.toLocalFile())
        mdir = self.m_url_2.text()
        if not mdir:
            self.errLog("Vui lòng chọn đường dẫn")
            return

    def browseRAW(self):
        dir = QFileDialog.getExistingDirectoryUrl(self)
        self.m_url_3.setText(dir.toLocalFile())

    def browseSaveFolder2(self):
        dir = QFileDialog.getExistingDirectoryUrl(self)
        if dir.toLocalFile():
            self.m_newFolder_2.setText(dir.toLocalFile())

    def OK(self):
        dir_JPG = self.m_url_2.text()
        dir_RAW = self.m_url_3.text()
        if not dir_JPG or not os.path.isdir(dir_JPG):
            self.errLog("Vui lòng chọn đường dẫn thư mục JPG đã lọc hợp lệ")
            return
        if not dir_RAW or not os.path.isdir(dir_RAW):
            self.errLog("Vui lòng chọn đường dẫn thư mục RAW cần lọc hợp lệ")
            return
        folder_dir = self.m_newFolder_2.text().strip()
        if not folder_dir:
            self.errLog("Vui lòng chọn thư mục lưu")
            return

        folder_dir = os.path.abspath(folder_dir)
        if not os.path.isdir(folder_dir):
            os.makedirs(folder_dir)

        list_JPG = self.get_all_files(dir_JPG, exclude_dir=folder_dir)
        list_JPG = [f for f in list_JPG if os.path.splitext(f)[1][1:].lower() in self.JPG_EXTENSIONS]
        if not list_JPG:
            self.errLog("Không tìm thấy file JPG nào trong thư mục đã lọc")
            return
        list_RAW = self.get_all_files(dir_RAW, exclude_dir=folder_dir)

        # Thư mục RAW gốc có thể chứa cả file RAW lẫn file JPG (raw + jpg),
        # nên chỉ lấy các file KHÔNG phải JPG để tránh copy nhầm ảnh JPG đã có sẵn.
        raw_by_basename = {}
        for raw_path in list_RAW:
            ext = os.path.splitext(raw_path)[1][1:].lower()
            if ext in self.JPG_EXTENSIONS:
                continue
            base_name = os.path.splitext(os.path.basename(raw_path))[0]
            raw_by_basename.setdefault(base_name, []).append(raw_path)

        if not raw_by_basename:
            self.errLog("Không tìm thấy file RAW nào trong thư mục nguồn (thư mục chỉ toàn file JPG)")
            return

        log_file_path = os.path.join(folder_dir, "log.txt")
        with open(log_file_path, "w", encoding="utf-8") as f:
            f.write("-------------------------Panel 2-------------------------\n")

        count = 0
        for jpg_path in list_JPG:
            base_name = os.path.splitext(os.path.basename(jpg_path))[0]
            matches = raw_by_basename.get(base_name, [])
            if not matches:
                with open(log_file_path, "a", encoding="utf-8") as f:
                    f.write(f"{base_name} - Not found\n")
                continue

            success = False
            for raw_path in matches:
                try:
                    shutil.copyfile(raw_path, os.path.join(folder_dir, os.path.basename(raw_path)))
                    with open(log_file_path, "a", encoding="utf-8") as f:
                        f.write(f"{raw_path} - Success \n")
                    success = True
                except Exception as e:
                    with open(log_file_path, "a", encoding="utf-8") as f:
                        f.write(f"{raw_path} - Fail {str(e)} \n")
            if success:
                count += 1

        self.infoLog(f"Hoàn thành {count} / {len(list_JPG)} trong tổng số {len(list_RAW)} files\nThư mục: {folder_dir}\nKiểm tra chi tiết trong tệp log.txt")
    
app=QApplication(sys.argv)
mainwindow=MainWindow()
widget=QtWidgets.QStackedWidget()
widget.addWidget(mainwindow)
widget.setFixedWidth(650)
widget.setFixedHeight(550)
widget.show()
sys.exit(app.exec())
