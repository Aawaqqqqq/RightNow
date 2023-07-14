import sys
import cv2
import mediapipe as mp
from Ui_basketball import Ui_Basketball
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtMultimedia import *

class HandIdentifyThread(QThread):
    pose = pyqtSignal(object)

    def __init__(self):
        super().__init__()

    def run(self):
        gesture_dict = {
            1: "1",
            2: "2",
            3: "",
        }

        # 配置meidapipe
        hand_drawing_utils = mp.solutions.drawing_utils  # 绘图工具
        mp_hands = mp.solutions.hands  # 手部识别api
        my_hands = mp_hands.Hands()  # 获取手部识别类
        # 调用摄像头 0为默认摄像头
        cap = cv2.VideoCapture(0)

        # 防抖
        lastingTime = 0
        lastNum = -1
        breakflag=0

        # 通过循环将每一帧的图片读出来
        while True:
            
            # read方法返回两个参数
            # success 判断摄像头是否打开成功，img 为读取的每一帧的图像对象
            success, img = cap.read()
        
            if not success:
                print('摄像头打开失败')
                break
        
            # 将BGR转换为RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            # 识别图像中的手势，并返回结果
            results = my_hands.process(img)
            # 再将RGB转回BGR
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            hand_jugg = ""

            if results.multi_hand_landmarks:
                for hand_label in results.multi_handedness:
                    hand_jugg=str(hand_label).split('"')[1]
                    cv2.putText(img,hand_jugg,(50,200),0,1.3,(0,0,255),2)

            # results.multi_hand_landmarks为None时进行for循环会报错，所以要先判断
            if results.multi_hand_landmarks:
                for hand_landmark in results.multi_hand_landmarks:
                    hand_drawing_utils.draw_landmarks(img,
                                                    hand_landmark,
                                                    mp_hands.HAND_CONNECTIONS,
                                                    mp.solutions.drawing_styles.get_default_hand_landmarks_style(),
                                                    mp.solutions.drawing_styles.get_default_hand_connections_style())
            
            if results.multi_hand_landmarks:
                for handLms in results.multi_hand_landmarks:
                    finger_count = 0
                    for id in [4, 8, 12, 16, 20]:
                        if handLms.landmark[id].y < handLms.landmark[id - 2].y:
                            finger_count += 1
                            # cv2.circle(img, (cx, cy), int(w / 50), (0, 255, 0), cv2.FILLED)

                    if finger_count == 2:
                        gesture_type = 1
                        if lastNum == 1:
                            lastingTime = lastingTime + 1
                        else:
                            lastNum = 1
                            lastingTime = 0
                    elif finger_count == 3:
                        gesture_type = 2
                        if lastNum == 2:
                            lastingTime = lastingTime + 1
                        else:
                            lastNum = 2
                            lastingTime = 0
                    else:
                        gesture_type = 3
                        lastNum = -1
                        lastingTime = 0

                    cv2.putText(img, gesture_dict[gesture_type][::-1], (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                    print(lastingTime)
                    # 0为开启上下镜像 1为开启左右镜像 -1为左右并上下镜像
                    img = cv2.flip(img, 1)
                    # imshow方法展示窗口，第一个参数为窗口的名字，第二个参数为帧数
                    cv2.imshow("frame", img)
                    # 延迟一毫秒
                    cv2.waitKey(1)

                    if lastingTime >= 20:
                        print(finger_count - 1)
                        breakflag=1
                        break
                if(breakflag):
                    break
        self.pose.emit(finger_count - 1)

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 创建 UI 对象并设置界面
        self.ui = Ui_Basketball()
        self.ui.setupUi(self)
        self.page=0
        
        #按键判断模式
        self.ui.AnalyseMode.clicked.connect(self.analyse_mode1)
        self.ui.Back1.clicked.connect(self.play_video)
        self.ui.Back2.clicked.connect(self.back)

        #视频播放跳转
        self.ui.player.mediaStatusChanged.connect(self.status_changed)

        #手势判断模式
        # self.thread1 = HandIdentifyThread()
        # self.thread1.pose.connect(self.analyse_mode2)
        # self.thread1.start()

    def analyse_mode1(self):
        self.ui.stackedWidget.setCurrentIndex(1)
        self.page=1
     
    def analyse_mode2(self,pose):
        if(self.page==0):
            if(pose==1):
                self.ui.stackedWidget.setCurrentIndex(1)
                self.page=1
            if(pose==2):
                self.ui.stackedWidget.setCurrentIndex(3)
                self.page=3

    def back(self):
        self.ui.stackedWidget.setCurrentIndex(0)
        self.page=0

    def play_video(self):
        self.ui.player.setSource(QFileDialog.getOpenFileUrl()[0])
        self.ui.player.play()

    def status_changed(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.ui.stackedWidget.setCurrentIndex(2)
            self.page=2

if __name__ == '__main__':
    # 运行界面
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())