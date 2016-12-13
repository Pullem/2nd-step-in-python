import configparser
import os
import subprocess

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QGridLayout, QDialog, QCheckBox, QLabel,
							 QPushButton)


class OptionsDialog:
	def __init__(self, win):
		super().__init__()
		print("initializing Options Dialog")

		self.mainWindow = win

		self.setOptions()
		self.layoutOptions()

		self.loadOptions()

	def setOptions(self):
		self.shutdownCheckBox = QCheckBox('Shutdown on completion')

		self.profileCheckBox = QCheckBox('Select last used profile')
		self.outputDirectoryCheckBox = QCheckBox(
			'Use the previous output directory')

		self.abortShutdownButton = QPushButton('Abort Shutdown')
		self.abortShutdownButton.clicked.connect(self.cancelShutdown)

		self.okButton = QPushButton('   OK   ')
		self.okButton.clicked.connect(self.saveOptions)
		self.cancelButton = QPushButton(' Cancel ')
		self.cancelButton.clicked.connect(self.exit)

	def layoutOptions(self):
		emptyCell = QLabel('')

		grid = QGridLayout()
		grid.addWidget(self.shutdownCheckBox, 0, 0)
		grid.addWidget(self.profileCheckBox, 1, 0)
		grid.addWidget(self.outputDirectoryCheckBox, 2, 0)
		grid.addWidget(emptyCell, 3, 0)

		grid.addWidget(self.abortShutdownButton, 4, 0)
		grid.addWidget(self.okButton, 4, 2)
		grid.addWidget(self.cancelButton, 4, 3)

		self.optionsWindow = QDialog(self.mainWindow,
									 Qt.WindowCloseButtonHint)
		self.optionsWindow.setWindowIcon(QIcon(os.path.normpath(
			'./Icons/transparent.png')))
		self.optionsWindow.setWindowTitle('Options')
		self.optionsWindow.setMinimumSize(400, 170)

		self.optionsWindow.setFixedSize(self.optionsWindow.size())
		self.optionsWindow.setLayout(grid)

	def loadOptions(self):
		if not os.path.isfile('./data/options.ini'):
			self.defaultOptions()

		config = configparser.ConfigParser()
		config.read(os.path.normpath('./data/options.ini'))

		self.shutdownCheckBox.setChecked(config.getboolean('Main', 'Shutdown'))

		self.profileCheckBox.setChecked(
			config.getboolean('Main', 'RememberProfile'))

		self.outputDirectoryCheckBox.setChecked(
			config.getboolean('Main', 'RememberOutput'))

	def cancelShutdown(self):
		subprocess.call(["shutdown", "-a"])

	def saveOptions(self):
		config = configparser.ConfigParser()
		config.read(os.path.normpath('./data/options.ini'))

		config['Main']['Shutdown'] = str(self.shutdownCheckBox.isChecked())
		config['Main']['RememberProfile'] = str(
			self.profileCheckBox.isChecked())
		config['Main']['RememberOutput'] = str(
			self.outputDirectoryCheckBox.isChecked())

		with open('./data/options.ini', 'w') as configfile:
			config.write(configfile)

		self.optionsWindow.close()

	def exit(self):
		self.optionsWindow.close()

	def defaultOptions(self):
		config = configparser.ConfigParser()
		config.read(os.path.normpath('./data/options.ini'))

		config['Main'] = {}
		config['Main']['Shutdown'] = 'False'

		config['Main']['RememberProfile'] = 'False'
		config['Main']['PreviousProfile'] = ''

		config['Main']['RememberOutput'] = 'False'
		config['Main']['PreviousOutput'] = ''

		with open('./data/options.ini', 'w') as configfile:
			config.write(configfile)
