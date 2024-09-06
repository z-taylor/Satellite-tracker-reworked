import sys
from PySide6 import QtCore
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QTimer, QThread, QEventLoop, Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel, QColor, QBrush
import os
import platform
import json
import re
import geocoder
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
from skyfield.api import load, wgs84
import time

def cloneMissingUIfiles(filePath, gitPath):
     print(f"UI file {filePath} missing, cloning from GitHub.....")
     directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_files")
     errorDirectory = os.path.join(directory, "errors")
     if not os.path.exists(directory):
          print(f"Directory {directory} not found, creating it...")
          os.makedirs(directory)
          os.makedirs(errorDirectory)
     if not os.path.exists(errorDirectory):
          print(f"Directory {errorDirectory} not found, creating it...")
          os.makedirs(errorDirectory)
     import subprocess
     gitURL = "https://raw.githubusercontent.com/z-taylor/Satellite-tracker-reworked/main/ui_files"
     gitPath = str(gitURL) + "/" + str(gitPath)
     try:
          subprocess.run(["curl", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
          try:
               subprocess.run(["curl", "-o", filePath, gitPath], check=True)
               print("UI files cloned successfully")
          except subprocess.CalledProcessError as e:
               print(f"Failed to clone UI files: {e}")
     except:
          if str(platform.system()) == "Linux":
               try:
                    print("Installing git.....")
                    subprocess.run(["sudo", "apt-get", "update"], check=True)
                    subprocess.run(["sudo", "apt-get", "install", "-y", "curl"], check=True)
                    print("Git installed successfully")
               except subprocess.CalledProcessError as e:
                    print(f"Failed to install curl: {e}")
          elif str(platform.system()) == "Windows":
               try:
                    print("Installing git.....")
                    subprocess.run(["winget", "install", "Curl.Curl", "--silent"], check=True)
                    print("Git installed successfully on Windows using winget.")
               except subprocess.CalledProcessError as e:
                    print(f"Failed to install curl: {e}")
          else:
               print("Your OS is not officially supported. Either try manually installing curl or manually copying the missing ui files and try again")

def error(self, path):
     if not QApplication.instance():
         app = QApplication(sys.argv)
     loader = QUiLoader()
     try:
          error_ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_files", "errors", path)
          error_window = loader.load(error_ui_path, None)
     except:
          filePath = (os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_files", "errors", path))
          gitPath = ("errors") + "/" + str(path)
          cloneMissingUIfiles(filePath, gitPath)
          error_ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_files", "errors", path)
          error_window = loader.load(error_ui_path, None)
     self.windows.append(error_window)
     error_window.OKbutton.clicked.connect(error_window.close)
     error_window.OKbutton.clicked.connect(lambda: self.windows.remove(error_window))
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
          "last_tle_update" : "2024-09-03 12:00:00",
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
def writeNewPrefsFile(self, preferences_window):
     try:
          with open("prefs.json", "r") as f:
               config = json.load(f)
          newlastTLEupdate = config["last_tle_update"]
          newRadConfig = config["radio_config"]
          newRotConfig = config["rotator_config"]
     except FileNotFoundError:
          writeDefPrefsFile()
          with open("prefs.json", "r") as f:
               config = json.load(f)
          newlastTLEupdate = config["last_tle_update"]
          newRadConfig = config["radio_config"]
          newRotConfig = config["rotator_config"]

     newLocation = [preferences_window.LatInputBox.text(), preferences_window.LonInputBox.text()]
     latitude, longitude = newLocation
     latitude_pattern = re.compile(r"^-?(90(\.0{1,6})?|[1-8]?\d(\.\d{1,6})?)$")
     longitude_pattern = re.compile(r"^-?(180(\.0{1,6})?|1[0-7]\d(\.\d{1,6})?|[1-9]?\d(\.\d{1,6})?)$")
     if not latitude_pattern.match(str(latitude)) and longitude_pattern.match(str(longitude)):
          error(self, "ErrorLatLon.ui")
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
                    error(self, "ErrorSource_1orMore.ui")
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
                    error(self, "ErrorID_1orMore.ui")
                    return
     except(AttributeError):
          print("Warning: ID table is empty")
     if re.fullmatch(r'\d+', str(preferences_window.UpdateRate.text())):
          if float(preferences_window.UpdateRate.text()) > 0:
               newUpdateRate = preferences_window.UpdateRate.text()
          else: 
               error(self, "ErrorUpdateTooLow.ui")
               return
     else:
          error(self, "ErrorUpdateNumbersOnly.ui")
          return
     

     newConfig = {
          "location": newLocation,
          "tle_sources": newSources,
          "tle_update" : newUpdate,
          "satellite_ids": newIDs,
          "update_rate" : newUpdateRate,
          "last_tle_update" : newlastTLEupdate,
          "radio_config": newRadConfig,
          "rotator_config": newRotConfig
     }
     with open("prefs.json", "w") as f:
          json.dump(newConfig, f, indent=4)

def addSource(self, preferences_window):
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
          error(self, "ErrorSource.ui")
          return  
def deleteSource(preferences_window):
     selection_model = preferences_window.TLElist.selectionModel()
     selected_indexes = selection_model.selectedIndexes()
     if selected_indexes:
          selected_index = selected_indexes[0]
          model = preferences_window.TLElist.model()
          model.removeRow(selected_index.row())

def addSat(self, preferences_window):
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
          error(self, "ErrorID.ui")
          return
def deleteSat(preferences_window):
     selection_model = preferences_window.SatelliteList.selectionModel()
     selected_indexes = selection_model.selectedIndexes()
     if selected_indexes:
          selected_index = selected_indexes[0]
          model = preferences_window.SatelliteList.model()
          model.removeRow(selected_index.row())

class read:
     def __init__(self, mainSelf):
          self.mainSelf = mainSelf
          try:
               with open("prefs.json", "r") as f:
                    config = json.load(f)
               self.location = config["location"]
               self.TLEsources = config["tle_sources"]
               self.TLEupdate = config["tle_update"]
               self.lastTLEupdate = config["last_tle_update"]
               self.SatIDs = config["satellite_ids"]
               self.UpdateRate = config["update_rate"]
               self.RadConfig = config["radio_config"]
               self.RotConfig = config["rotator_config"]
          except:
               writeDefPrefsFile()
               with open("prefs.json", "r") as f:
                    config = json.load(f)
               self.location = config["location"]
               self.TLEsources = config["tle_sources"]
               self.TLEupdate = config["tle_update"]
               self.lastTLEupdate = config["last_tle_update"]
               self.SatIDs = config["satellite_ids"]
               self.UpdateRate = config["update_rate"]
               self.RadConfig = config["radio_config"]
               self.RotConfig = config["rotator_config"]
               error(self.mainSelf, "ErrorRead.ui")

          self.latitude, self.longitude = self.location
          self.period, self.unit = self.TLEupdate

def fetchTLEs(self):
     print("Updating TLEs.....")
     urls = self.read_instance.TLEsources
     unique_tles = set()
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
               try:
                    error_ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_files", "errors", "ErrorBrokenTle.ui")
                    error_window = loader.load(error_ui_path, None)
               except:
                    filePath = (os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_files", "errors", "ErrorBrokenTle.ui"))
                    gitPath = "errors" + "/" + "ErrorBrokenTle.ui"
                    cloneMissingUIfiles(filePath, gitPath)
                    error_ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_files", "errors", "ErrorBrokenTle.ui")
                    error_window = loader.load(error_ui_path, None)
               error_window.label.text(f"One or more broken TLE sources. The link may be typed incorrectly or the website may be down.\nError code: {status}\nBroken link: {url}")
               error_window.OKbutton.clicked.connect(error_window.close)
               error_window.show()
               loop = QEventLoop()
               loop.exec()
               return
     print("TLE update finished")
def updateUsedTLEs(self):
     print("Updating active satellites list.....")
     target_norad_ids = self.read_instance.SatIDs
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
     def __init__(self, mainSelf, sat_id, x, sat_info, now, satellites, by_number, base, ts):
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
          try:
               for satellite in satellites:
                    if satellite.model.satnum == int(sat_id):
                         self.name = satellite.name
                         break
                    else:
                         self.name = "Name unavailable"
               
               name = self.name
          except:
               print("TLE file empty or formatted incorrectly. Refreshing TLEs and restarting thread(s).....")
               raise ValueError(2)
               
               name = self.name
          self.by_number = by_number
          self.base = base
          self.ts = ts
          try:
               self.satellite = self.by_number[int(self.sat_id)]
          except KeyError:
               print(f"Satellite ID {self.sat_id} not found. Updating active TLE list and restarting thread.....")
               raise ValueError(1)

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
          nextEvent = "Next Event" #shows next event, will work on later
          self.sat_info[index-1] = [name, trackSat, targetAlt, targetAz, horizon, nextEvent, distance, lat, lon]

class main(QMainWindow):
     def __init__(self):
          super(main, self).__init__()
          loader = QUiLoader()
          try:
               ui_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_files", "SatelliteTracker.ui")
               self.ui = loader.load(ui_file_path, None)
          except:
               filePath = (os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_files", "SatelliteTracker.ui"))
               gitPath = "SatelliteTracker.ui"
               cloneMissingUIfiles(filePath, gitPath)
               ui_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_files", "SatelliteTracker.ui")
               self.ui = loader.load(ui_file_path, None)
          self.setCentralWidget(self.ui)

          self.windows = []
          self.read_instance = read(self)
          
          self.ui.actionPreferences.triggered.connect(self.open_preferences)
          self.ui.actionRadio.triggered.connect(self.open_radio)
          self.ui.actionRotator.triggered.connect(self.open_rotator)
          self.ui.actionManual_TLE_update.triggered.connect(lambda: fetchTLEs(self))
          self.ui.actionManual_TLE_update.triggered.connect(lambda: updateUsedTLEs(self))

          self.threads = []
          self.event_loop = QEventLoop()
          updateUnit = self.read_instance.unit
          self.timer2 = QTimer(self)
          self.timer2.timeout.connect(lambda: self.tleUpdate(updateUnit))
          self.timer2.start(1000)
          
          self.tableView = self.ui.tableView
          headers = [
               "Satellite name", "Norad ID", "Elevation", "Azimuth",
               "Above horizon", "Next event", "Distance", "Latitude", "Longitude"
          ]
          model = QStandardItemModel()
          model.setHorizontalHeaderLabels(headers)
          self.tableView.setModel(model)
          self.timer1 = QTimer(self)
          self.timer1.timeout.connect(lambda: self.update_sat_info(self.tableView, model))
          self.timer1.start(int(self.read_instance.UpdateRate))
          
     def restoreDefaults(self, preferences_window):
          loader = QUiLoader()
          try:
               confirm_ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_files", "ConfirmChoice.ui")
               confirm_window = loader.load(confirm_ui_path, None)
          except:
               filePath = (os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_files", "ConfirmChoice.ui"))
               gitPath = "ConfirmChoice.ui"
               cloneMissingUIfiles(filePath, gitPath)
               confirm_ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_files", "ConfirmChoice.ui")
               confirm_window = loader.load(confirm_ui_path, None)
          self.windows.append(confirm_window)
          confirm_window.YesButton.clicked.connect(lambda: writeDefPrefsFile())
          confirm_window.YesButton.clicked.connect(lambda: confirm_window.close())
          confirm_window.YesButton.clicked.connect(lambda: self.windows.remove(confirm_window))
          confirm_window.YesButton.clicked.connect(lambda: self.refresh_preferences())
          confirm_window.YesButton.clicked.connect(lambda: preferences_window.close())
          confirm_window.YesButton.clicked.connect(lambda: self.windows.remove(preferences_window))
          confirm_window.NoButton.clicked.connect(lambda: confirm_window.close())
          confirm_window.NoButton.clicked.connect(lambda: self.windows.remove(confirm_window))
          confirm_window.show()
          loop = QEventLoop()
          loop.exec()
     def open_preferences(self):
          location = self.read_instance.location
          TLEsources = self.read_instance.TLEsources
          TLEupdate = self.read_instance.TLEupdate
          SatIDs = self.read_instance.SatIDs
          latitude, longitude = location
          period, unit = TLEupdate

          loader = QUiLoader()
          try:
               preferences_ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_files", "Preferences.ui")
               preferences_window = loader.load(preferences_ui_path, None)
          except:
               filePath = (os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_files", "Preferences.ui"))
               gitPath = "Preferences.ui"
               cloneMissingUIfiles(filePath, gitPath)
               preferences_ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_files", "Preferences.ui")
               preferences_window = loader.load(preferences_ui_path, None)
          self.windows.append(preferences_window)
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
          preferences_window.SaveButton_2.clicked.connect(lambda: writeNewPrefsFile(self, preferences_window))
          preferences_window.SaveButton_2.clicked.connect(lambda: self.refresh_preferences())
          preferences_window.CancelButton.clicked.connect(lambda: preferences_window.close())
          preferences_window.CancelButton.clicked.connect(lambda: self.windows.remove(preferences_window))
          preferences_window.RestoreDefButton.clicked.connect(lambda: self.restoreDefaults(preferences_window))
          preferences_window.GeolocateButton.clicked.connect(lambda: (preferences_window.LatInputBox.setText(str(geolocate.latitude))))
          preferences_window.GeolocateButton.clicked.connect(lambda: (preferences_window.LonInputBox.setText(str(geolocate.longitude))))
          preferences_window.GeolocateButton.clicked.connect(lambda: (print(f"Accuracy is within {geolocate.accuracy} meters." if geolocate.accuracy else "Accuracy estimate not available")))
          preferences_window.LoadButton.clicked.connect(lambda: (preferences_window.LatInputBox.setText(self.read_instance.latitude)))
          preferences_window.LoadButton.clicked.connect(lambda: (preferences_window.LonInputBox.setText(self.read_instance.longitude)))

          preferences_window.TLEadd.clicked.connect(lambda: addSource(self, preferences_window))
          preferences_window.TLEremove.clicked.connect(lambda: deleteSource(preferences_window))
          
          preferences_window.SatelliteAdd.clicked.connect(lambda: addSat(self, preferences_window))
          preferences_window.SatelliteRemove.clicked.connect(lambda: deleteSat(preferences_window))
          
          preferences_window.show()
          loop = QEventLoop()
          loop.exec()
     def refresh_preferences(self):
          try:
               with open("prefs.json", "r") as f:
                    config = json.load(f)
                    self.read_instance.location = config["location"]
                    self.read_instance.latitude, self.read_instance.longitude = self.read_instance.location
                    self.read_instance.TLEsources = config["tle_sources"]
                    self.read_instance.TLEupdate = config["tle_update"]
                    self.read_instance.SatIDs = config["satellite_ids"]
                    self.read_instance.UpdateRate = config["update_rate"]
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
          
          try:
               radio_ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_files", "Radio.ui")
               radio_window = loader.load(radio_ui_path, None)
          except:
               filePath = (os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_files", "Radio.ui"))
               gitPath = "Rotator.ui"
               cloneMissingUIfiles(filePath, gitPath)
               radio_ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_files", "Radio.ui")
               radio_window = loader.load(radio_ui_path, None)
          
          radio_window.saveButton.clicked.connect(self.radSave)
          radio_window.connectButton.clicked.connect(self.radConnect)
          self.windows.append(radio_window)
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
          try:
               rotator_ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_files", "Rotator.ui")
               rotator_window = loader.load(rotator_ui_path, None)
          except:
               filePath = (os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_files", "Rotator.ui"))
               gitPath = "Rotator.ui"
               cloneMissingUIfiles(filePath, gitPath)
               rotator_ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_files", "Rotator.ui")
               rotator_window = loader.load(rotator_ui_path, None)
          rotator_window.saveButton.clicked.connect(self.rotSave)
          rotator_window.connectButton.clicked.connect(self.rotConnect)
          self.windows.append(rotator_window)
          rotator_window.show()
          loop = QEventLoop()
          loop.exec()

     def updateTimers(self, preferences_window):
          newUpdate = str(preferences_window.UpdateRate.text())
          if newUpdate!=self.read_instance.UpdateRate:
               self.timer1.stop()
               self.timer1.start(int(newUpdate))
          newTLEs = []
          model = preferences_window.TLElist.model()
          for index in range(model.rowCount()):
               item_index = model.index(index, 0)
               item_text = model.data(item_index)
               newTLEs.append(item_text)
          if newTLEs!=self.read_instance.TLEsources:
               if newUpdate!=self.read_instance.UpdateRate:
                    fetchTLEs(self)
                    updateUsedTLEs(self)
                    self.timer1.stop()
                    self.timer1.start(int(newUpdate))
               else:
                    fetchTLEs(self)
                    updateUsedTLEs(self)
                    self.timer1.stop()
                    self.timer1.start(int(self.read_instance.UpdateRate))

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
                    fetchTLEs(self)
                    updateUsedTLEs(self)
               by_number = {sat.model.satnum: sat for sat in satellites}
               base = wgs84.latlon(float(latitude), float(longitude))
               ts = load.timescale()
               try:
                    worker = Worker(self, sat_id, index, sat_info, now, satellites, by_number, base, ts)
                    worker.start()
                    worker.finished.connect(lambda: self.increment_threads())
                    self.threads.append(worker)
               except ValueError as e:
                    if e.args[0] == 1:
                         print(f"Restarting thread {index}.....")
                         updateUsedTLEs(self)
                         satellites = load.tle_file("UsedTLEs.txt", reload=True)
                         by_number = {sat.model.satnum: sat for sat in satellites}
                         worker = Worker(self, sat_id, index, sat_info, now, satellites, by_number, base, ts)
                         worker.start()
                         print(f"Thread {index} restarted")
                         worker.finished.connect(lambda: self.increment_threads())
                         self.threads.append(worker)
                    elif e.args[0] == 2:
                         print(f"Restarting thread {index}.....")
                         fetchTLEs(self)
                         updateUsedTLEs(self)
                         satellites = load.tle_file("UsedTLEs.txt", reload=True)
                         by_number = {sat.model.satnum: sat for sat in satellites}
                         worker = Worker(self, sat_id, index, sat_info, now, satellites, by_number, base, ts)
                         worker.start()
                         print(f"Thread {index} restarted")
                         worker.finished.connect(lambda: self.increment_threads())
                         self.threads.append(worker)

     def tleUpdate(self, updateUnit):
          run = True
          date1 = self.read_instance.lastTLEupdate
          if isinstance(self.read_instance.lastTLEupdate, str):
               date1 = datetime.strptime(date1, "%Y-%m-%d %H:%M:%S")
          date2 = datetime(int(datetime.now().strftime("%Y").lstrip("0")), int(datetime.now().strftime("%m").lstrip("0")), int(datetime.now().strftime("%d").lstrip("0")), int(datetime.now().strftime("%H").lstrip("0")))
          difference = relativedelta(date2, date1)
          differenceMonths = difference.months
          differenceWeeks = difference.days // 7
          differenceDays = difference.days
          differenceHours = difference.hours
          differenceWeeks += (differenceMonths * (365/12/7)) if differenceMonths > 0 else 0
          differenceDays += (differenceWeeks * 7) if differenceWeeks > 0 else 0
          differenceHours += (differenceDays * 24) if differenceDays > 0 else 0
          if updateUnit == "Months" and differenceMonths >= self.read_instance.period and run == True:
               self.read_instance.lastTLEupdate = date2
               newConfig = {
                    "location": self.read_instance.location,
                    "tle_sources": self.read_instance.TLEsources,
                    "tle_update" : self.read_instance.TLEupdate,
                    "satellite_ids": self.read_instance.SatIDs,
                    "update_rate" : self.read_instance.UpdateRate,
                    "last_tle_update" : date2,
                    "radio_config": self.read_instance.RadConfig,
                    "rotator_config": self.read_instance.RotConfig
               }
               with open("prefs.json", "w") as f:
                    json.dump(newConfig, f, indent=4)
               fetchTLEs(self)
               updateUsedTLEs(self)
               run = False
          if updateUnit == "Weeks" and differenceWeeks >= self.read_instance.period and run == True:
               self.read_instance.lastTLEupdate = date2
               newConfig = {
                    "location": self.read_instance.location,
                    "tle_sources": self.read_instance.TLEsources,
                    "tle_update" : self.read_instance.TLEupdate,
                    "satellite_ids": self.read_instance.SatIDs,
                    "update_rate" : self.read_instance.UpdateRate,
                    "last_tle_update" : date2,
                    "radio_config": self.read_instance.RadConfig,
                    "rotator_config": self.read_instance.RotConfig
               }
               with open("prefs.json", "w") as f:
                    json.dump(newConfig, f, indent=4)
               fetchTLEs(self)
               updateUsedTLEs(self)
               run = False
          if updateUnit == "Days" and differenceDays >= self.read_instance.period and run == True:
               self.read_instance.lastTLEupdate = date2
               newConfig = {
                    "location": self.read_instance.location,
                    "tle_sources": self.read_instance.TLEsources,
                    "tle_update" : self.read_instance.TLEupdate,
                    "satellite_ids": self.read_instance.SatIDs,
                    "update_rate" : self.read_instance.UpdateRate,
                    "last_tle_update" : date2,
                    "radio_config": self.read_instance.RadConfig,
                    "rotator_config": self.read_instance.RotConfig
               }
               with open("prefs.json", "w") as f:
                    json.dump(newConfig, f, indent=4)
               fetchTLEs(self)
               updateUsedTLEs(self)
               run = False
          if updateUnit == "Hours" and differenceHours >= self.read_instance.period and run == True:
               self.read_instance.lastTLEupdate = date2
               newConfig = {
                    "location": self.read_instance.location,
                    "tle_sources": self.read_instance.TLEsources,
                    "tle_update" : self.read_instance.TLEupdate,
                    "satellite_ids": self.read_instance.SatIDs,
                    "update_rate" : self.read_instance.UpdateRate,
                    "last_tle_update" : str(date2),
                    "radio_config": self.read_instance.RadConfig,
                    "rotator_config": self.read_instance.RotConfig
               }
               with open("prefs.json", "w") as f:
                    json.dump(newConfig, f, indent=4)
               fetchTLEs(self)
               updateUsedTLEs(self)
     def update_sat_info(self, tableView, model):
          self.create_threads(self.read_instance.SatIDs, self.read_instance.latitude, self.read_instance.longitude)
          self.event_loop = QEventLoop()
          QTimer.singleShot(0, self.event_loop.quit)
          self.event_loop.exec()
          while self.sat_info[(len(self.sat_info) - 1)] == []:
               time.sleep(0.01)
          model.removeRows(0, model.rowCount())
          for row_data in self.sat_info:
               items = [QStandardItem(str(item)) for item in row_data]
               model.appendRow(items)
               for item in items:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
          for row in range(model.rowCount()):
               status_item = model.item(row, 4)
               if status_item:
                    is_false = status_item.text().lower() == 'false'
                    color = QColor("red") if is_false else QColor("green")
                    for col in range(2, 5):
                         item = model.item(row, col)
                         if item:
                              item.setForeground(QBrush(color))
          tableView.resizeColumnsToContents()

     def increment_threads(self):
          self.finished_threads += 1
          if self.finished_threads == self.total_threads:
               self.threads.clear()
               self.event_loop.quit()
     def closeEvent(self, event):
          for thread in self.threads:
                    thread.wait()
                    self.threads.remove(thread)
          for window in self.windows:
               window.close()

if __name__ == "__main__":
     QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
     app=QApplication(sys.argv)
     window=main()
     window.show()
     sys.exit(app.exec())
