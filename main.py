import pynput
import time
import asyncio
import time, sys
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import plotly.graph_objs as go
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis


# visualize ur APM(Actions Per Minute) which suitable for keyboard guys

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(600, 400)
        self.pushButton1 = QtWidgets.QPushButton(Form)
        self.pushButton1.setGeometry(QtCore.QRect(270, 330, 75, 50))
        self.pushButton1.setObjectName("pushButton1")

        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(170, 70, 131, 81))
        self.label.setStyleSheet("font: 36pt \"微软雅黑\";")
        self.label.setObjectName("label")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "APM统计器"))
        self.pushButton1.setText(_translate("Form", "开始统计APM"))


class Master(QMainWindow, Ui_Form):
    def __init__(self):
        super(Master, self).__init__()

        self.setupUi(self)
        self.label = QtWidgets.QLabel()
        self.main = signal_thread()
        self.main.signal_apm[int, list].connect(self.paint_func)
        self.pushButton1.clicked.connect(self.start_thread)

    def paint_func(self, apm, record):
        chart = QChart()
        chart.setTitle("APM曲线,现在APM是{0}".format(apm))

        series = QLineSeries()
        for i in range(len(record)):
            series.append(i, record[i])
            series.setName("apm history")

        chart.addSeries(series)
        axisX = QValueAxis()
        axisX.setRange(0, len(record))
        axisX.setTitleText('Times(sec)')
        axisY = QValueAxis()
        axisY.setRange(0, max(record))
        axisY.setTitleText('APM')

        chart.setAxisX(axisX, series)
        chart.setAxisY(axisY, series)

        chartView = QChartView()
        chartView.setChart(chart)
        self.setCentralWidget(chartView)

    def start_thread(self):
        self.main.start()


class signal_thread(QThread):
    signal_apm = pyqtSignal([int, list])

    def __init__(self):
        super(QThread, self).__init__()
        super(signal_thread, self).__init__()
        self.queues = [0]
        self.count = 0
        self.apm = 0
        self.record = []

    def son_function(self):
        def on_click(x, y, button, pressed):
            if pressed:
                self.count += 1

        def on_press(key):
            if key:
                self.count += 1

        def cal_apm(count):
            if len(self.queues) < 60:
                pass
            else:
                self.apm -= self.queues[0]
                self.queues.pop(0)

            self.queues.append(count)
            self.apm += self.count

        mouse_listener = pynput.mouse.Listener(on_click=on_click)
        keyboard_listener = pynput.keyboard.Listener(on_press=on_press)
        mouse_listener.start()
        keyboard_listener.start()
        while True:
            time.sleep(1)
            cal_apm(self.count)
            self.count = 0
            if len(self.record) < 1800:
                pass
            else:
                self.record.pop(0)
            self.record.append(self.apm)
            self.signal_apm[int, list].emit(self.apm, self.record)
            print(self.count)
            print('-----')
            print(self.apm)

    def run(self):
        self.son_function()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myshow = Master()
    myshow.show()
    sys.exit(app.exec_())
