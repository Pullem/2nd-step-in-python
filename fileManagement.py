import ctypes

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QFileDialog, QPushButton, QListWidgetItem, QAbstractItemView, QTextBrowser)

from myListWidget import MyListWidget

ctypes.WinDLL('./tools/MediaInfo.dll')
from MediaInfoDLL3 import *


class FileManagement:
	def setFileAdd(self):
		self.fileList = MyListWidget(self)
		self.fileList.resize(500, 200)
		self.fileList.setSelectionMode(QAbstractItemView.ExtendedSelection)
		self.fileList.setAcceptDrops(True)
		self.fileList.setDragEnabled(True)
		self.fileList.setDragDropMode(QAbstractItemView.InternalMove)
		self.fileList.setDefaultDropAction(Qt.MoveAction)
		self.fileList.setDropIndicatorShown(True)
		self.fileList.setSelectionRectVisible(False)

		self.fileList.model().rowsInserted.connect(self.itemsAdded)
		self.fileList.clicked.connect(self.displayMediaInfo)

		self.addFileButton = QPushButton('Add', self)
		self.addFileButton.clicked.connect(self.addFileDialog)

	def addFileDialog(self):
		files = QFileDialog.getOpenFileNames(self, 'Select Files', '/',
											 filter='Videos (*.webm *.mkv *.flv *.vob *.ogv *.ogg *.drc *.mng *.avi '
													+ '*.mov *.qt *.wmv *.yuv *.rm *.rmvb *.asf *.mp4 *.m4p '
													+ '*.m4v *.mpg *.mp2 *.mpeg *.mpe *mpv *.m2v *.svi *.3gp '
													+ '*.3g2 *.mxf *.roq *.nsv)')

		print(files[0])
		for item in files[0]:
			itemToAdd = QListWidgetItem()
			itemToAdd.setText(os.path.basename(item))
			itemToAdd.setData(1001, item)
			self.fileList.addItem(itemToAdd)

		# print(os.path.basename(item))
		# print(itemToAdd.data(1001))

		if self.fileList.count() > 0:
			self.removeFileButton.setEnabled(True)
			self.removeAllButton.setEnabled(True)

	def setFileRemove(self):
		self.removeFileButton = QPushButton('Remove', self)
		self.removeFileButton.clicked.connect(self.removeFiles)
		self.removeFileButton.setEnabled(False)

		self.removeAllButton = QPushButton('Remove All', self)
		self.removeAllButton.clicked.connect(self.removeAll)
		self.removeAllButton.setEnabled(False)

	def itemsAdded(self):
		if self.fileList.count() > 0:
			self.removeFileButton.setEnabled(True)
			self.removeAllButton.setEnabled(True)

	def removeFiles(self):
		for item in self.fileList.selectedItems():
			self.fileList.takeItem(self.fileList.row(item))

		self.mediaInfoText.clear()
		if self.fileList.count() == 0:
			self.removeFileButton.setEnabled(False)
			self.removeAllButton.setEnabled(False)

	def removeAll(self):
		self.numFiles = 0
		self.fileList.clear()
		self.mediaInfoText.clear()

		self.removeFileButton.setEnabled(False)
		self.removeAllButton.setEnabled(False)

	def setMediaInfoText(self):
		self.mediaInfoText = QTextBrowser(self)
		self.mediaInfoText.setReadOnly(True)
		self.mediaInfoText.setContextMenuPolicy(Qt.NoContextMenu)
		self.mediaInfoText.setPlaceholderText(
			'Select an Input File to View its MediaInfo')

	def displayMediaInfo(self):
		print("\n<Selected File>")
		print(self.fileList.currentItem().text())
		print(self.fileList.currentItem().data(1001))

		MI = MediaInfo()
		MI.Open(self.fileList.currentItem().data(1001))

		self.mediaInfoText.setPlainText(MI.Inform())
		MI.Close()
