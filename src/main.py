import random
from pygame import mixer
import fnmatch
import os
from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer
import sys

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__() #gọi các lớp kế thừa phương thức __init__
        uic.loadUi('playAudio.ui', self) #tải tệp ui

        #tìm các widget trong file UI
        self.selectFolderButton = self.findChild(QPushButton,'btn_chonThuMuc')
        self.lw_dsBH = self.findChild(QListWidget, 'lw_dsBH')
        self.btn_play = self.findChild(QPushButton, 'btn_play')
        self.btn_pause = self.findChild(QPushButton, 'btn_pause')
        self.btn_prev = self.findChild(QPushButton, 'btn_prev')
        self.btn_next = self.findChild(QPushButton, 'btn_next')
        self.btn_repeat = self.findChild(QPushButton, 'btn_repeat')
        self.btn_Random = self.findChild(QPushButton, 'btn_Random')
        self.slder_adjust = self.findChild(QSlider, 'slider_adjustVolume')
        self.message_label = self.findChild(QLabel, 'lb_tbao')
        self.slider_time = self.findChild(QSlider, 'slider_time')
        self.lb_time = self.findChild(QLabel, 'lb_time')

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



        # Đặt giá trị tối thiểu và tối đa cho slider
        self.slider_time.setMinimum(0)
        self.slider_time.setMaximum(100)

        # Kết nối sự kiện sliderMoved và sliderReleased với phương thức update_time và set_music_position
        self.slider_time.sliderMoved.connect(self.update_time)
        self.slider_time.sliderReleased.connect(self.set_music_position)

        mixer.init() #khởi tạo mixer của pygame
        self.current_index = -1 #chỉ số bài hát hiện tại
        self.repeat = False
        self.random_enabled = False

        # Tạo một timer để cập nhật thời gian
        self.timer = QTimer(self)
        self.timer.setInterval(1000)  # Cập nhật mỗi giây
        self.timer.timeout.connect(self.update_slider_time)
        self.timer.start()


        self.show() # Hiển thị GUI


    def select_folder(self):
        #Mở hộp thoại chọn thư mục
        folder_path = QFileDialog.getExistingDirectory(self, "Chọn Thư Mục Nhạc")

        if folder_path:
            self.load_music(folder_path)

    def load_music(self, folder_path):
        #Duyệt qua các file nhạc trong thư mục và thêm vào QListWidget
        patterns = ["*.mp3", "*.wav", "*.flac", "*.ogg", "*.m4a"]
        self.lw_dsBH.clear() #xoá danh sách cũ

        for root, dirs, files in os.walk(folder_path):
            for pattern in patterns:  #vòng lặp này duyệt qua từng pattern trong ds patterns
                for filename in fnmatch.filter(files, pattern): #mỗi pattern, fnmath.filter sẽ lọc các file trong 'files' tương ứng với pattern đó
                    full_path = os.path.join(root, filename)
                    #tạo một QListWidgetItem mới với tên tệp
                    item = QtWidgets.QListWidgetItem(filename)
                    #lưu trữ đường dẫn đầy đủ vào dữ liệu của mục này
                    item.setData(QtCore.Qt.UserRole, full_path)
                    self.lw_dsBH.addItem(item) # thêm từng file nhạc phù hợp vào musicListWidget

    def play_music(self, index=None, resume=False, start_position=0):
        try:
            if index is not None:
                self.current_index = index
                self.lw_dsBH.setCurrentRow(self.current_index)

            current_item = self.lw_dsBH.currentItem()
            if current_item:
                #Lấy đường dẫn đầy đủ từ dữ liệu của mục
                file_path = current_item.data(QtCore.Qt.UserRole)
                if not resume:
                    mixer.music.load(file_path)
                    mixer.music.play(start=start_position)
                else:
                    #tiếp tục nhạc từ vị trí bị tạm dừng
                    mixer.music.unpause()
        except Exception as e:
            print(f"Error playing music: {e}")

    def play_music_item(self, item):
        index = self.lw_dsBH.row(item)
        self.play_music(index)

    def pause_music(self):
        if mixer.music.get_busy():
            mixer.music.pause()

    def prev_music(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.play_music(self.current_index)

    def next_music(self):
        if self.current_index < self.lw_dsBH.count() - 1:
            self.current_index += 1
            self.play_music(self.current_index)
        elif self.repeat:
            self.play_music(0) #chơi lại từ đầu nếu ở chế độ repeat

    def repeat_music(self):
        self.repeat = not self.repeat
        if self.repeat:
            self.btn_repeat.setIcon(QIcon("icon/repeat-active.png"))
        else:
            self.btn_repeat.setIcon(QIcon("icon/repeat.png"))

    def random_music(self):
        if self.lw_dsBH.count() > 0:
            if not self.random_enabled: #nếu chức năng random chưa được bật
                random_index = random.randint(0, self.lw_dsBH.count() - 1)
                self.play_music(random_index)
                self.btn_Random.setIcon(QIcon("icon/random.png"))
                self.random_enabled = True # Bật chức năng random
                self.message_label.setText("")
            else: #nếu chức năng random đã được bật
                self.btn_Random.setIcon(QIcon("icon/random-off.png"))
                self.random_enabled = False # tắt chức năng random
        else:
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
                mixer.music.set_volume(0) # đặt âm lượng của mixer thành 0
            else:
                # đặt âm lượng cho nhạc
                mixer.music.set_volume(volume)
        except Exception as e:
            print(f"Error adjusting volume: {e}")

    def update_slider_time(self):
        if mixer.music.get_busy():
            current_pos = mixer.music.get_pos() // 1000  # Lấy thời gian hiện tại của bài hát (ms to s)
            self.slider_time.setValue(current_pos)

            # Giả định rằng thời lượng bài nhạc là 180 giây
            total_duration = 180

            # Tính toán thời gian hiển thị dưới dạng mm:ss
            minutes = current_pos // 60
            seconds = current_pos % 60

            total_minutes = total_duration // 60
            total_seconds = total_duration % 60

            # Cập nhật label với thời gian hiển thị
            self.lb_time.setText(f"{minutes}:{seconds:02d} / {total_minutes}:{total_seconds:02d}")
        else:
            self.lb_time.setText("0:00 / 3:00")  # Reset thời gian khi không có bài hát đang phát

        # Kiểm tra nếu bài hát kết thúc
        if current_pos >= total_duration:
            if self.random_enabled:
                self.random_music()
            else:
                self.next_music()

    def update_time(self, value):
        # Lấy giá trị hiện tại của slider
        current_value = self.slider_time.value()

        # Giả định rằng thời lượng bài nhạc là 180 giây
        total_duration = 180

        # Tính toán thời gian hiển thị dưới dạng mm:ss
        minutes = current_value // 60
        seconds = current_value % 60

        total_minutes = total_duration // 60
        total_seconds = total_duration % 60

        # Cập nhật label với thời gian hiển thị
        self.lb_time.setText(f"{minutes}:{seconds:02d} / {total_minutes}:{total_seconds:02d}")

    def set_music_position(self):
        # Lấy giá trị hiện tại của slider
        current_value = self.slider_time.value()

        # Giả định rằng thời lượng bài nhạc là 180 giây
        total_duration = 180

        # Tính vị trí phát lại theo tỷ lệ của tổng thời lượng
        position_ratio = current_value / 100.0
        new_position = position_ratio * total_duration

        # Đặt vị trí phát lại mới (pygame không hỗ trợ trực tiếp việc tua nhạc,
        # nên chúng ta cần phát lại từ vị trí mới)
        mixer.music.load(self.lw_dsBH.currentItem().data(QtCore.Qt.UserRole))
        mixer.music.play(start=new_position)

app = QApplication(sys.argv) #tạo một phiên bản QtWidgets.QApplication
window = MainWindow()
app.exec()


