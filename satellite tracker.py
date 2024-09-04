import sys
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import QApplication, QMainWindow, QDialog, QWidget, QDialogButtonBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QTimer, QThread, QEventLoop, Signal
from PySide6.QtGui import QStandardItem, QStandardItemModel
import os
import json
import re
import geocoder
import requests
from datetime import datetime
from skyfield.api import load, wgs84
import time

def error(path):
     if not QApplication.instance():
         app = QApplication(sys.argv)
     loader = QUiLoader()
     error_ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui files", "errors", path)
     error_window = loader.load(error_ui_path, None)
     error_window.OKbutton.clicked.connect(error_window.close)
     error_window.show()
     loop = QEventLoop()
     loop.exec()

def writeDefPrefsFile():
     defaultConfig = {
          "location": [
               "-48.88120089", "-123.34616041"
          ],
          "tle_sources": [
               "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle"
          ],
          "tle_update" : [
               24, "Hours"
          ],
          "satellite_ids": [
               "25338", "28654", "33591", "40069", "44387", "57166", "59051", "41866", "51850"
          ],
          "update_rate" : "1000",
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
               "MinMaxAz": [
                    0,
                    0
               ],
               "MinMaxEl": [
                    0, 
                    0
               ],
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
          error("ErrorLatLon.ui")
          return

     newSources = []
     pattern = re.compile(
          r'^(https?:\/\/)'        # http:// or https://
          r'(\w+\.)?'              # optional subdomain
          r'[a-zA-Z0-9-]{2,63}'    # domain name
          r'\.[a-zA-Z]{2,6}'       # top-level domain
          r'(:\d{1,5})?'           # optional port
          r'(\/\S*)?'              # optional path
          r'(\?\S*)?$'             # optional query parameters
     )
     try:
          model = preferences_window.TLElist.model()
          for row in range(model.rowCount()):
               item = model.item(row)
               if re.match(pattern, item.text()):
                    newSources.append(item.text())
               else:
                    error("ErrorSource_1orMore.ui")
                    return
     except(AttributeError):
          print("Warning: source table is empty")

     newUpdate = [preferences_window.TLEupdatePeriod.value(), preferences_window.TLEupdateUnit.currentText()]
     
     newIDs = []
     pattern = re.compile(r'^\d{5}$')
     try:
          model = preferences_window.SatelliteList.model()
          for row in range(model.rowCount()):
               item = model.item(row)
               if re.match(pattern, item.text()):
                    newIDs.append(item.text())
               else:
                    error("ErrorID_1orMore.ui")
                    return
     except(AttributeError):
          print("Warning: ID table is empty")
     if re.fullmatch(r'\d+', str(preferences_window.UpdateRate.text())):
          if float(preferences_window.UpdateRate.text()) > 0:
               newUpdateRate = preferences_window.UpdateRate.text()
          else: 
               error("ErrorUpdateTooLow.ui")
               return
     else:
          error("ErrorUpdateNumbersOnly.ui")
          return
     

     newConfig = {
          "location": newLocation,
          "tle_sources": newSources,
          "tle_update" : newUpdate,
          "satellite_ids": newIDs,
          "update_rate" : newUpdateRate,
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
          error("ErrorSource.ui")
          return  
def deleteSource(preferences_window):
     selection_model = preferences_window.TLElist.selectionModel()
     selected_indexes = selection_model.selectedIndexes()
     if selected_indexes:
          selected_index = selected_indexes[0]
          model = preferences_window.TLElist.model()
          model.removeRow(selected_index.row())

def addSat(preferences_window):
     pattern = re.compile(r'^\d{5}$')
     source = str(preferences_window.SatelliteIDbox.text())
     if re.match(pattern, source):
          item = QStandardItem(str(source))
          model = preferences_window.SatelliteList.model()
          if model is None:
               model = QStandardItemModel(preferences_window.SatelliteList)
               preferences_window.SatelliteList.setModel(model)
          model.appendRow(item)
     else:
          loader = QUiLoader()
          error("ErrorID.ui")
          return
def deleteSat(preferences_window):
     selection_model = preferences_window.SatelliteList.selectionModel()
     selected_indexes = selection_model.selectedIndexes()
     if selected_indexes:
          selected_index = selected_indexes[0]
          model = preferences_window.SatelliteList.model()
          model.removeRow(selected_index.row())

class read:
     try:
          with open("prefs.json", "r") as f:
               config = json.load(f)
               location = config["location"]
               TLEsources = config["tle_sources"]
               TLEupdate = config["tle_update"]
               SatIDs = config["satellite_ids"]
               UpdateRate = config["update_rate"]
     except:
          writeDefPrefsFile()
          with open("prefs.json", "r") as f:
               config = json.load(f)
          location = config["location"]
          TLEsources = config["tle_sources"]
          TLEupdate = config["tle_update"]
          SatIDs = config["satellite_ids"]
          UpdateRate = config["update_rate"]
          error("ErrorRead.ui")

     latitude, longitude = location
     period, unit = TLEupdate

def fetchTLEs():
     print("Updating TLEs.....")
     urls = read.TLEsources
     unique_tles = set()
     target_norad_ids = read.SatIDs
     for url in urls:
          response = requests.get(url)
          status = response.status_code
          if status == 200:
               lines = response.text.splitlines()
               for i in range(0, len(lines), 3):
                    if i+2 <= len(lines):
                         tle_set = "\n".join(lines[i:i+3])
                         unique_tles.add(tle_set)
               with open('AllTLEs.txt', 'w', encoding='utf-8') as file:
                    for tle in unique_tles:
                         file.write(tle + "\n")
          else: 
               loader = QUiLoader()
               error_ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui files", "errors", "ErrorBrokenTle.ui")
               error_window = loader.load(error_ui_path, None)
               error_window.label.text(f"One or more broken TLE sources. The link may be typed incorrectly or the website may be down.\nError code: {status}\nBroken link: {url}")
               error_window.OKbutton.clicked.connect(error_window.close)
               error_window.show()
               loop = QEventLoop()
               loop.exec()
               return
     print("TLE update finished")
def updateUsedTLEs():
     print("Updating active satellites list.....")
     target_norad_ids = read.SatIDs
     with open('AllTLEs.txt', 'r', encoding='utf-8') as file:
          all_tles = file.readlines()
     matching_tles = []
     for i in range(0, len(all_tles), 3):
          if i + 2 < len(all_tles):
               tle_lines = all_tles[i:i + 3]
               line2 = tle_lines[1].strip()
               try:
                    norad_id_part = line2[2:8].strip()
                    if len(norad_id_part) == 6 and norad_id_part[-1] == 'U':
                         norad_id_str = norad_id_part[:-1]
                         if norad_id_str.isdigit():
                              norad_id = norad_id_str
                              if norad_id in target_norad_ids:
                                   matching_tles.append("".join(tle_lines))
               except (ValueError, IndexError) as e:
                    print(f"Error processing TLE starting with: {tle_lines[0].strip()}")
                    print(f"Exception: {e}")
     with open('UsedTLEs.txt', 'w', encoding='utf-8') as file:
          file.writelines(matching_tles)
     print("Finished updating active satellite list")

class geolocate:
     g = geocoder.ip('me')
     if g.ok:
          latitude = g.latlng[0] if g.latlng else None
          longitude = g.latlng[1] if g.latlng else None
          accuracy = g.accuracy

class Worker(QThread):
     def __init__(self, sat_id, x, sat_info, now, satellites, by_number, base, ts):
          super().__init__()
          self.sat_id = sat_id
          self.index = x
          self.sat_info = sat_info
          self.now = now
          self.y = self.now.strftime("%Y").lstrip("0")
          self.mo = self.now.strftime("%m").lstrip("0")
          self.d = self.now.strftime("%d").lstrip("0")
          self.h = self.now.strftime("%H").lstrip("0")
          self.date = int(self.d+self.mo+self.y+self.h)
          self.satellites = satellites
          for satellite in satellites:
               if satellite.model.satnum == int(sat_id):
                    self.name = satellite.name
                    break
               else:
                    self.name = "Name unavailable"
          name = self.name
          self.by_number = by_number
          self.base = base
          self.ts = ts
          try:
               self.satellite = self.by_number[int(self.sat_id)]
          except KeyError:
               updateUsedTLEs()
               self.__init__(self, sat_id, x, sat_info, name, now, satellites, by_number, base, ts)

     def run(self):
          trackSat, name, now, y, mo, d, h, date, by_number, base, ts, satellite, index = self.sat_id, self.name, self.now, self.y, self.mo, self.d, self.h, self.date, self.by_number, self.base, self.ts, self.satellite, self.index
          run=True
          t = ts.now()
          difference = satellite - base
          topocentric = difference.at(t)
          alt, az, distance = topocentric.altaz()
          targetAlt = alt.degrees # elevation in degrees
          targetAz = az.degrees # azimuth in degrees
          distance = ('{:.1f} km'.format(distance.km)) # distance in kilometers
          geocentric = satellite.at(t)
          lat, lon = wgs84.latlon_of(geocentric)
          lat=lat.degrees # latitude above earth
          lon=lon.degrees # longitude above earth
          horizon = targetAlt > 0 # false if below horizon true if above
          self.sat_info[index-1] = [index, name, trackSat, targetAlt, targetAz, horizon, distance, lat, lon]

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
          self.ui.actionManual_TLE_update.triggered.connect(fetchTLEs)
          self.ui.actionManual_TLE_update.triggered.connect(updateUsedTLEs)

          self.threads = []
          self.event_loop = QEventLoop()
                    
          timer = QTimer(self)
          timer.timeout.connect(lambda: self.update_sat_info())
          timer.start(int(read.UpdateRate))
          
     def restoreDefaults(self, preferences_window):
          loader = QUiLoader()
          confirm_ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui files", "ConfirmChoice.ui")
          confirm_window = loader.load(confirm_ui_path, None)
          confirm_window.YesButton.clicked.connect(lambda: writeDefPrefsFile())
          confirm_window.YesButton.clicked.connect(lambda: confirm_window.close())
          confirm_window.YesButton.clicked.connect(lambda: self.refresh_preferences())
          confirm_window.YesButton.clicked.connect(lambda: preferences_window.close())
          confirm_window.NoButton.clicked.connect(lambda: confirm_window.close())
          confirm_window.show()
          loop = QEventLoop()
          loop.exec()
     def open_preferences(self):
          location = read.location
          TLEsources = read.TLEsources
          TLEupdate = read.TLEupdate
          SatIDs = read.SatIDs
          latitude, longitude = location
          period, unit = TLEupdate

          loader = QUiLoader()
          preferences_ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui files", "Preferences.ui")
          preferences_window = loader.load(preferences_ui_path, None)
          
          preferences_window.LatInputBox.setText(str(latitude))
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


          preferences_window.SaveButton_2.clicked.connect(lambda: self.updateTimers(preferences_window))
          preferences_window.SaveButton_2.clicked.connect(lambda: writeNewPrefsFile(preferences_window))
          preferences_window.SaveButton_2.clicked.connect(lambda: self.refresh_preferences())
          preferences_window.CancelButton.clicked.connect(lambda: preferences_window.close())
          preferences_window.RestoreDefButton.clicked.connect(lambda: self.restoreDefaults(preferences_window))
          preferences_window.GeolocateButton.clicked.connect(lambda: (preferences_window.LatInputBox.setText(str(geolocate.latitude))))
          preferences_window.GeolocateButton.clicked.connect(lambda: (preferences_window.LonInputBox.setText(str(geolocate.longitude))))
          preferences_window.GeolocateButton.clicked.connect(lambda: (print(f"Accuracy is within {geolocate.accuracy} meters." if geolocate.accuracy else "Accuracy estimate not available")))
          preferences_window.LoadButton.clicked.connect(lambda: (preferences_window.LatInputBox.setText(read.latitude)))
          preferences_window.LoadButton.clicked.connect(lambda: (preferences_window.LonInputBox.setText(read.longitude)))

          preferences_window.TLEadd.clicked.connect(lambda: addSource(preferences_window))
          preferences_window.TLEremove.clicked.connect(lambda: deleteSource(preferences_window))
          
          preferences_window.SatelliteAdd.clicked.connect(lambda: addSat(preferences_window))
          preferences_window.SatelliteRemove.clicked.connect(lambda: deleteSat(preferences_window))
          
          preferences_window.show()
          loop = QEventLoop()
          loop.exec()
     def refresh_preferences(self):
          try:
               with open("prefs.json", "r") as f:
                    config = json.load(f)
                    read.location = config["location"]
                    read.TLEsources = config["tle_sources"]
                    read.TLEupdate = config["tle_update"]
                    read.SatIDs = config["satellite_ids"]
                    read.UpdateRate = config["update_rate"]
          except FileNotFoundError:
               writeDefPrefsFile()
               self.refresh_preferences()


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

     def updateTimers(self, preferences_window):
          newUpdate = str(preferences_window.UpdateRate.text())
          if newUpdate!=read.UpdateRate:
               self.timer.stop()
               self.timer.start(newUpdate)

     def create_threads(self, SatIDs, latitude, longitude):
          index = 0
          sat_info = []
          self.sat_info = sat_info
          self.total_threads = 0
          self.finished_threads = 0
          for sat_id in SatIDs:
               index+=1
               self.total_threads+=1
               sat_info.append([])
               name = "name"
               now = datetime.now()
               try:
                    satellites = load.tle_file("UsedTLEs.txt", reload=True)
               except:
                    fetchTLEs()
                    updateUsedTLEs()
               by_number = {sat.model.satnum: sat for sat in satellites}
               base = wgs84.latlon(float(latitude), float(longitude))
               ts = load.timescale()
               worker = Worker(sat_id, index, sat_info, now, satellites, by_number, base, ts)
               worker.start()
               worker.finished.connect(lambda: self.increment_threads())
               self.threads.append(worker)

     def update_sat_info(self):
          self.create_threads(read.SatIDs, read.latitude, read.longitude)
          self.event_loop = QEventLoop()
          QTimer.singleShot(0, self.event_loop.quit)
          self.event_loop.exec()
          while self.sat_info[(len(self.sat_info) - 1)] == []:
               time.sleep(0.01)
               print("Final thread is not finished. Waiting for completion.....")
          print(self.sat_info, "\n")



     def increment_threads(self):
          self.finished_threads += 1
          if self.finished_threads+1 == self.total_threads:
               self.event_loop.quit()

if __name__ == "__main__":
     QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
     app=QApplication(sys.argv)
     window=main()
     window.show()
     sys.exit(app.exec())