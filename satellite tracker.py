import sys
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import QApplication, QMainWindow, QDialog, QWidget, QDialogButtonBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QTimer, QThread, QEventLoop, Signal
import os
def writeDefPrefsFile():
      {
            "location": [
                  -48.88120089, -123.34616041
            ],
            "tle_sources": [
                  "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle"
            ],
            "satellite_ids": [
                  25338, 28654, 33591, 40069, 44387, 57166, 59051, 41866, 51850
            ],
            "radio_config": {
                  "IP": "127.0.0.1",
                  "Port": 4532,
                  "RadioType": "RX",
                  "PTTstatus": "None",
                  "VFO": "N/A",
                  "LOup": 0,
                  "LOdown": 0,
                  "Signaling": [],
            },
            "rotator_config": {
                  "IP": "127.0.0.1",
                  "Port": 4533,
                  "AZtype": 1,
                  "MinMaxAz": [0, 0],
                  "MinMaxEl": [0, 0],
                  "AzStop": 0,
            }
}

class main(QMainWindow):
      def __init__(self):
            super(main, self).__init__()
            loader = QUiLoader()
            ui_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui files", "SatelliteTracker.ui")
            self.ui = loader.load(ui_file_path, None)
            self.setCentralWidget(self.ui)
            self.ui.actionPreferences.triggered.connect(self.open_preferences)
            self.ui.actionRadio.triggered.connect(self.open_radio)
            self.ui.actionRotator.triggered.connect(self.open_rotator)
            #timer1 = QTimer(self)
            #timer1.timeout.connect(self.update_sat_info)
            #timer1.start(200)
      def confirmYes(self):
            writeDefPrefsFile()
      def confirmNo(self, preferences_window):
            preferences_window.close()
      def restoreDefaults(self):
            loader = QUiLoader()
            confirm_ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui files", "ConfirmChoice.ui")
            confirm_window = loader.load(confirm_ui_path, None)
            confirm_window.YesButton.clicked.connect(self.confirmYes)
            confirm_window.NoButton.clicked.connect(lambda: self.confirmNo(confirm_window))
            confirm_window.show()
            loop = QEventLoop()
            loop.exec()
      def savePrefs(self, preferences_window):
            try:
                  #write to json file
                  print("try")
            except:
                  #if no json file present, create a json file and write preferences to it
                  print("except")
      def cancelPrefs(self, confirm_window):
            confirm_window.close()
      def open_preferences(self):
            loader = QUiLoader()
            preferences_ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui files", "Preferences.ui")
            preferences_window = loader.load(preferences_ui_path, None)
            preferences_window.SaveButton_2.clicked.connect(lambda: self.savePrefs(preferences_window))
            preferences_window.CancelButton.clicked.connect(lambda: self.cancelPrefs(preferences_window))
            preferences_window.RestoreDefButton.clicked.connect(self.restoreDefaults)
            preferences_window.show()
            loop = QEventLoop()
            loop.exec()
      def radSave(self):
            print("save")
            #code to save
      def radConnect(self):
            print("connect")
            #code to connect
      def open_radio(self):
            loader = QUiLoader()
            radio_ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui files", "Radio.ui")
            radio_window = loader.load(radio_ui_path, None)
            radio_window.saveButton.clicked.connect(self.radSave)
            radio_window.connectButton.clicked.connect(self.radConnect)
            radio_window.show()
            loop = QEventLoop()
            loop.exec()
      def rotSave(self):
            print("save")
            #code to save
      def rotConnect(self):
            print("connect")
            #code to connect
      def open_rotator(self):
            loader = QUiLoader()
            rotator_ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui files", "Rotator.ui")
            rotator_window = loader.load(rotator_ui_path, None)
            rotator_window.saveButton.clicked.connect(self.rotSave)
            rotator_window.connectButton.clicked.connect(self.rotConnect)
            rotator_window.show()
            loop = QEventLoop()
            loop.exec()
     
if __name__ == "__main__":
      QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
      app=QApplication(sys.argv)
      window=main()
      window.show()
      sys.exit(app.exec())