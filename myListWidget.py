import os.path

from PyQt5.QtWidgets import (QListWidget, QListWidgetItem, QAbstractItemView,
	QMessageBox, QApplication)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt

class MyListWidget(QListWidget):
	def __init__(self, parent):
		super(MyListWidget, self).__init__(parent)
		# self.setAcceptDrops(True)
		# self.setDragDropMode(QAbstractItemView.InternalMove)

	def dragEnterEvent(self, event):
		QApplication.setActiveWindow(self)
		if event.mimeData().hasUrls():
			event.acceptProposedAction()
		else:
			super(MyListWidget, self).dragEnterEvent(event)

	def dragMoveEvent(self, event):
		super(MyListWidget, self).dragMoveEvent(event)

	def dropEvent(self, event):
		if event.mimeData().hasUrls():
			for url in event.mimeData().urls():
				if url.toLocalFile().lower().endswith(
				('.webm', '.mkv', '.flv', '.vob', '.ogv', '.ogg', '.drc', 
				'.mng', '.avi ', ',.mov', '.qt', '.wmv', '.yuv', '.rm', 
				'.rmvb', '.asf', '.mp4', '.m4p ', ',.m4v', '.mpg', '.mp2', 
				'.mpeg', '.mpe', 'mpv', '.m2v', '.svi', '.3gp ',
				',.3g2', '.mxf', '.roq', '.nsv')):
					itemToAdd = QListWidgetItem()
					itemToAdd.setText(os.path.basename(url.toLocalFile()))
					itemToAdd.setData(1001, url.toLocalFile())
					self.addItem(itemToAdd)

					event.acceptProposedAction()
				else:
					invalidFormatDialog = QMessageBox(self)
					invalidFormatDialog.setWindowIcon(QIcon(os.path.normpath(
						'./Icons/transparent.png')))
					invalidFormatDialog.setWindowTitle('Error')
					invalidFormatDialog.setText(
						'Invalid file format. \nPlease import video files only.')
					invalidFormatDialog.setIconPixmap(QPixmap(os.path.normpath(
						'./Icons/warning.png')))
					invalidFormatDialog.exec_()

		super(MyListWidget,self).dropEvent(event)