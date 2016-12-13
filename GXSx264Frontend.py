import sys, os, configparser, queue, datetime, glob, ctypes, psutil, subprocess, zlib
import qdarkstyle

from PyQt5.QtWidgets import (QWidget, QApplication, QDesktopWidget, QGroupBox, 
	QGridLayout, QLabel, QLineEdit, QPushButton, QComboBox, QFileDialog,
	QMessageBox)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QProcess, QCoreApplication

os.chdir(os.path.dirname(os.path.realpath(sys.argv[0])))

ctypes.WinDLL('./tools/MediaInfo.dll')
from MediaInfoDLL3 import *

from fileManagement import FileManagement
from Settings import SettingsDialog
from Options import OptionsDialog

class HoverButton(QPushButton):
    mouseHover = pyqtSignal(bool)

    def __init__(self, parent=None):
        QPushButton.__init__(self, parent)
        self.setMouseTracking(True)

    def enterEvent(self, event):
        self.mouseHover.emit(True)
        self.setStyleSheet(
        	'padding: 0px;background-color: rgba(255, 255, 255, 20);')

    def leaveEvent(self, event):
        self.mouseHover.emit(False)
        self.setStyleSheet('padding: 0px;background-color: none;')

class MainWindow(QWidget, FileManagement):

	def __init__(self):
		super().__init__()

		self.initUI()
		self.layoutGrid()
		self.findProfiles()
		self.selectOptions()

		self.center()
		self.show()

	def initUI(self):
		# self.statusBar().showMessage('Select Source File(s) to Encode')
		self.setMinimumSize(600, 570)
		self.setWindowTitle(
			"GXS x264 Frontend v0.42 Another Heaven")
		self.setWindowIcon(QIcon(os.path.normpath('./Icons/gxs-256.ico')))

		self.fileListLabel = QLabel('Input Files')
		self.ProfileLabel = QLabel('Profile')
		self.outputLabel = QLabel('Output')

		self.ProfileLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
		self.outputLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

		self.setFileAdd()
		self.setMediaInfoText()
		self.setFileRemove()

		self.fileList.clicked.connect(self.updateMediaInfoGroupBox)

		self.optionsButton = QPushButton('Options')
		self.optionsButton.clicked.connect(self.openOptions)

		self.profileComboBox = QComboBox()

		self.profileLineEdit = QLineEdit()
		self.profileLineEdit.setReadOnly(True)
		self.profileLineEdit.setVisible(False)

		self.settingsButton = QPushButton('Settings')
		self.settingsButton.setStyleSheet('padding: 4px;border-radius: 2px;')
		self.settingsButton.clicked.connect(self.openSettings)

		self.outputLineEdit = QLineEdit()
		self.outputLineEdit.setPlaceholderText('Select an Output Directory')

		self.saveOutputButton = QPushButton('Browse')
		self.saveOutputButton.setStyleSheet('padding: 4px;border-radius: 2px;')
		self.saveOutputButton.clicked.connect(self.openOutputDirectory)

		self.startEncodeButton = QPushButton('     Start Encode     ')
		self.startEncodeButton.setStyleSheet('border-radius: 2px;')
		self.startEncodeButton.clicked.connect(self.readyToEncode)

		self.processQueue = queue.Queue()

		self.encodeProgressLabel = QLabel()
		self.encodeProgressLabel.setVisible(False)

		self.pauseEncodeButton = HoverButton()
		self.pauseEncodeButton.setIcon(QIcon(os.path.normpath(
			'./Icons/pause.png')))
		self.pauseEncodeButton.setIconSize(QSize(23, 23))
		self.pauseEncodeButton.setStyleSheet(
			'padding: 0px;border: none;background-color: none;')
		self.pauseEncodeButton.setToolTip('Pause')
		self.pauseEncodeButton.setVisible(False)
		self.pauseEncodeButton.clicked.connect(self.pauseEncode)

		self.resumeEncodeButton = HoverButton()
		self.resumeEncodeButton.setIcon(QIcon(os.path.normpath(
			'./Icons/resume.png')))
		self.resumeEncodeButton.setIconSize(QSize(23, 23))
		self.resumeEncodeButton.setStyleSheet(
			'padding: 0px;border: none;background-color: none;')
		self.resumeEncodeButton.setToolTip('Resume')
		self.resumeEncodeButton.setVisible(False)
		self.resumeEncodeButton.clicked.connect(self.resumeEncode)

		self.stopEncodeButton = HoverButton()
		self.stopEncodeButton.setIcon(QIcon(os.path.normpath(
			'./Icons/stop.png')))
		self.stopEncodeButton.setIconSize(QSize(23, 23))
		self.stopEncodeButton.setStyleSheet(
			'padding: 0px;border: none;background-color: none;')
		self.stopEncodeButton.setToolTip('Stop')
		self.stopEncodeButton.setVisible(False)
		self.stopEncodeButton.clicked.connect(self.stopEncode)

		self.process = QProcess()
		self.audioStreamProcess = QProcess()
		self.ffmpegEncodeProcess = QProcess()
		self.neroAacEncodeProcess = QProcess()
		self.mkvMergeProcess = QProcess()

	def openOutputDirectory(self):
		if self.outputLineEdit.text() == '':
			self.outputLineEdit.setText(QFileDialog.getExistingDirectory(self, 
			'Select Output Directory', '/home'))
		else:
			outputDir = (QFileDialog.getExistingDirectory(self, 
				'Select Output Directory', self.outputLineEdit.text()))
			if not outputDir == '':
				self.outputLineEdit.setText(outputDir)

	def openOptions(self):
		mainWindow = self

		options = OptionsDialog(mainWindow)

		self.fileList.setAcceptDrops(False)

		options.optionsWindow.exec_()

		self.fileList.setAcceptDrops(True)

	def openSettings(self):
		mainWindow = self

		settings = SettingsDialog(mainWindow, 
			self.profileComboBox.currentIndex())

		self.fileList.setAcceptDrops(False)

		settings.settingsWindow.exec_()

		self.fileList.setAcceptDrops(True)
		selected = settings.getSelectedProfile()
		self.refreshProfileList(selected)

	def selectOptions(self):
		if not os.path.exists(os.path.normpath('./temp')):
			os.makedirs(os.path.normpath('./temp'))

		if not os.path.exists(os.path.normpath('./data')):
			os.makedirs(os.path.normpath('./data'))

		if not os.path.isfile('./data/options.ini'):
			OptionsDialog.defaultOptions(self)

		config = configparser.ConfigParser()
		config.read(os.path.normpath('./data/options.ini'))

		if config.getboolean('Main','RememberProfile'):
			self.profileComboBox.setCurrentIndex(
				self.profileComboBox.findText(str(
					config.get('Main','PreviousProfile'))))

		if config.getboolean('Main','RememberOutput'):
			self.outputLineEdit.setText(str(
				config.get('Main','PreviousOutput')))

	"""
	Encoding process functions
	"""
	def readyToEncode(self):
		self.halt = False
		missingFieldDialog = QMessageBox(self)

		self.process = QProcess()
		self.audioStreamProcess = QProcess()
		self.ffmpegEncodeProcess = QProcess()
		self.neroAacEncodeProcess = QProcess()
		self.mkvMergeProcess = QProcess()

		if self.fileList.count() == 0:
			missingFieldDialog.setWindowTitle('Missing Input')
			missingFieldDialog.setText('Please import video files to encode.')
			missingFieldDialog.exec_()
			return -1
		elif self.outputLineEdit.text() == '':
			missingFieldDialog.setWindowTitle('Missing Output Directory')
			missingFieldDialog.setText('Please specify the output directory.')
			missingFieldDialog.exec_()
			return -1

		flag = True

		for index in range(self.fileList.count()):
			if not os.path.isfile(self.fileList.item(index).data(1001)):
				if flag:
					flag = False
					self.mediaInfoText.setPlainText('Error - files not found:')

				self.mediaInfoText.append(
					self.fileList.item(index).data(1001))
			else:
				self.mediaInfoGroupBox.setTitle('Output Log')

		if not flag:
			return None

		self.fileList.setAcceptDrops(False)
		self.fileList.setDragEnabled(False)
		self.fileList.clicked.disconnect()


		self.addFileButton.setEnabled(False)
		self.removeFileButton.setEnabled(False)
		self.removeAllButton.setEnabled(False)
		self.settingsButton.setEnabled(False)
		self.saveOutputButton.setEnabled(False)
		self.outputLineEdit.setReadOnly(True)

		self.profileComboBox.setVisible(False)
		self.profileLineEdit.setText(self.profileComboBox.currentText())
		self.profileLineEdit.setVisible(True)

		self.startEncodeButton.setVisible(False)
		self.encodeProgressLabel.setVisible(True)
		self.pauseEncodeButton.setVisible(True)
		self.stopEncodeButton.setVisible(True)

		config = configparser.ConfigParser()
		config.read(os.path.normpath('./data/options.ini'))

		if config.getboolean('Main','Shutdown'):
			self.mediaInfoText.setPlainText(
			'Shutdown on Completion is Enabled.  To Disable, Go to Options')
		else:
			self.mediaInfoText.clear()
		self.updateOptions()

		self.startEncode()


	def startEncode(self):
		files = glob.glob(os.path.normpath('./temp/*'))
		for f in files:
			os.remove(f)
		
		profileName = self.profileComboBox.currentText()

		self.encodeConfig = configparser.ConfigParser()
		self.encodeConfig.read(os.path.normpath(
			'./profiles/' + profileName + '.ini'))

		cmdOutput = self.encodeConfig.get('Misc','CommandLineOutput')
		cmdOutput += ' ' + self.encodeConfig.get('Misc', 'CustomCmdLine')
		self.curInputFile = 1
		self.totalInputFiles = 0

		for index in range(self.fileList.count()):
			completeCmdOutput = (os.path.normpath('./tools/' + cmdOutput) + 
				' --quiet --output ' + 
				'"' + os.path.normpath('./temp/Output.mkv') + '" ' + '"' +
				os.path.normpath(self.fileList.item(index).data(1001) + '"'))

			self.processQueue.put(completeCmdOutput)
			print(completeCmdOutput)
			print()

			self.totalInputFiles += 1

		now = datetime.datetime.now()
		self.mediaInfoText.append('[' + str(now.date()) + ' ' + 
			str(now.hour) + ':' + str(now.minute) + ':' + str(now.second) + 
			']  Encoding file ' + str(self.curInputFile) + '/' + 
			str(self.totalInputFiles) + '  -  ' + 
			self.fileList.item(self.curInputFile - 1).text() + '...')

		self.process.finished.connect(self.finishedCurrentVideoEncode)
		self.process.readyReadStandardError.connect(self.progressUpdate)

		self.process.start(self.processQueue.get())
		self.currentProcess = psutil.Process(self.process.processId())

	def progressUpdate(self):
		# print(self.process.readAllStandardError())
		curProgress = (bytes(self.process.readAllStandardError()).
			decode().strip().split('\r'))

		# print(curProgress[len(curProgress) - 1])
		self.encodeProgressLabel.setText(curProgress[len(curProgress) - 1])

	def finishedCurrentVideoEncode(self):
		if self.halt:
			return -1

		now = datetime.datetime.now()
		if self.process.exitCode() == -1:
			self.mediaInfoText.append('[' + str(now.date()) + ' ' + 
			str(now.hour) + ':' + str(now.minute) + ':' + str(now.second) + 
			']  Invalid Custom Command Line Input')

			self.mediaInfoText.append('\n[' + str(now.date()) + ' ' + 
				str(now.hour) + ':' + str(now.minute) + ':' + str(now.second) + 
				']  Stopping Encode')
			self.finishEncode()
		else:
			self.mediaInfoText.append('[' + str(now.date()) + ' ' + 
				str(now.hour) + ':' + str(now.minute) + ':' + str(now.second) +
				']  Video Encode Complete')
			self.encodeAudioStreams()

	def encodeAudioStreams(self):
		if self.halt:
			return -1

		now = datetime.datetime.now()
		if self.encodeConfig.getboolean('Misc','audiosource'):
			self.mediaInfoText.append('[' + str(now.date()) + ' ' + 
				str(now.hour) + ':' + str(now.minute) + ':' + str(now.second) +
				']  Using Source Audio')
			self.startMergeProcess()
			return None

		print('start identify')
		self.encodeProgressLabel.setText('Analyzing audio streams...')

		self.audioStreamProcess.finished.connect(self.startFfmEncode)
		self.audioStreamProcess.readyReadStandardOutput.connect(
			self.processTracks)

		self.ffmpegQueue = queue.Queue()
		self.neroAacQueue = queue.Queue()
		self.numAudioTracks = 1
		self.totalAudioTracks = 0

		mkvMergeCmd = ''
		if self.encodeConfig.get('System','architecture') == 32:
			mkvMergeCmd += os.path.normpath('./tools/' + 'mkvmerge32.exe ')
		else:
			mkvMergeCmd += os.path.normpath('./tools/' + 'mkvmerge64.exe ')

		print(mkvMergeCmd + ' --identify "' + 
			self.fileList.item(self.curInputFile - 1).data(1001) + '"')
		self.audioStreamProcess.start(mkvMergeCmd + ' --identify "' + 
			self.fileList.item(self.curInputFile - 1).data(1001) + '"')
		self.currentProcess = psutil.Process(
			self.audioStreamProcess.processId())

	def processTracks(self):
		print('processing tracks')
		output = (bytes(self.audioStreamProcess.readAllStandardOutput()).
			decode().strip().split('\r\n'))
		print(output)

		for line in output:
			line = line.split()

			print(line)
			if len(line) != 0 and line[0] == 'Track':
				if line[3] == 'audio':
					self.totalAudioTracks += 1

					ffmpegCmd = (os.path.normpath('./tools/ffmpeg.exe') + 
						' -i "' + os.path.normpath(self.fileList.item(
							self.curInputFile - 1).data(1001)) +
						'" -map 0:' + line[2][:-1] + ' -f wav "' + 
						os.path.normpath('./temp/OutputAudio' + 
							str(self.totalAudioTracks) + '.wav') + '"')

					neroAacCmd = (
						os.path.normpath('./tools/' + 'neroAacEnc.exe') + 
						' -ignorelength -q ' + 
						self.encodeConfig.get('Misc','audioquality') + 
						' -if "' + os.path.normpath('./temp/OutputAudio' + 
							str(self.totalAudioTracks) + '.wav') + '" -of "' + 
						os.path.normpath('./temp/OutputAudio' + 
							str(self.totalAudioTracks) + '.aac') + '"')

					print(ffmpegCmd)
					print(neroAacCmd)
					self.ffmpegQueue.put(ffmpegCmd)
					self.neroAacQueue.put(neroAacCmd)

		print('Broke Loop')

	def startFfmEncode(self):
		if self.halt:
			return -1

		self.audioStreamProcess.close()
		self.audioStreamProcess = QProcess()

		print('Start ffmpeg + nero encode')
		self.encodeProgressLabel.setText('Encoding audio stream ' +
		str(self.numAudioTracks) + '/' + str(self.totalAudioTracks) + '...')

		now = datetime.datetime.now()
		self.mediaInfoText.append('[' + str(now.date()) + ' ' + 
			str(now.hour) + ':' + str(now.minute) + ':' + str(now.second) + 
			']  Encoding Audio Stream ' + str(self.numAudioTracks) + '/' + 
			str(self.totalAudioTracks) + '...')

		self.ffmpegEncodeProcess.finished.connect(self.startNeroAacEncode)

		self.ffmpegEncodeProcess.start(self.ffmpegQueue.get())
		self.currentProcess = psutil.Process(
			self.ffmpegEncodeProcess.processId())

	def startNeroAacEncode(self):
		if self.halt:
			return -1

		self.ffmpegEncodeProcess.close()
		self.ffmpegEncodeProcess = QProcess()

		self.neroAacEncodeProcess.finished.connect(self.encodeNextAudioStream)

		self.numAudioTracks += 1
		self.neroAacEncodeProcess.start(self.neroAacQueue.get())
		self.currentProcess = psutil.Process(
			self.neroAacEncodeProcess.processId())

	def encodeNextAudioStream(self):
		print("In Audio Stream")
		if self.halt:
			return -1

		self.neroAacEncodeProcess.close()
		self.neroAacEncodeProcess = QProcess()

		now = datetime.datetime.now()
		self.mediaInfoText.append('[' + str(now.date()) + ' ' + 
			str(now.hour) + ':' + str(now.minute) + ':' + str(now.second) + 
			']  Finished Encoding Audio Stream')

		print('audiotrack ' + str(self.numAudioTracks))
		print('totalaudiotrack ' + str(self.totalAudioTracks))
		if self.numAudioTracks <= self.totalAudioTracks:
			print("Starting audio stream")

			self.ffmpegEncodeProcess.close()
			self.ffmpegEncodeProcess = QProcess()

			self.startFfmEncode()
		else:
			print("to merge process")
			self.startMergeProcess()

	def startMergeProcess(self):
		print("In merge process")
		if self.halt:
			return -1

		MI = MediaInfo()
		MI.Open(self.fileList.item(self.curInputFile - 1).data(1001))
		MI.Inform()

		mkvMergeCmd = ''
		if self.encodeConfig.get('System','architecture') == 32:
			mkvMergeCmd += os.path.normpath('./tools/' + 'mkvmerge32.exe ')
		else:
			mkvMergeCmd += os.path.normpath('./tools/' + 'mkvmerge64.exe ')

		mkvMergeCmd += ('-o "' + os.path.normpath(self.outputLineEdit.text() + 
			'/' + self.fileList.item(self.curInputFile - 1).text()[:-4] + 
			'[Encoded].mkv"'))

		self.encodedFile = (os.path.normpath(self.outputLineEdit.text() + 
			'/' + self.fileList.item(self.curInputFile - 1).text()[:-4] + 
			'[Encoded].mkv'))
		print(self.encodedFile)

		if not MI.Get(Stream.Video, 0, "Language") == '':
			mkvMergeCmd += (' --language "0:' + 
				MI.Get(Stream.Video, 0, "Language") + '"')

		mkvMergeCmd += (' "' + os.path.normpath('./temp/Output.mkv') + '" ')
		if self.encodeConfig.getboolean('Misc','audiosource'):
			mkvMergeCmd += ('-D "' + os.path.normpath(
				self.fileList.item(self.curInputFile - 1).data(1001)) + '"')
		else:
			for i in range(self.totalAudioTracks):
				mkvMergeCmd += ('--no-chapters ')

				if not MI.Get(Stream.Audio, i, "Language") == '':
					mkvMergeCmd += ('--language "0:' +
						MI.Get(Stream.Audio, i, "Language") + '" ')

				mkvMergeCmd += ('--track-name "0:AAC LC ' + 
					self.encodeConfig.get('Misc','audioquality') + '" "' 
					+ os.path.normpath('./temp/OutputAudio' + str(i+1) + 
					'.aac" '))
				# MI.Get(Stream.Audio, i, "Title") + '" "' + os.path.normpath(
				# 	'./temp/OutputAudio' + str(i+1) + '.aac" '))

			mkvMergeCmd += ('-D -A "' + os.path.normpath(
				self.fileList.item(self.curInputFile - 1).data(1001)) + '"')

		self.encodeProgressLabel.setText('Merging files.')

		print(mkvMergeCmd)

		MI.Close()
		now = datetime.datetime.now()
		self.mediaInfoText.append('[' + str(now.date()) + ' ' + 
			str(now.hour) + ':' + str(now.minute) + ':' + str(now.second) + 
			']  Merging Files...')

		self.mkvMergeProcess.finished.connect(self.startCRCProcess)

		print("Starting merge process")
		self.mkvMergeProcess.start(mkvMergeCmd)
		self.currentProcess = psutil.Process(self.mkvMergeProcess.processId())

	def startCRCProcess(self):
		print("In crc process")
		if self.halt:
			return -1

		self.mkvMergeProcess.close()
		self.mkvMergeProcess = QProcess()
		self.pauseEncodeButton.setVisible(False)
		self.stopEncodeButton.setVisible(False)

		self.encodeProgressLabel.setText('Generating CRC...')

		now = datetime.datetime.now()
		self.mediaInfoText.append('[' + str(now.date()) + ' ' + 
			str(now.hour) + ':' + str(now.minute) + ':' + str(now.second) + 
			']  Generating CRC...')

		print("Starting crc process")
		prev = 0
		for eachLine in open(self.encodedFile, "rb"):
			prev = zlib.crc32(eachLine, prev)
			QCoreApplication.processEvents()

		crc = "%X"%(prev & 0xFFFFFFFF)
		print(crc)
		os.rename(self.encodedFile, self.encodedFile[0:-13] + '[' + crc + ']' +
			'.mkv')
		self.pauseEncodeButton.setVisible(True)
		self.stopEncodeButton.setVisible(True)
		self.startNextEncode()

	def startNextEncode(self):
		self.process.close()
		self.audioStreamProcess.close()
		self.ffmpegEncodeProcess.close()
		self.neroAacEncodeProcess.close()
		self.mkvMergeProcess.close()

		now = datetime.datetime.now()
		if not self.processQueue.empty():
			files = glob.glob(os.path.normpath('./temp/*'))
			for f in files:
				os.remove(f)
			
			self.curInputFile += 1
			self.mediaInfoText.append('')
			self.mediaInfoText.append('[' + str(now.date()) + ' ' + 
				str(now.hour) + ':' + str(now.minute) + ':' + str(now.second) + 
				']  Encoding file ' + str(self.curInputFile) + '/' + 
				str(self.totalInputFiles) + '  -  ' + 
				self.fileList.item(self.curInputFile - 1).text())

			if not os.path.isfile(os.path.normpath(
				self.fileList.item(self.curInputFile - 1).data(1001))):
				self.mediaInfoText.append('[' + str(now.date()) + ' ' + 
				str(now.hour) + ':' + str(now.minute) + ':' + str(now.second) + 
				']  Error - file not found: ' + 
				self.fileList.item(self.curInputFile - 1).data(1001))
				self.processQueue.get()
				self.startNextEncode()
			else:
				self.process = QProcess()
				self.process.finished.connect(self.finishedCurrentVideoEncode)
				self.process.readyReadStandardError.connect(self.progressUpdate)

				self.audioStreamProcess = QProcess()
				self.ffmpegEncodeProcess = QProcess()
				self.neroAacEncodeProcess = QProcess()
				self.mkvMergeProcess = QProcess()

				self.process.start(self.processQueue.get())
				self.currentProcess = psutil.Process(
					self.process.processId())
		else:
			self.mediaInfoText.append('\n[' + str(now.date()) + ' ' + 
				str(now.hour) + ':' + str(now.minute) + ':' + str(now.second) + 
				']  Encoding Complete')

			self.finishEncode()

	def finishEncode(self, halt = False):
		print("finished encode")
		files = glob.glob(os.path.normpath('./temp/*'))
		for f in files:
			os.remove(f)

		self.process.close()
		self.audioStreamProcess.close()
		self.ffmpegEncodeProcess.close()
		self.neroAacEncodeProcess.close()
		self.mkvMergeProcess.close()

		self.fileList.setAcceptDrops(True)
		self.fileList.setDragEnabled(True)
		self.fileList.clicked.connect(self.displayMediaInfo)

		self.addFileButton.setEnabled(True)
		self.removeFileButton.setEnabled(True)
		self.removeAllButton.setEnabled(True)
		self.settingsButton.setEnabled(True)
		self.saveOutputButton.setEnabled(True)
		self.outputLineEdit.setReadOnly(False)

		self.profileComboBox.setVisible(True)
		self.profileLineEdit.setVisible(False)

		self.pauseEncodeButton.setVisible(False)
		self.resumeEncodeButton.setVisible(False)
		self.stopEncodeButton.setVisible(False)

		self.encodeProgressLabel.setVisible(False)
		self.startEncodeButton.setVisible(True)

		config = configparser.ConfigParser()
		config.read(os.path.normpath('./data/options.ini'))

		if config.getboolean('Main','Shutdown') and not halt:
			subprocess.call(["shutdown", "-f", "-s", "-t", "60"])

	def updateMediaInfoGroupBox(self):
		self.mediaInfoGroupBox.setTitle('MediaInfo')


	"""
	Kill override for Encoding Process
	"""
	def pauseEncode(self):
		self.currentProcess.suspend()

		now = datetime.datetime.now()
		self.mediaInfoText.append('[' + str(now.date()) + ' ' + 
			str(now.hour) + ':' + str(now.minute) + ':' + str(now.second) + 
			']  Process Paused ')

		self.resumeEncodeButton.setVisible(True)
		self.pauseEncodeButton.setVisible(False)

	def resumeEncode(self):
		self.currentProcess.resume()
		self.resumeEncodeButton.setVisible(False)
		self.pauseEncodeButton.setVisible(True)

		now = datetime.datetime.now()
		self.mediaInfoText.append('[' + str(now.date()) + ' ' + 
			str(now.hour) + ':' + str(now.minute) + ':' + str(now.second) + 
			']  Process Resumed ')

	def stopEncode(self):
		exitDialog = QMessageBox(self)
		exitDialog.setWindowTitle('Confirm Rending')

		exitDialog.setText(
			'Are you sure you want to halt the encoding process?\n' + 
			'Unfinished encodes will be cast into Emptiness.')

		exitDialog.setStandardButtons(
			QMessageBox.Yes | QMessageBox.No)
		exitDialog.setDefaultButton(QMessageBox.No)

		if (exitDialog.exec_() == QMessageBox.No):
			return -1

		now = datetime.datetime.now()
		self.mediaInfoText.append('[' + str(now.date()) + ' ' + 
			str(now.hour) + ':' + str(now.minute) + ':' + str(now.second) + 
			']  Process Stopped ')

		while not self.processQueue.empty():
			self.processQueue.get()

		self.halt = True

		self.process.close()
		self.audioStreamProcess.close()
		self.ffmpegEncodeProcess.close()
		self.neroAacEncodeProcess.close()
		self.mkvMergeProcess.close()

		self.finishEncode(True)

	"""
	Main menu functions
	"""
	def center(self):
		winGeo = self.frameGeometry()
		centerPoint = QDesktopWidget().availableGeometry().center()
		winGeo.moveCenter(centerPoint)
		self.move(winGeo.topLeft())

	def findProfiles(self):
		self.profileComboBox.clear()
		if not os.path.exists(os.path.normpath('./profiles')):
			os.makedirs(os.path.normpath('./profiles'))

		for profile in os.listdir('./profiles'):
			if profile.endswith('.ini'):
				self.profileComboBox.addItem(profile[:-4])

		if self.profileComboBox.count() == 0:
			SettingsDialog.defaultConfig(self, 'Default')
			self.profileComboBox.addItem('Default')

	def refreshProfileList(self, selected = None):
		self.findProfiles()
		self.profileComboBox.setCurrentIndex(
			self.profileComboBox.findText(selected))

	def closeEvent(self, event):
		if (self.process.state() == QProcess.NotRunning and 
			self.audioStreamProcess.state() == QProcess.NotRunning and
			self.audioStreamProcess.state() == QProcess.NotRunning and
			self.ffmpegEncodeProcess.state() == QProcess.NotRunning and
			self.neroAacEncodeProcess.state() == QProcess.NotRunning and
			self.mkvMergeProcess.state() == QProcess.NotRunning):

			self.updateOptions()

			event.accept()
		else:
			# exitDialog = QMessageBox(self)
			# exitDialog.setWindowTitle('Confirm Exit')

			# exitDialog.setText('Are you sure you want to exit?\n' + 
			# 	'There are jobs in progress.')

			# exitDialog.setStandardButtons(
			# 	QMessageBox.Yes | QMessageBox.No)
			# exitDialog.setDefaultButton(QMessageBox.No)

			# if (exitDialog.exec_() == QMessageBox.Yes):
				

			if (self.stopEncode() != -1):

				self.updateOptions()
				event.accept()
			else:
				event.ignore()

	def updateOptions(self):
		config = configparser.ConfigParser()
		config.read(os.path.normpath('./data/options.ini'))

		if config.getboolean('Main','RememberProfile'):
			config['Main']['PreviousProfile'] = (
				self.profileComboBox.currentText())

		if config.getboolean('Main','RememberOutput'):
			config['Main']['PreviousOutput'] = self.outputLineEdit.text()

		with open('./data/options.ini', 'w') as configfile:
			config.write(configfile)

	def layoutGrid(self):
		grid = QGridLayout()
		grid.setSpacing(10)

		fileListGroupBox = QGroupBox('Input Files')
		grid1 = QGridLayout()

		grid1.addWidget(self.fileList, 1, 0, 24, 45)
		grid1.addWidget(self.addFileButton, 2, 45, 2, 5)
		grid1.addWidget(self.removeFileButton, 4, 45, 2, 5)
		grid1.addWidget(self.removeAllButton, 6, 45, 2, 5)
		grid1.addWidget(self.optionsButton, 21, 45, 2, 5)

		fileListGroupBox.setLayout(grid1)
		grid.addWidget(fileListGroupBox, 0, 0, 23, 50)

		self.mediaInfoGroupBox = QGroupBox()
		self.mediaInfoGroupBox.setAlignment(Qt.AlignLeft)
		self.mediaInfoGroupBox.setTitle('MediaInfo')

		grid2 = QGridLayout()
		grid2.addWidget(self.mediaInfoText, 0, 0)

		self.mediaInfoGroupBox.setLayout(grid2)
		grid.addWidget(self.mediaInfoGroupBox, 23, 0, 25, 50)

		grid.addWidget(self.ProfileLabel, 48, 0, 1, 4)
		grid.addWidget(self.profileComboBox, 48, 4, 1, 40)
		grid.addWidget(self.settingsButton, 48, 44, 1, 6)

		grid.addWidget(self.profileLineEdit, 48, 4, 1, 40)

		grid.addWidget(self.outputLabel, 49, 0, 1, 4)
		grid.addWidget(self.outputLineEdit, 49, 4, 1, 40)
		grid.addWidget(self.saveOutputButton, 49, 44, 1, 6)

		grid.addWidget(self.encodeProgressLabel, 50, 0, 1, 46)
		grid.addWidget(self.startEncodeButton, 50, 0, 1, 50, Qt.AlignCenter)

		encodeGroupBox = QGroupBox()
		encodeGroupBox.setFlat(True)
		encodeGroupBox.setStyleSheet('border: none;margin-top: 0ex')
		grid3 = QGridLayout()
		grid3.setSpacing(1)
		grid3.setContentsMargins(0, 0, 0, 0)

		grid3.addWidget(self.pauseEncodeButton, 0, 0)
		grid3.addWidget(self.resumeEncodeButton, 0, 0)
		grid3.addWidget(self.stopEncodeButton, 0, 1)
		encodeGroupBox.setLayout(grid3)

		grid.addWidget(encodeGroupBox, 50, 46, 1, 4)

		self.setLayout(grid)


if __name__ == '__main__':
	app = QApplication(sys.argv)
	app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

	win = MainWindow()
	sys.exit(app.exec_())