import sys
from deepdiff import DeepDiff
import cv2
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from barcodeModule import *
from barcodeModule import ReadBarcode
from paymentModule import Payment
from yolo import *
from matplotlib import cm
import matplotlib.pyplot as plt
import numpy as np
import threading
import time
import winsound


# UI파일 연결
# 단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.

#form_class = uic.loadUiType("selfcounter.ui")[0]
count=0
global ObjectImageResult




# 화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow):
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])

    def __init__(self):
        super().__init__()
        # 데이터
        self.priceDict = dict()
        self.numDict = dict()
        self.priceDict['Sample'] = 4000  # 샘플
        self.numDict['Sample'] = 2  # 샘플
        self.totalPrice = 0
        self.over = False
        self.temp_totalPrice = -1000  # 총 결제금액 예비용
        # 함수 모듈
        self.barcodeReader = ReadBarcode()
        self.payment = Payment()
        self.product_name = []  # 물건 인식때 인식한 물건 이름들 넣는 배열
        self.yoloTest = YOLO_Object_Detector()
        self.middle_Dict = dict()  # 물건의 한글 이름과 영어 이름 이어주는 용도
        # 변수
        self.fps = 20
        self.cpt = cv2.VideoCapture(0)
        _, self.camImg = self.cpt.read()
        self.isPay = False
        self.run_video = True
        # 아래는 모두 GUI
        self.setupUi(self)
        self.sleepHour=3
        self.lock = threading.Lock()

        self.frame = self.imglabel  # 영상

        self.payment_btn.clicked.connect(self.totalPayment_creditCard);  # 카드 결제 이벤트 연결

    def setupUi(self, myWindow):
        myWindow.setObjectName("SelfCounter")
        myWindow.resize(797, 621)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(myWindow.sizePolicy().hasHeightForWidth())
        myWindow.setSizePolicy(sizePolicy)
        self.setStyleSheet("QMainWindow { background: 'white'}");
        font = QFont()
        font.setFamily("새굴림")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        myWindow.setFont(font)
        self.centralwidget = QWidget(myWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.imglabel = QLabel(self.centralwidget)
        self.imglabel.setGeometry(QRect(10, 390, 431, 221))
        self.imglabel.setFrameShape(QFrame.Box)
        self.imglabel.setText("")
        self.imglabel.setObjectName("imglabel")
        self.payment_btn = QPushButton(self.centralwidget)
        self.payment_btn.setGeometry(QRect(640, 430, 151, 71))
        font = QFont()
        font.setFamily("새굴림")
        font.setPointSize(15)
        font.setBold(False)
        font.setWeight(50)
        self.payment_btn.setFont(font)
        self.payment_btn.setAutoFillBackground(False)
        self.payment_btn.setObjectName("pushButton_2")

        self.alertlabel = QLabel(self.centralwidget)
        self.alertlabel.setGeometry(QRect(450, 390, 171, 221))
        font = QFont()
        font.setFamily("새굴림")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.alertlabel.setFont(font)
        self.alertlabel.setText("")
        self.alertlabel.setObjectName("alertlabel")
        self.alertlabel.setWordWrap(True)

        self.payLabel = QLabel(self.centralwidget)
        self.payLabel.setGeometry(QRect(10, 10, 800, 650))
        font = QFont()
        font.setFamily("새굴림")
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(50)
        self.payLabel.setFont(font)
        self.payLabel.setStyleSheet("background-color: #FFFFFF")
        self.payLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.payLabel.setText("결제가 완료되었습니다.\n영수증과 상품을 챙겨주세요.")
        self.payLabel.setObjectName("payLabel")
        self.payLabel.setWordWrap(True)
        self.payLabel.setHidden(True)

        self.productTable = QTableWidget(self.centralwidget)
        self.productTable.setGeometry(QRect(10, 10, 781, 341))
        font = QFont()
        font.setPointSize(11)
        self.productTable.setFont(font)
        self.productTable.setObjectName("productTable")

        self.productTable.setEditTriggers(QAbstractItemView.NoEditTriggers)  # edit 금지

        self.tableWidget = QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QRect(10, 350, 781, 31))
        self.tableWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tableWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tableWidget.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.tableWidget.setTabKeyNavigation(False)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setDragDropOverwriteMode(False)
        self.tableWidget.setSelectionMode(QAbstractItemView.NoSelection)
        self.tableWidget.setIconSize(QSize(0, 0))
        self.tableWidget.setTextElideMode(Qt.ElideMiddle)
        self.tableWidget.setShowGrid(True)
        self.tableWidget.setGridStyle(Qt.SolidLine)
        self.tableWidget.setCornerButtonEnabled(False)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(0)
        item = QTableWidgetItem()
        item.setTextAlignment(Qt.AlignCenter)
        font = QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QTableWidgetItem()
        item.setTextAlignment(Qt.AlignCenter)
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QTableWidgetItem()
        item.setTextAlignment(Qt.AlignCenter)
        self.tableWidget.setHorizontalHeaderItem(2, item)
        self.tableWidget.horizontalHeader().setCascadingSectionResizes(False)
        self.tableWidget.horizontalHeader().setDefaultSectionSize(260)
        self.tableWidget.horizontalHeader().setMinimumSectionSize(50)
        myWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(myWindow)
        QMetaObject.connectSlotsByName(myWindow)
        myWindow.show()

    def retranslateUi(self, myWindow):
        _translate = QCoreApplication.translate
        myWindow.setWindowTitle(_translate("SelfCounter", "SelfCounter"))
        self.payment_btn.setText(_translate("SelfCounter", "카드 결제"))

        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("SelfCounter", "합계"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("SelfCounter", "0"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("SelfCounter", "0"))
        self.productTable.setColumnCount(4)
        self.productTable.setHorizontalHeaderLabels(['상품명', '가격', '수량', '총 합'])
        self.productTable.setColumnWidth(0, 315)
        self.productTable.setColumnWidth(1, 154.3)
        self.productTable.setColumnWidth(2, 154.3)
        self.productTable.setColumnWidth(3, 154.3)
        self.productTable.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.productTable.verticalHeader().hide()
        self.productTable.setEditTriggers(QAbstractItemView.NoEditTriggers)  # edit 금지

    def totalPayment_creditCard(self):  # 카드 결제 이벤트
        #self.isPay = True
        self.sleepHour=10000
        #_, self.camImg = self.cpt.read()
        money = self.barcodeReader.moneyReturn(self.camImg)
        print(money)
        if int(money) < self.temp_totalPrice:
            self.alertlabel.setText("잔액이 부족합니다")
        else:
            print(self.temp_totalPrice)
            lastMoney = int(money) - self.temp_totalPrice
            self.alertlabel.setText("잔금: " + repr(lastMoney) + " 원")
            self.payLabel.setHidden(False)
            self.productTable.setHidden(True)
            self.tableWidget.setHidden(True)

    def start(self):  # 일반 인식 모듈.
        self.alertlabel.setText("물체 인식 중 입니다.")


    def reading(self):  # 바코드 인식 함수. timer 마다 실행
        while not self.isPay:
            print("reading 실행")
            _, self.camImg = self.cpt.read()
            image_sharp = cv2.filter2D(self.camImg, -1, self.kernel)
            barcodeImg, barcodeNum = self.barcodeReader.readBarcode(image_sharp)
            # 디비로부터 정보를 읽어옴
            try:
                dic = self.payment.findProduct(barcodeNum)
            except:
                dic.clear()
            if len(dic) != 0:
                for key in dic.keys():
                    if key in self.priceDict:  # 이미 있는 상품이면 수량 1 증가
                        self.numDict[key] = self.numDict[key] + 1
                    else:  # 없으면 priceDict와 numDict에 추가
                        self.priceDict[key] = dic[key]
                        self.numDict[key] = 1
                print(DeepDiff(dic, self.priceDict, ignore_order=True))
                self.createLine()
            #print("바코드 숫자=> ",barcodeNum)
            time.sleep(self.sleepHour)
        #time.sleep(self.sleepHour)

    def readingClassDict(self,_classDict):   # object detection 에서 받은 classDict로 priceDict,numDict 에 추가하가
        for key in _classDict.keys():
            if _classDict[key]!=0 :
                self.middle_Dict[key]=_classDict[key]
                self.product_name.append(key)
        dic, dicForName=self.payment.findProductByName(self.product_name) # key 가 name, val 이 price
        if len(dic) != 0:
            for key in dicForName.keys():   # dicForName (key=eng_name, val=kor_name)
                kor_name= dicForName[key]
                if kor_name in self.priceDict:  # 이미 있는 상품이면 수량 1 증가
                    self.numDict[kor_name] = self.numDict[kor_name]+_classDict[key]
                    self.priceDict[kor_name]=dic[kor_name]
                else:  # 없으면 priceDict와 numDict에 추가
                    self.priceDict[kor_name] = dic[kor_name]
                    self.numDict[kor_name] = _classDict[key]
            print(DeepDiff(dic, self.priceDict, ignore_order=True))
            self.createLine()

    def createLine(self):
        self.productTable.clearContents()  # 기존 항목 모두 삭제
        self.productTable.setRowCount(0)
        self.totalnum = 0
        print(self.priceDict.keys().__str__())
        for key in self.priceDict.keys():
            row = self.productTable.rowCount()
            print("row %d", row)
            self.productTable.insertRow(row)
            self.productTable.setItem(row, 0, QTableWidgetItem(key))  # 이름
            self.productTable.setItem(row, 1, QTableWidgetItem(self.priceDict[key].__str__()))  # 가격
            self.productTable.setItem(row, 2, QTableWidgetItem(self.numDict[key].__str__()))  # 수량
            self.totalnum += self.numDict[key]
            self.productTable.setItem(row, 3,
                                      QTableWidgetItem((self.priceDict[key] * self.numDict[key]).__str__()))  # 총합
            self.totalPrice += (self.priceDict[key] * self.numDict[key])
        if len(list(self.priceDict.keys())) == 0:
            self.alertlabel.setText("아무것도 인식된게 없습니다.")
        else:
            self.tableWidget.setHorizontalHeaderItem(1, QTableWidgetItem(self.totalnum.__str__()))
            self.tableWidget.setHorizontalHeaderItem(2, QTableWidgetItem(self.totalPrice.__str__()))
        self.temp_totalPrice = self.totalPrice
        self.totalPrice = 0
        self.beepsound()


    def showImg(self):  # 일반 인식 함수. timer 마다 실행
        while self.run_video:
            _, cam = self.cpt.read()
            self.camImg = cam
            cam = cv2.cvtColor(cam, cv2.COLOR_BGR2RGB)  #PIL.Image.Image
            self.lock.acquire()
            img = QImage(cam, cam.shape[1], cam.shape[0], QImage.Format_RGB888)
            pix = QPixmap.fromImage(img)
            self.frame.setPixmap(pix)
            self.lock.release()

    def closeEvent(self, QCloseEvent):  # 종료 이벤트 선언
        self.stop()
        self.deleteLater()
        self.payment.finishPayment()
        QCloseEvent.accept()

    def stop(self):  # 종료 이벤트
        self.frame.setPixmap(QPixmap.fromImage(QImage()))
        #self.timer.stop()
        self.cpt.release()

    def findingObject(self):
        while not self.isPay:
            _, image_=self.cpt.read()
            image_ = cv2.cvtColor(image_, cv2.COLOR_BGR2RGB)    #(480,640,3)
            im = Image.fromarray((255-image_ * 255).astype(np.uint8))   #색깔이 반전되서 들어가서 255에서 뺐다
            result_image, class_dict = self.yoloTest.detect_image(im)
            print("class_dict",class_dict)                      # 물품 배열 (판별된것에 1을 표시하는듯)
            result = np.asarray(result_image)
            self.lock.acquire()
            final_img = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
            img = QImage(final_img, final_img.shape[1], final_img.shape[0], QImage.Format_RGB888)
            pix = QPixmap.fromImage(img)
            self.frame.setPixmap(pix)
            self.lock.release()
            self.readingClassDict(class_dict)
            #threading.Timer(2, self.findingObject).start()
            time.sleep(self.sleepHour)




    def beepsound(self):
        freq = 1500  # range : 37 ~ 32767
        dur = 250  # ms
        winsound.Beep(freq, dur)  # winsound.Beep(frequency, duration)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    myWindow.start()

    t = threading.Thread(target=myWindow.showImg)
    t.daemon=True
    t.start()


    th = threading.Thread(target=myWindow.findingObject)
    th.start()

    th2= threading.Thread(target=myWindow.reading)
    th2.start()

    app.exec_()  # 여기서부터 무한 루프인 이벤트 루프가 실행된다
    sys.exit(app.exec_())


