import sys
import os
import shutil
import glob
import enum
import re
from PyQt6 import uic, QtWidgets, QtCore
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QTabWidget
from PyQt6.QtCore import QUrl, QDir, QSettings, QEvent, Qt

VERSION = "1.4.1"
ORG_NAME = "KhoaNguyen"
APP_NAME = "ToolChonFile"

class MyType(enum.Enum):
    Copy = 1
    Move = 2

class LogDialog(QtWidgets.QDialog):
    """Hộp thoại hiển thị kết quả và nội dung log.txt ngay trong ứng dụng."""
    def __init__(self, parent, title, summary, log_file_path, folder_dir):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(600, 400)
        self.folder_dir = folder_dir

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel(summary))

        self.text_edit = QtWidgets.QTextEdit()
        self.text_edit.setReadOnly(True)
        try:
            with open(log_file_path, "r", encoding="utf-8") as f:
                self.text_edit.setPlainText(f.read())
        except Exception:
            self.text_edit.setPlainText("Không thể đọc tệp log.")
        layout.addWidget(self.text_edit)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_open_folder = QtWidgets.QPushButton("Mở thư mục kết quả")
        btn_open_folder.clicked.connect(self.openFolder)
        btn_layout.addWidget(btn_open_folder)
        btn_layout.addStretch()
        btn_close = QtWidgets.QPushButton("Đóng")
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)

    def openFolder(self):
        try:
            os.startfile(self.folder_dir)
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể mở thư mục: {str(e)}")

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        self.setWindowTitle("Tool chọn file " + VERSION)
        ui_path = os.path.join(getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__))), "gui2.ui")
        uic.loadUi(ui_path, self)
        # self.tabWidget.tabBarClicked.connect(self.handle_tabbar_clicked)

        self.settings = QSettings(ORG_NAME, APP_NAME)

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

        # Gợi ý nhập liệu
        self.plainTextEdit.setPlaceholderText(
            "Nhập số thứ tự ảnh cần copy/move, cách nhau bằng dấu phẩy hoặc xuống dòng.\nVí dụ: 345, 346, 347"
        )
        self.m_url.setToolTip("Thư mục gốc chứa ảnh (có thể kéo-thả thư mục vào đây)")
        self.m_newFolder.setToolTip("Thư mục sẽ lưu ảnh được copy/move (có thể kéo-thả thư mục vào đây)")
        self.m_url_2.setToolTip("Thư mục chứa ảnh JPG đã lọc (có thể kéo-thả thư mục vào đây)")
        self.m_url_3.setToolTip("Thư mục chứa ảnh RAW gốc cần lọc (có thể kéo-thả thư mục vào đây)")
        self.m_newFolder_2.setToolTip("Thư mục sẽ lưu ảnh RAW được copy (có thể kéo-thả thư mục vào đây)")

        # Cho phép kéo-thả thư mục vào các ô đường dẫn
        self._drop_targets = [self.m_url, self.m_newFolder, self.m_url_2, self.m_url_3, self.m_newFolder_2]
        for w in self._drop_targets:
            w.setAcceptDrops(True)
            w.installEventFilter(self)

        # Xem trước số lượng file tìm thấy
        self.comboBox.currentTextChanged.connect(self.updatePreviewPanel1)
        self.m_url_2.textChanged.connect(self.updatePreviewPanel2)
        self.m_url_3.textChanged.connect(self.updatePreviewPanel2)

        self.setMinimumSize(650, 550)

        self.loadSettings()

    # def handle_tabbar_clicked(self, index):
        # print("page index: ", index)

    def loadSettings(self):
        self.m_url.setText(self.settings.value("panel1/url", ""))
        self.m_newFolder.setText(self.settings.value("panel1/newFolder", ""))
        self.m_url_2.setText(self.settings.value("panel2/urlJPG", ""))
        self.m_url_3.setText(self.settings.value("panel2/urlRAW", ""))
        self.m_newFolder_2.setText(self.settings.value("panel2/newFolder", ""))
        if self.m_url.text() and os.path.isdir(self.m_url.text()):
            self.setComboBox()

    def saveSettings(self):
        self.settings.setValue("panel1/url", self.m_url.text())
        self.settings.setValue("panel1/newFolder", self.m_newFolder.text())
        self.settings.setValue("panel2/urlJPG", self.m_url_2.text())
        self.settings.setValue("panel2/urlRAW", self.m_url_3.text())
        self.settings.setValue("panel2/newFolder", self.m_newFolder_2.text())

    def eventFilter(self, obj, event):
        if obj in getattr(self, "_drop_targets", []):
            event_type = event.type()
            if event_type in (QEvent.Type.DragEnter, QEvent.Type.DragMove):
                mime = event.mimeData()
                if mime.hasUrls() and any(u.isLocalFile() and os.path.isdir(u.toLocalFile()) for u in mime.urls()):
                    event.acceptProposedAction()
                    return True
                return False
            if event_type == QEvent.Type.Drop:
                mime = event.mimeData()
                if mime.hasUrls():
                    for u in mime.urls():
                        if u.isLocalFile() and os.path.isdir(u.toLocalFile()):
                            obj.setText(u.toLocalFile())
                            if obj is self.m_url:
                                self.setComboBox()
                            event.acceptProposedAction()
                            return True
                return False
        return super().eventFilter(obj, event)

    def updatePreviewPanel1(self):
        dir = self.m_url.text()
        ext = self.comboBox.currentText()
        if not dir or not os.path.isdir(dir) or not ext:
            return
        count = len(glob.glob(os.path.join(dir, f"*.{ext}")))
        self.statusBar().showMessage(f"Tìm thấy {count} file .{ext} trong thư mục gốc")

    def updatePreviewPanel2(self):
        dir_JPG = self.m_url_2.text()
        dir_RAW = self.m_url_3.text()
        msgs = []
        if dir_JPG and os.path.isdir(dir_JPG):
            count_jpg = len([f for f in self.get_all_files(dir_JPG) if os.path.splitext(f)[1][1:].lower() in self.JPG_EXTENSIONS])
            msgs.append(f"{count_jpg} file JPG")
        if dir_RAW and os.path.isdir(dir_RAW):
            count_raw = len([f for f in self.get_all_files(dir_RAW) if os.path.splitext(f)[1][1:].lower() not in self.JPG_EXTENSIONS])
            msgs.append(f"{count_raw} file RAW")
        if msgs:
            self.statusBar().showMessage("Tìm thấy " + ", ".join(msgs))

    def confirmOverwrite(self, folder_dir, filenames):
        """Kiểm tra file trùng tên đã tồn tại ở thư mục đích.
        Trả về None nếu người dùng hủy thao tác, ngược lại trả về tập tên file cần bỏ qua (có thể rỗng)."""
        existing = [name for name in filenames if os.path.isfile(os.path.join(folder_dir, name))]
        if not existing:
            return set()
        sample = "\n".join(existing[:10])
        more = f"\n... và {len(existing) - 10} file khác" if len(existing) > 10 else ""
        reply = QMessageBox.question(
            self,
            "File đã tồn tại",
            f"Phát hiện {len(existing)} file đã tồn tại trong thư mục đích:\n{sample}{more}\n\n"
            "Chọn 'Yes' để ghi đè, 'No' để bỏ qua (giữ nguyên file cũ), 'Cancel' để hủy toàn bộ thao tác.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Cancel:
            return None
        if reply == QMessageBox.StandardButton.No:
            return set(existing)
        return set()

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
        if dir.toLocalFile():
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
        reply = QMessageBox.question(
            self,
            "Xác nhận di chuyển",
            "Thao tác Move sẽ XÓA file khỏi thư mục gốc sau khi chuyển sang thư mục đích.\nBạn có chắc chắn muốn tiếp tục?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
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

        m_select = self.selectFile()
        if not m_select:
            self.errLog("Không có file nào được chọn")
            return
        m_list = self.getFileList(dir)
        if not m_list:
            self.errLog("Không tìm thấy file nào với định dạng đã chọn")
            return

        planned = []
        not_found = []
        duplicate = []
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
                not_found.append(i)
            elif len(matches) > 1:
                duplicate.append((i, matches))
            else:
                planned.append((i, matches[0]))

        if not os.path.isdir(folder_dir):
            os.makedirs(folder_dir)

        skip_names = self.confirmOverwrite(folder_dir, [os.path.basename(p) for _, p in planned])
        if skip_names is None:
            return

        log_file_path = os.path.join(folder_dir, "log.txt")
        with open(log_file_path, "w", encoding="utf-8") as f:
            f.write("-------------------------Panel 1-------------------------\n")
            for i in not_found:
                f.write(f"{i} - Not found\n")
            for i, matches in duplicate:
                names = ", ".join(os.path.basename(m) for m in matches)
                f.write(f"{i} - Duplicate, tìm thấy nhiều file trùng khớp ({names}), vui lòng nhập thêm số để phân biệt\n")

        count = 0
        if planned:
            action_label = "Đang copy" if type == MyType.Copy else "Đang di chuyển"
            progress = QtWidgets.QProgressDialog(f"{action_label} file...", "Hủy", 0, len(planned), self)
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setMinimumDuration(300)

            for idx, (i, j) in enumerate(planned):
                progress.setValue(idx)
                progress.setLabelText(f"{action_label}: {os.path.basename(j)}")
                QApplication.processEvents()
                if progress.wasCanceled():
                    with open(log_file_path, "a", encoding="utf-8") as f:
                        f.write("Thao tác bị hủy bởi người dùng\n")
                    break

                dest_name = os.path.basename(j)
                if dest_name in skip_names:
                    with open(log_file_path, "a", encoding="utf-8") as f:
                        f.write(f"{j} - Skipped (giữ nguyên file cũ)\n")
                    continue

                try:
                    if type == MyType.Copy:
                        shutil.copyfile(j, os.path.join(folder_dir, dest_name))
                    else:
                        shutil.move(j, os.path.join(folder_dir, dest_name))
                    with open(log_file_path, "a", encoding="utf-8") as f:
                        f.write(f"{j} - Success \n")
                    count += 1
                except Exception as e:
                    action = "copy" if type == MyType.Copy else "move"
                    with open(log_file_path, "a", encoding="utf-8") as f:
                        f.write(f"{j} - Fail to {action}: {str(e)}\n")
            progress.setValue(len(planned))

        verb = "Copy" if type == MyType.Copy else "Di chuyển"
        summary = f"{verb} hoàn tất {count} / {len(m_select)}\nThư mục: {folder_dir}"
        LogDialog(self, "Kết quả", summary, log_file_path, folder_dir).exec()

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
        if dir.toLocalFile():
            self.m_url_2.setText(dir.toLocalFile())

    def browseRAW(self):
        dir = QFileDialog.getExistingDirectoryUrl(self)
        if dir.toLocalFile():
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

        planned = []
        not_found = []
        for jpg_path in list_JPG:
            base_name = os.path.splitext(os.path.basename(jpg_path))[0]
            matches = raw_by_basename.get(base_name, [])
            if not matches:
                not_found.append(base_name)
            else:
                planned.extend(matches)

        if not os.path.isdir(folder_dir):
            os.makedirs(folder_dir)

        skip_names = self.confirmOverwrite(folder_dir, [os.path.basename(p) for p in planned])
        if skip_names is None:
            return

        log_file_path = os.path.join(folder_dir, "log.txt")
        with open(log_file_path, "w", encoding="utf-8") as f:
            f.write("-------------------------Panel 2-------------------------\n")
            for name in not_found:
                f.write(f"{name} - Not found\n")

        succeeded_raw = set()
        if planned:
            progress = QtWidgets.QProgressDialog("Đang copy file RAW...", "Hủy", 0, len(planned), self)
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setMinimumDuration(300)

            for idx, raw_path in enumerate(planned):
                progress.setValue(idx)
                progress.setLabelText(f"Đang copy: {os.path.basename(raw_path)}")
                QApplication.processEvents()
                if progress.wasCanceled():
                    with open(log_file_path, "a", encoding="utf-8") as f:
                        f.write("Thao tác bị hủy bởi người dùng\n")
                    break

                dest_name = os.path.basename(raw_path)
                if dest_name in skip_names:
                    with open(log_file_path, "a", encoding="utf-8") as f:
                        f.write(f"{raw_path} - Skipped (giữ nguyên file cũ)\n")
                    succeeded_raw.add(raw_path)
                    continue

                try:
                    shutil.copyfile(raw_path, os.path.join(folder_dir, dest_name))
                    with open(log_file_path, "a", encoding="utf-8") as f:
                        f.write(f"{raw_path} - Success \n")
                    succeeded_raw.add(raw_path)
                except Exception as e:
                    with open(log_file_path, "a", encoding="utf-8") as f:
                        f.write(f"{raw_path} - Fail {str(e)} \n")
            progress.setValue(len(planned))

        count = 0
        for jpg_path in list_JPG:
            base_name = os.path.splitext(os.path.basename(jpg_path))[0]
            matches = raw_by_basename.get(base_name, [])
            if any(m in succeeded_raw for m in matches):
                count += 1

        summary = f"Hoàn thành {count} / {len(list_JPG)} trong tổng số {len(list_RAW)} files\nThư mục: {folder_dir}"
        LogDialog(self, "Kết quả", summary, log_file_path, folder_dir).exec()

app=QApplication(sys.argv)
mainwindow=MainWindow()
app.aboutToQuit.connect(mainwindow.saveSettings)
widget=QtWidgets.QStackedWidget()
widget.addWidget(mainwindow)
widget.setMinimumSize(650, 550)
widget.resize(650, 550)
widget.show()
sys.exit(app.exec())
