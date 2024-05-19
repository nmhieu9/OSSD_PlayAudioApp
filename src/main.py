import random

import yt_dlp
from pygame import mixer
import fnmatch
import os
from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer, pyqtSignal, QObject, QUrl
import sys
import youtube_dl
import requests
from bs4 import BeautifulSoup


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()  #gọi các lớp kế thừa phương thức __init__
        uic.loadUi('playAudio.ui', self)  #tải tệp ui

        #tìm các widget trong file UI
        self.selectFolderButton = self.findChild(QPushButton, 'btn_chonThuMuc')
        self.lw_dsBH = self.findChild(QListWidget, 'lw_dsBH')
        self.btn_play = self.findChild(QPushButton, 'btn_play')
        self.btn_pause = self.findChild(QPushButton, 'btn_pause')
        self.btn_prev = self.findChild(QPushButton, 'btn_prev')
        self.btn_next = self.findChild(QPushButton, 'btn_next')
        self.btn_repeat = self.findChild(QPushButton, 'btn_repeat')
        self.btn_Random = self.findChild(QPushButton, 'btn_Random')
        self.slder_adjust = self.findChild(QSlider, 'slider_adjustVolume')
        self.message_label = self.findChild(QLabel, 'lb_tbao')

        self.lb_dsNhac = self.findChild(QLabel, 'lb_dsNhac')
        self.btn_tainhac = self.findChild(QPushButton, 'btn_tainhac')
        self.txt_url = self.findChild(QTextEdit,'txt_url')

        #Kết nối sự kiện click của button với phương thức
        self.selectFolderButton.clicked.connect(self.select_folder)
        self.btn_play.clicked.connect(self.play_music)
        self.btn_pause.clicked.connect(self.pause_music)
        self.btn_prev.clicked.connect(self.prev_music)
        self.btn_next.clicked.connect(self.next_music)
        self.btn_repeat.clicked.connect(self.repeat_music)
        self.btn_Random.clicked.connect(self.random_music)
        self.lw_dsBH.itemDoubleClicked.connect(self.play_music_item)
        self.slder_adjust.valueChanged.connect(self.adjust_volume)
        self.btn_tainhac.clicked.connect(self.download_music)


        mixer.init()  #khởi tạo mixer của pygame
        self.current_index = -1  #chỉ số bài hát hiện tại
        self.repeat = False
        self.random_enabled = False

        self.show()  # Hiển thị giao diện


    def select_folder(self):
        ## Mở hộp thoại chọn thư mục và lưu đường dẫn của thư mục được chọn vào biến folder_path
        folder_path = QFileDialog.getExistingDirectory(self, "Chọn Thư Mục Nhạc")

        # Kiểm tra nếu người dùng đã chọn một thư mục (folder_path không rỗng)
        if folder_path:
            # Gọi phương thức load_music với đối số là đường dẫn thư mục được chọn
            self.load_music(folder_path)

    def load_music(self, folder_path):
        #Duyệt qua các file nhạc trong thư mục và thêm vào QListWidget
        patterns = ["*.mp3", "*.wav", "*.flac", "*.ogg", "*.m4a"]  # Các định dạng file nhạc cần tìm
        self.lw_dsBH.clear()  #xoá danh sách cũ trong QListWidget

        # Duyệt qua các thư mục con và file trong folder_path
        for root, dirs, files in os.walk(folder_path):
            for pattern in patterns:  #vòng lặp này duyệt qua từng pattern trong ds patterns
                # Lọc các file trong 'files' tương ứng với pattern hiện tại
                for filename in fnmatch.filter(files, pattern):
                    full_path = os.path.join(root, filename)  # Tạo đường dẫn đầy đủ của file
                    #tạo một QListWidgetItem mới với tên tệp
                    item = QtWidgets.QListWidgetItem(filename)
                    #lưu trữ đường dẫn đầy đủ vào dữ liệu của mục này
                    item.setData(QtCore.Qt.UserRole, full_path)
                    self.lw_dsBH.addItem(item)  # thêm từng file nhạc phù hợp vào musicListWidget

    def play_music(self, index=None, resume=False, start_position=0):
        try:
            if index is not None:
                # Nếu chỉ số (index) được cung cấp, cập nhật current_index và đặt hàng hiện tại trong QListWidget
                self.current_index = index
                self.lw_dsBH.setCurrentRow(self.current_index)

            # Lấy mục hiện tại trong QListWidget
            current_item = self.lw_dsBH.currentItem()
            if current_item:
                #Lấy đường dẫn đầy đủ từ dữ liệu của mục
                file_path = current_item.data(QtCore.Qt.UserRole)
                if not resume:
                    # Nếu không phải tiếp tục từ điểm tạm dừng, tải và phát nhạc từ đầu hoặc từ vị trí được chỉ định
                    mixer.music.load(file_path)
                    mixer.music.play(start=start_position)
                else:
                    #tiếp tục nhạc từ vị trí bị tạm dừng
                    mixer.music.unpause()
        except Exception as e:
            # Bắt lỗi và in ra thông báo lỗi nếu có
            print(f"Error playing music: {e}")

    def play_music_item(self, item):
        # Lấy chỉ số của mục được chọn trong QListWidget
        index = self.lw_dsBH.row(item)
        # Gọi phương thức play_music với chỉ số đã lấy được
        self.play_music(index)

    def pause_music(self):
        # Kiểm tra nếu có nhạc đang được phát
        if mixer.music.get_busy():
            # Tạm dừng phát nhạc
            mixer.music.pause()

    def prev_music(self):
        # Kiểm tra nếu chỉ số bài hát hiện tại lớn hơn 0 (tức là không phải bài hát đầu tiên)
        if self.current_index > 0:
            # Giảm chỉ số bài hát hiện tại đi 1 để chuyển sang bài hát trước đó
            self.current_index -= 1
            # Gọi phương thức play_music để phát bài hát mới với chỉ số đã cập nhật
            self.play_music(self.current_index)

    def next_music(self):
        # Kiểm tra nếu chỉ số bài hát hiện tại nhỏ hơn số lượng bài hát trong danh sách trừ 1
        if self.current_index < self.lw_dsBH.count() - 1:
            # Tăng chỉ số bài hát hiện tại lên 1 để chuyển sang bài hát kế tiếp
            self.current_index += 1
            # Gọi phương thức play_music để phát bài hát mới với chỉ số đã cập nhật
            self.play_music(self.current_index)
        # Nếu đang ở bài hát cuối cùng và chế độ repeat đang bật
        elif self.repeat:
            self.play_music(0)  #chơi lại từ bài hát đầu tiên

    def repeat_music(self):
        # Chuyển đổi trạng thái của biến repeat (nếu đang True thì thành False và ngược lại)
        self.repeat = not self.repeat
        # Kiểm tra nếu chế độ lặp lại đang bật
        if self.repeat:
            # Đặt biểu tượng cho nút repeat thành biểu tượng của chế độ lặp lại đang hoạt động
            self.btn_repeat.setIcon(QIcon("icon/repeat-active.png"))
        else:
            # Đặt biểu tượng cho nút repeat thành biểu tượng của chế độ lặp lại không hoạt động
            self.btn_repeat.setIcon(QIcon("icon/repeat.png"))

    def random_music(self):
        if self.lw_dsBH.count() > 0:
            if not self.random_enabled:  #nếu chức năng random chưa được bật
                # Chọn một chỉ số ngẫu nhiên từ 0 đến số lượng bài hát - 1
                random_index = random.randint(0, self.lw_dsBH.count() - 1)
                # Phát nhạc từ bài hát được chọn ngẫu nhiên
                self.play_music(random_index)
                # Đặt biểu tượng cho nút Random thành biểu tượng random hoạt động
                self.btn_Random.setIcon(QIcon("icon/random.png"))
                self.random_enabled = True  # Bật chức năng random
                self.message_label.setText("")  # Xóa thông báo lỗi (nếu có)
            else:  #nếu chức năng random đã được bật
                # Đặt biểu tượng cho nút Random thành biểu tượng random không hoạt động
                self.btn_Random.setIcon(QIcon("icon/random-off.png"))
                self.random_enabled = False  # tắt chức năng random
        else:
            # Hiển thị thông báo rằng danh sách nhạc trống
            self.message_label.setText("Danh sách nhạc trống !!!")

    def adjust_volume(self, value):
        try:
            # đảm bảo rằng mixer đã được khởi tạo trước
            if not mixer.get_init():
                mixer.init()

            # chuyển đổi giá trị phần trăm âm lượng thành khoảng từ 0.0 đến 1.0
            volume = value / 100.0

            #ktra nếu gtri âm lượng = 0 thì tắt âm thanh
            if self.slder_adjust.value() == 0:
                mixer.music.set_volume(0)  # đặt âm lượng của mixer thành 0
            else:
                # # Đặt âm lượng cho nhạc bằng giá trị volume đã tính toán
                mixer.music.set_volume(volume)
        except Exception as e:
            # Bắt lỗi và in ra thông báo lỗi nếu có
            print(f"Error adjusting volume: {e}")

    download_path = "../data/music"
    def download_music(self, download_path):
        url = self.textEdit_url.toPlainText()  # Lấy URL từ QTextEdit

        ydl_opts = {
            'format':'bestaudio/best',
            'postprocessors':[{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '128',
            }],
            'outtmpl':os.path.join(download_path, '%(title)s.mp3'),
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


app = QApplication(sys.argv)  #tạo một phiên bản QtWidgets.QApplication
window = MainWindow()  # Tạo một cửa sổ MainWindow
app.exec()  # Bắt đầu vòng lặp sự kiện của ứng dụng
