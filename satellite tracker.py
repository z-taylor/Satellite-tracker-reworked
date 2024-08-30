import sys
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import QApplication, QMainWindow, QDialog, QWidget, QDialogButtonBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QTimer, QThread, QEventLoop, Signal
from PySide6.QtGui import QStandardItem, QStandardItemModel
import os
import json
import re

def writeDefPrefsFile():
     defaultConfig = {
          "location": [
               -48.88120089, -123.34616041
          ],
          "tle_sources": [
               "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle"
          ],
          "tle_update" : [
               24, "Hours"
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
     with open("prefs.json", "w") as f:
          json.dump(defaultConfig, f, indent=4)
def writeNewPrefsFile(preferences_window):
     try:
          with open("prefs.json", "r") as f:
               config = json.load(f)
          newRadConfig = config["radio_config"]
          newRotConfig = config["rotator_config"]
     except FileNotFoundError:
          writeDefPrefsFile()
          with open("prefs.json", "r") as f:
               config = json.load(f)
          newRadConfig = config["radio_config"]
          newRotConfig = config["rotator_config"]

     newLocation = [preferences_window.LatInputBox.text(), preferences_window.LonInputBox.text()]
     latitude, longitude = newLocation
     latitude_pattern = re.compile(r"^-?(90(\.0{1,6})?|[1-8]?\d(\.\d{1,6})?)$")
     longitude_pattern = re.compile(r"^-?(180(\.0{1,6})?|1[0-7]\d(\.\d{1,6})?|[1-9]?\d(\.\d{1,6})?)$")
     if not latitude_pattern.match(str(latitude)) and longitude_pattern.match(str(longitude)):
          loader = QUiLoader()
          error_ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui files", "ErrorLatLon.ui")
          error_window = loader.load(error_ui_path, None)
          error_window.OKbutton.clicked.connect(error_window.close)
          error_window.show()
          loop = QEventLoop()
          loop.exec()
          return

     newSources = []
     try:
          model = preferences_window.TLElist.model()
          for row in range(model.rowCount()):
               item = model.item(row)
               newSources.append(item)
     except(AttributeError):
          print("Warning: source table is empty")

     newUpdate = [preferences_window.TLEupdatePeriod.value(), preferences_window.TLEupdateUnit.currentText()]
     newIDs = []
     try:
          model = preferences_window.SatelliteList.model()
          for row in range(model.rowCount()):
               item = model.item(row)
               newIDs.append(int(item))
     except(AttributeError):
          print("Warning: ID table is empty")

     newConfig = {
          "location": newLocation,
          "tle_sources": newSources,
          "tle_update" : newUpdate,
          "satellite_ids": newIDs,
          "radio_config": newRadConfig,
          "rotator_config": newRotConfig
     }
     with open("prefs.json", "w") as f:
          json.dump(newConfig, f, indent=4)
def addSource(preferences_window):
     pattern = re.compile(
          r'^(https?:\/\/)'        # http:// or https://
          r'(\w+\.)?'              # optional subdomain
          r'[a-zA-Z0-9-]{2,63}'    # domain name
          r'\.[a-zA-Z]{2,6}'       # top-level domain
          r'(:\d{1,5})?'           # optional port
          r'(\/\S*)?'              # optional path
          r'(\?\S*)?$'             # optional query parameters
     )
     source = str(preferences_window.TLEsource.text())
     if re.match(pattern, source):
          item = QStandardItem(str(source))
          model = preferences_window.TLElist.model()
          if model is None:
               model = QStandardItemModel(preferences_window.TLElist)
               preferences_window.TLElist.setModel(model)
          model.appendRow(item)
     else:
          loader = QUiLoader()
          error_ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui files", "ErrorSource.ui")
          error_window = loader.load(error_ui_path, None)
          error_window.OKbutton.clicked.connect(error_window.close)
          error_window.show()
          loop = QEventLoop()
          loop.exec()
          return  

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

     def confirmYes(self, confirm_window):
          writeDefPrefsFile()
          confirm_window.close()
     def confirmNo(self, confirm_window):
          confirm_window.close()
     def restoreDefaults(self):
          loader = QUiLoader()
          confirm_ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui files", "ConfirmChoice.ui")
          confirm_window = loader.load(confirm_ui_path, None)
          confirm_window.YesButton.clicked.connect(lambda: self.confirmYes(confirm_window))
          confirm_window.NoButton.clicked.connect(lambda: self.confirmNo(confirm_window))
          confirm_window.show()
          loop = QEventLoop()
          loop.exec()
     def savePrefs(self, preferences_window):
          writeNewPrefsFile(preferences_window)
     def cancelPrefs(self, confirm_window):
          confirm_window.close()
     def open_preferences(self):
          try:
               with open("prefs.json", "r") as f:
                    config = json.load(f)
               location = config["location"]
               TLEsources = config["tle_sources"]
               TLEupdate = config["tle_update"]
               SatIDs = config["satellite_ids"]
          except FileNotFoundError:
               writeDefPrefsFile()
               with open("prefs.json", "r") as f:
                    config = json.load(f)
               location = config["location"]
               TLEsources = config["tle_sources"]
               TLEupdate = config["tle_update"]
               SatIDs = config["satellite_ids"]
          lattitude, longitude = location
          period, unit = TLEupdate

          loader = QUiLoader()
          preferences_ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui files", "Preferences.ui")
          preferences_window = loader.load(preferences_ui_path, None)
          
          preferences_window.LatInputBox.setText(str(lattitude))
          preferences_window.LonInputBox.setText(str(longitude))
          preferences_window.TLEupdatePeriod.setValue(period)
          preferences_window.TLEupdateUnit.setCurrentText(unit)
          if len(TLEsources)>0:
               model = QStandardItemModel(preferences_window.TLElist)
               preferences_window.TLElist.setModel(model)
               for i in range (len(TLEsources)):
                    item = QStandardItem(TLEsources[i])
                    model.appendRow(item)
          if len(SatIDs)>0:
               model = QStandardItemModel(preferences_window.SatelliteList)
               preferences_window.SatelliteList.setModel(model)
               for i in range (len(SatIDs)):
                    item = QStandardItem(str(SatIDs[i]))
                    model.appendRow(item)

          preferences_window.SaveButton_2.clicked.connect(lambda: self.savePrefs(preferences_window))
          preferences_window.CancelButton.clicked.connect(lambda: self.cancelPrefs(preferences_window))
          preferences_window.RestoreDefButton.clicked.connect(self.restoreDefaults)
          preferences_window.TLEadd.clicked.connect(lambda: addSource(preferences_window))

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