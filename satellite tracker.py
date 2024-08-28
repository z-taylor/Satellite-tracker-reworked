import sys
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import QApplication, QMainWindow, QDialog, QWidget, QDialogButtonBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QTimer, QThread, QEventLoop, Signal
import os


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
      def savePrefs(self):
            print("save")
      def cancelPrefs(self):
            print("cancel")
      def restoreDefaults(self):
            print("restore defaults")
      def open_preferences(self):
            loader = QUiLoader()
            preferences_ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui files", "Preferences.ui")
            preferences_window = loader.load(preferences_ui_path, None)
            preferences_window.SaveButton_2.clicked.connect(self.savePrefs)
            preferences_window.CancelButton.clicked.connect(self.cancelPrefs)
            preferences_window.RestoreDefButton.clicked.connect(self.restoreDefaults)
            preferences_window.show()
            loop = QEventLoop()
            loop.exec()
      def open_radio(self):
            loader = QUiLoader()
            radio_ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui files", "Radio.ui")
            radio_window = loader.load(radio_ui_path, None)
            radio_window.show()
            loop = QEventLoop()
            loop.exec()
      def open_rotator(self):
            loader = QUiLoader()
            rotator_ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui files", "Rotator.ui")
            rotator_window = loader.load(rotator_ui_path, None)
            rotator_window.show()
            loop = QEventLoop()
            loop.exec()
     
if __name__ == "__main__":
      QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
      app=QApplication(sys.argv)
      window=main()
      window.show()
      sys.exit(app.exec())