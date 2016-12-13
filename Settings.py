import os, sys, platform, configparser, multiprocessing
import qdarkstyle

from PyQt5.QtWidgets import (QTabWidget, QWidget, QGridLayout, QDialog, 
	QInputDialog, QMessageBox, QGroupBox, QLabel, QComboBox, QPushButton, 
	QSpinBox, QDoubleSpinBox, QSlider, QCheckBox, QTextEdit, QTextBrowser, 
	QSizePolicy)
from PyQt5.QtGui import QIcon, QTextOption
from PyQt5.QtCore import Qt, QSize

class SettingsDialog:
	def __init__(self, win, selected):
		super().__init__()
		print("initializing Settings Dialog")

		self.mainWindow = win
		self.initUI(selected)
		self.disableDeleteButton()

		self.setCommonTab()
		self.setFrameTypeTab()
		self.setRateControlTab()
		self.setAdvancedTab()
		self.setMiscTab()

		self.layoutMainGrid()
		self.layoutCommonGrid()
		self.layoutFrameTypeGrid()
		self.layoutRateControlGrid()
		self.layoutAdvancedGrid()
		self.layoutMiscGrid()

		self.loadProfileSettings()

	def initUI(self, selected):
		self.tabs = QTabWidget()

		self.tab1 = QWidget()
		self.tab2 = QWidget()
		self.tab3 = QWidget()
		self.tab4 = QWidget()
		self.tab5 = QWidget()

		self.tabs.addTab(self.tab1, ' Common ')
		self.tabs.addTab(self.tab2, ' Frame-Type ')
		self.tabs.addTab(self.tab3, ' Rate Control ')
		self.tabs.addTab(self.tab4, ' Advanced ')
		self.tabs.addTab(self.tab5, ' Misc ')

		self.tabs.currentChanged.connect(self.tabChanged)

		self.profileComboBox = QComboBox()
		self.findProfiles()
		self.profileComboBox.setCurrentIndex(selected)
		self.profileComboBox.currentIndexChanged.connect(
			self.loadProfileSettings)

		self.profileLabel = QLabel('Profile')
		self.profileLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

		self.renameProfileButton = QPushButton()
		self.renameProfileButton.setIcon(QIcon(os.path.normpath(
			'./Icons/rename.png')))
		self.renameProfileButton.setIconSize(QSize(20, 20))
		self.renameProfileButton.setStyleSheet(
			'QPushButton {padding: 0px;border-radius: 2px}'
			'QToolTip {padding: -1px; opacity: 255}')
		self.renameProfileButton.setToolTip('Rename')
		self.renameProfileButton.clicked.connect(self.renameProfile)

		self.addProfileButton = QPushButton()
		self.addProfileButton.setIcon(QIcon(os.path.normpath(
			'./Icons/add.png')))
		self.addProfileButton.setIconSize(QSize(23, 23))
		self.addProfileButton.setStyleSheet(
			'QPushButton {padding: 0px;border-radius: 2px}'
			'QToolTip {padding: -1px; opacity: 255}')
		self.addProfileButton.setToolTip('New Profile')
		self.addProfileButton.clicked.connect(self.addProfile)

		self.deleteProfileButton = QPushButton()
		self.deleteProfileButton.setIcon(QIcon(os.path.normpath(
			'./Icons/delete.png')))
		self.deleteProfileButton.setIconSize(QSize(23, 23))
		self.deleteProfileButton.setStyleSheet(
			'QPushButton {padding: 0px;border-radius: 2px}'
			'QToolTip {padding: -1px; opacity: 255}')
		self.deleteProfileButton.setToolTip('Delete Profile')
		self.deleteProfileButton.clicked.connect(self.deleteProfile)

		self.saveProfileButton = QPushButton()
		self.saveProfileButton.setIcon(QIcon(os.path.normpath(
			'./Icons/save.png')))
		self.saveProfileButton.setIconSize(QSize(23, 23))
		self.saveProfileButton.setStyleSheet(
			'QPushButton {padding: 0px;border-radius: 2px}'
			'QToolTip {padding: -1px; opacity: 255}')
		self.saveProfileButton.setToolTip('Save Changes')
		self.saveProfileButton.clicked.connect(self.saveProfile)

		self.restoreProfileButton = QPushButton()
		self.restoreProfileButton.setIcon(QIcon(os.path.normpath(
			'./Icons/restore.png')))
		self.restoreProfileButton.setIconSize(QSize(23, 23))
		self.restoreProfileButton.setStyleSheet(
			'QPushButton {padding: 0px;border-radius: 2px}'
			'QToolTip {padding: -1px; opacity: 255}')
		self.restoreProfileButton.setToolTip('Restore Last Saved')
		self.restoreProfileButton.clicked.connect(self.loadProfileSettings)

	def tabChanged(self):
		if ((self.quickSettingsCheckBox.isChecked() 
			and self.tabs.currentIndex() == 4) or 
			(not self.quickSettingsCheckBox.isChecked() 
			and self.tabs.currentIndex() == 1)):
			profileName = self.profileComboBox.currentText()

			config = configparser.ConfigParser()
			config.read(os.path.normpath('./profiles/' + profileName + '.ini'))

			self.updateCmdLineOutput(config)

	def getSelectedProfile(self):
		return self.profileComboBox.currentText()

	def disableDeleteButton(self):
		print("inital check to disable delete profile button")

		if self.profileComboBox.count() <= 1:
			self.deleteProfileButton.setEnabled(False)
			print("delete profile button disabled")


	"""
	Creating the Common Tab Widgets
	"""
	def setCommonTab(self):
		print("Setting Common Tab")

		self.encodingModeComboBox = QComboBox()
		self.encodingModeComboBox.addItem('Constant Quantizer')
		self.encodingModeComboBox.addItem('Constant Ratefactor')
		self.encodingModeComboBox.setToolTip("Encoding Mode\n\
Sets the encoding mode.\n\n\
Default: Constant Ratefactor\n\
Recommended: Constant Ratefactor")
		self.encodingModeComboBox.setStyleSheet(
			'QToolTip {padding: -1px; opacity: 255}')
		self.encodingModeComboBox.currentIndexChanged.connect(
			self.encodingModeChanged)

		self.encodingModeValueLabel = QLabel()
		self.encodingModeValueDoubleSpinBox = QDoubleSpinBox()

		self.tuningComboBox = QComboBox()
		self.tuningComboBox.addItem('None')
		self.tuningComboBox.addItem('Film')
		self.tuningComboBox.addItem('Animation')
		self.tuningComboBox.addItem('Grain')
		self.tuningComboBox.setToolTip("--tune <string>\n\
Sets x264 parameters to optimize for the input source.\n\
These 'optimized' settings are decided by the developers\n\
and are not necessarily the best.\n\n\
Values:\n\
	-film: Intended for high-bitrate/high quality content.\n\
	-animation: Intended for animated content with high deblocking.\n\
	-grain: Should be used for material that is already grainy.\n\
		Retains more grains by using a higher aq-strength.\n\
Default: not set")
		self.tuningComboBox.setStyleSheet('QToolTip {padding: -1px; opacity: 255}')

		self.presetLabel = QLabel()
		self.presetSlider = QSlider(Qt.Horizontal)
		self.presetSlider.setMinimum(0)
		self.presetSlider.setMaximum(9)
		self.presetSlider.setPageStep(1)
		self.presetSlider.setSingleStep(1)
		self.presetSlider.setInvertedControls(True)
		self.presetSlider.valueChanged.connect(self.presetValueChanged)
		self.presetSlider.setToolTip("--preset <string>\n\
Sets x264 parameters to balance compression efficiency with encoding speed.\n\
Should generally be set to a slower value. Placebo should be avoided as it gives a\n\
negligible increase in compression efficiency for a much slower encoding speed.\n\n\
Values: ultrafast, superfast, veryfast, faster, fast, medium, slow, slower,\n\
	veryslow, placebo\n\
Default: medium\n\
Recommended: slow, veryslow")
		self.presetSlider.setStyleSheet(
			'QToolTip {padding: -1px; opacity: 255}')

		self.AVCprofileComboBox = QComboBox()
		self.AVCprofileComboBox.addItem('Baseline')
		self.AVCprofileComboBox.addItem('Main')
		self.AVCprofileComboBox.addItem('High')
		self.AVCprofileComboBox.setToolTip("--profile <string>\n\
Encoding Profiles representing a sub-set of the encoding parameters\n\
to target specific decoders. Enabled for 8-bit only.\n\n\
Values:\n\
	-baseline: Primarily for lower-cost applications with limited computing resources.\n\
	-main: Originally intended as the mainstream profile, now replaced by the High profile.\n\
	-high: Primary profile for broadcast and storage. Adopted by HD DVD and Blu-ray.\n\n\
Default: High\n\
Recommended: High")
		self.AVCprofileComboBox.setStyleSheet('QToolTip {padding: -1px; opacity: 255}')

		self.levelComboBox = QComboBox()
		self.levelComboBox.addItem('Auto-detect')
		self.levelComboBox.addItem('Level 1')
		self.levelComboBox.addItem('Level 1b')
		self.levelComboBox.addItem('Level 1.1')
		self.levelComboBox.addItem('Level 1.2')
		self.levelComboBox.addItem('Level 1.3')
		self.levelComboBox.addItem('Level 2')
		self.levelComboBox.addItem('Level 2.1')
		self.levelComboBox.addItem('Level 2.2')
		self.levelComboBox.addItem('Level 3')
		self.levelComboBox.addItem('Level 3.1')
		self.levelComboBox.addItem('Level 3.2')
		self.levelComboBox.addItem('Level 4')
		self.levelComboBox.addItem('Level 4.1')
		self.levelComboBox.addItem('Level 4.2')
		self.levelComboBox.addItem('Level 5')
		self.levelComboBox.addItem('Level 5.1')
		self.levelComboBox.addItem('Level 5.2')
		self.levelComboBox.setToolTip("--level <string>\n\
Sets the level flag in the output (as defined by Annex A of the H.264 standard).\n\
If not set, x264 will attempt to auto-detect the level and may not be accurate.\n\
Level 4.1 is the current Blu-ray/HD DVD standard and is supported by most devices.\n\n\
Values: 1, 1b, 1.1, 1.2, 1.3, 2, 2.1, 2.2, 3, 3.1, 3.2, 4, 4.1, 4.2, 5, 5.1, 5.2\n\
Default: not set (auto-detect)\n\
Recommended: 4.1")
		self.levelComboBox.setStyleSheet('QToolTip {padding: -1px; opacity: 255}')

		self.bitDepthCheckBox = QCheckBox('Enable 10-Bit Encoding')
		self.bitDepthCheckBox.stateChanged.connect(self.bit10StateChanged)
		self.bitDepthCheckBox.setToolTip("10-Bit Depth\n\
10-bit depth encoding offers a better compression efficiency\n\
(better quality at the same bitrates) but is slower to encode/decode.\n\n\
Default: disabled\n\
Recommended: enabled")
		self.bitDepthCheckBox.setStyleSheet('QToolTip {padding: -1px; opacity: 255}')

		self.quickSettingsCheckBox = QCheckBox(
			'Overwrite Preset/Tune Settings')
		self.quickSettingsCheckBox.stateChanged.connect(
			self.quickSettingsChanged)
		self.quickSettingsCheckBox.setToolTip("More Settings!\n\
Reveals more x264 settings that can be modified.\n\
Don't worry, there are tooltips for each setting!")
		self.quickSettingsCheckBox.setStyleSheet('QToolTip {padding: -1px; opacity: 255}')


	def encodingModeChanged(self):
		if self.encodingModeComboBox.currentText() == 'Constant Quantizer':
			self.encodingModeValueLabel.setText('Quantizer')

			self.encodingModeValueDoubleSpinBox.setMinimum(0)
			self.encodingModeValueDoubleSpinBox.setMaximum(81)
			self.encodingModeValueDoubleSpinBox.setSingleStep(1)
			self.encodingModeValueDoubleSpinBox.setDecimals(0)
			self.encodingModeValueDoubleSpinBox.setToolTip(
"--qp <integer>\n\
Encodes the video in Constant Quantizer (CQ) mode.\n\
The value specifies the Pframe quantizer.\n\
The quantizer used for I- and B- frames are derived from –ipratio and –pbratio.\n\n\
Values: 0-81 (0=lossless)\n\
Default: not set\n\
Recommended: --crf")
			self.encodingModeValueDoubleSpinBox.setStyleSheet(
				'QToolTip {padding: -1px; opacity: 255}')

		elif self.encodingModeComboBox.currentText() == 'Constant Ratefactor':
			self.encodingModeValueLabel.setText('Quality')

			self.encodingModeValueDoubleSpinBox.setMinimum(-12)
			self.encodingModeValueDoubleSpinBox.setMaximum(51)
			self.encodingModeValueDoubleSpinBox.setSingleStep(0.1)
			self.encodingModeValueDoubleSpinBox.setDecimals(1)
			self.encodingModeValueDoubleSpinBox.setToolTip(
"--crf <float>\n\
Constant Ratefactor, is a type of rate control in which ’quality’ is targeted.\n\
The value specifies the quantizer. The idea of CRF is to give the same or higher\n\
perceptual quality in a smaller size. This is achieved by using less bitrate for \n\
high motion frames and redistribute these bits for still frames. The reason behind\n\
this is that high motion frames are deemed less important as a decrease in quality\n\
is difficult to notice while details in a still frame are more noticeable and would\n\
require a significantly higher bitrate to achieve a good perceptual quality.\n\n\
Values: -12-51 (-12=lossless | 18=high | 23=average | 28+=low)\n\
Default: 23.0\n\
Recommended: 17.0-21.0")
			self.encodingModeValueDoubleSpinBox.setStyleSheet(
				'QToolTip {padding: -1px; opacity: 255}')


	def presetValueChanged(self):
		if self.presetSlider.value() == 0:
			self.presetLabel.setText('Ultra Fast')
		elif self.presetSlider.value() == 1:
			self.presetLabel.setText('Super Fast')
		elif self.presetSlider.value() == 2:
			self.presetLabel.setText('Very Fast')
		elif self.presetSlider.value() == 3:
			self.presetLabel.setText('Faster')
		elif self.presetSlider.value() == 4:
			self.presetLabel.setText('Fast')
		elif self.presetSlider.value() == 5:
			self.presetLabel.setText('Medium')
		elif self.presetSlider.value() == 6:
			self.presetLabel.setText('Slow')
		elif self.presetSlider.value() == 7:
			self.presetLabel.setText('Slower')
		elif self.presetSlider.value() == 8:
			self.presetLabel.setText('Very Slow')
		elif self.presetSlider.value() == 9:
			self.presetLabel.setText('Placebo')

	def bit10StateChanged(self):
		if self.bitDepthCheckBox.isChecked():
			self.AVCprofileGroup.setEnabled(False)
		else:
			self.AVCprofileGroup.setEnabled(True)

	def quickSettingsChanged(self):
		if self.quickSettingsCheckBox.isChecked():
			self.tabs.removeTab(4)
			self.tabs.addTab(self.tab2, ' Frame-Type ')
			self.tabs.addTab(self.tab3, ' Rate Control ')
			self.tabs.addTab(self.tab4, ' Advanced ')
			self.tabs.addTab(self.tab5, ' Misc ')
		else:
			self.tabs.removeTab(1)
			self.tabs.removeTab(1)
			self.tabs.removeTab(1)

	"""
	Creating the Frame-type Tab Widgets
	"""
	def setFrameTypeTab(self):
		print('Setting Frame-type Tab')

		self.deblockingCheckBox = QCheckBox('Deblocking')
		self.deblockingCheckBox.stateChanged.connect(
			self.deblockingStateChanged)
		self.deblockingCheckBox.setToolTip(
"--no-deblock (to disable)\n\
One of H.264 main features that controls the amount of blocking artifacts\n\
from motion estimation with the tradeoff of detail. This requires a small\n\
amount of decoding CPU but can significantly increase quality.\n\n\
Default: enabled\n\
Recommended: enabled")
		self.deblockingCheckBox.setStyleSheet(
			'QToolTip {padding: -1px; opacity: 255}')

		self.deblockingStrLabel = QLabel('Deblocking Strength')
		self.deblockingStrSpinBox = QSpinBox()
		self.deblockingStrSpinBox.setMinimum(-3)
		self.deblockingStrSpinBox.setMaximum(3)
		self.deblockingStrSpinBox.setToolTip(
"--deblock <integer>:<integer>\n\
The first value is called deblocking strength (alpha deblocking).\n\
Alpha deblocking affects the total amount of deblocking applied on the picture.\n\
A higher alpha value increases the amount of deblocking but destroys more detail.\n\n\
Default: 0\n\
Recommended: -1 (animation)")
		self.deblockingStrSpinBox.setStyleSheet(
			'QToolTip {padding: -1px; opacity: 255}')

		self.deblockingThresholdLabel = QLabel('Deblocking Threshold')
		self.deblockingThresholdSpinBox = QSpinBox()
		self.deblockingThresholdSpinBox.setMinimum(-3)
		self.deblockingThresholdSpinBox.setMaximum(3)
		self.deblockingThresholdSpinBox.setToolTip(
"--deblock <integer>:<integer>\n\
The second value is called deblocking threshold (beta deblocking).\n\
Beta deblocking determines if something in a block is a detail when\n\
deblocking is applied to it. Lower beta values apply less deblocking\n\
to more flat blocks when details are present.\n\n\
Default: 0\n\
Recommended: -1 (animation)")
		self.deblockingThresholdSpinBox.setStyleSheet(
			'QToolTip {padding: -1px; opacity: 255}')

		self.cabacCheckBox = QCheckBox('CABAC')

		self.gopMaxSizeLabel = QLabel('Maximum GOP Size')
		self.gopMaxSizeSpinBox = QSpinBox()
		self.gopMaxSizeSpinBox.setMinimum(0)
		self.gopMaxSizeSpinBox.setMaximum(1000)
		self.gopMaxSizeSpinBox.setSingleStep(10)
		self.gopMaxSizeSpinBox.setToolTip(
"--keyint <integer>\n\
Sets the max interval between IDR-frames (keyframes or Group of pictures (GOP) length).\n\
This trades off seeking file seekability with compression efficiency. IDRframes are\n\
'delimiters' in the stream and are I-frames, meaning players can start decoding from the\n\
nearest I-frame instead from the beginning. Therefore they can be used as seek points in\n\
a video.\n\
When encoding Blu-ray, broadcast, live streaming or other similar videos,\n\
a significantly lower GOP length may be required.\n\n\
Default: 250\n\
Recommended: 250, --fps*10")
		self.gopMaxSizeSpinBox.setStyleSheet(
			'QToolTip {padding: -1px; opacity: 255}')

		self.gopMinSizeLabel = QLabel('Minimum GOP Size')
		self.gopMinSizeSpinBox = QSpinBox()
		self.gopMinSizeSpinBox.setMinimum(0)
		self.gopMinSizeSpinBox.setMaximum(100)
		self.gopMinSizeSpinBox.setToolTip(
"--min-keyint <integer>\n\
Sets the minimum GOP length, minimum distance between IDR-frames.\n\
Playback can only be started at an IDR-frame. Generally the minimum\n\
value should be the framerate of the video.\n\n\
Default: 0, auto (min(--keyint/10, --fps))\n\
Recommended: 0, auto")
		self.gopMinSizeSpinBox.setStyleSheet(
			'QToolTip {padding: -1px; opacity: 255}')

		self.bframeWeightCheckBox = QCheckBox(
			'Weighted Prediction for B-Frames')
		self.bframeWeightCheckBox.setToolTip(
"--no-weightb (to disable)\n\
Enables/disables weighted prediction for weightb. Enabling weightb produces B-Frames\n\
that are more accurate by allowing non-symmetric weighting of reference frames. This\n\
feature has a negligible impact on speed. Since weighted B-frames generally improves\n\
visual quality, it is better to have it enabled.\n\n\
Default: enabled\n\
Recommended: enabled")
		self.bframeWeightCheckBox.setStyleSheet(
			'QToolTip {padding: -1px; opacity: 255}')

		self.bframeNumberLabel = QLabel('Maximum B-frames')
		self.bframeNumberSpinBox = QSpinBox()
		self.bframeNumberSpinBox.setMinimum(0)
		self.bframeNumberSpinBox.setMaximum(16)
		self.bframeNumberSpinBox.valueChanged.connect(self.bframeNumberChanged)
		self.bframeNumberSpinBox.setToolTip(
"--bframes <integer>\n\
Sets the maximum number of concurrent B-frames that can be used.\n\
The average quality is controlled by --pbratio.\n\n\
Default: 3\n\
Recommended: 8-16")
		self.bframeNumberSpinBox.setStyleSheet(
			'QToolTip {padding: -1px; opacity: 255}')

		self.bframeBiasLabel = QLabel('B-frame Bias')
		self.bframeBiasSpinBox = QSpinBox()
		self.bframeBiasSpinBox.setMinimum(-100)
		self.bframeBiasSpinBox.setMaximum(100)
		self.bframeBiasSpinBox.setSingleStep(5)
		self.bframeBiasSpinBox.setToolTip(
"--b-bias <integer>\n\
Controls the likelihood of B-frames being used over P-frames.\n\
Values larger than 0 increase the weighting towards B-frame,\n\
while values less than 0 do the reverse.\n\n\
Default: 0\n\
Recommended: 0")
		self.bframeBiasSpinBox.setStyleSheet(
			'QToolTip {padding: -1px; opacity: 255}')

		self.bframeAdaptiveLabel = QLabel('Adaptive B-frame')
		self.bframeAdaptiveComboBox = QComboBox()
		self.bframeAdaptiveComboBox.addItem('Disabled')
		self.bframeAdaptiveComboBox.addItem('Fast')
		self.bframeAdaptiveComboBox.addItem('Optimal')
		self.bframeAdaptiveComboBox.setToolTip(
"--b-adapt <integer>\n\
Sets the adaptive B-frame placement algorithm,\n\
deciding whether a P- or B-frame is placed.\n\n\
Values:\n\
	0: Disable. Always pick B-frames.\n\
	1: ’Fast’ algorithm, speed slightly increases\n\
	    with higher –b-frames setting (use --b-frames 16)\n\
	2: Primary profile for broadcast and storage.\n\
	    Adopted by HD DVD and Blu-ray.\n\
Default: 1\n\
Recommended: 2")
		self.bframeAdaptiveComboBox.setStyleSheet(
			'QToolTip {padding: -1px; opacity: 255}')

		self.bframePyramidLabel = QLabel('B-Pyramid')
		self.bframePyramidComboBox = QComboBox()
		self.bframePyramidComboBox.addItem('Disabled')
		self.bframePyramidComboBox.addItem('Strict')
		self.bframePyramidComboBox.addItem('Normal')
		self.bframePyramidComboBox.setToolTip(
"--b-pyramid <string>\n\
Allows B-frames to be used as references for other frames. B-frames references have\n\
a quantizer between I-frames and P-frames. This setting is generally beneficial but\n\
increases the Decoded Picture Buffer (DPB) size required for playback which may have\n\
compatibility issues. Quality increase is negligible and increases decoding complexity\n\
but also increases compression.\n\n\
Values:\n\
	-none: do not allow B-frames to be used as references.\n\
	-strict: allow one B-frame per minigop to be used as reference, Bluray standard.\n\
	-normal: allow many B-frames per minigop to be used as reference.\n\
Default: normal\n\
Recommended: normal, strict (if abiding by Blu-ray standards)")
		self.bframePyramidComboBox.setStyleSheet(
			'QToolTip {padding: -1px; opacity: 255}')

		self.frameEncodingRefLabel = QLabel('Maximum Reference Frames')
		self.frameEncodingRefSpinBox = QSpinBox()
		self.frameEncodingRefSpinBox.setMinimum(1)
		self.frameEncodingRefSpinBox.setMaximum(16)
		self.frameEncodingRefSpinBox.setToolTip(
"--ref <integer>\n\
Controls the size of the Decoded Picture Buffer (DPB). The value controls\n\
the number of previous frames each P-frame can use as references. A higher\n\
value increases the DPB, which means hardware playback devices usually have\n\
strict limits for the number of refs they can handle. If adhering to the\n\
H.264 spec, the max refs for 720p and 1080p are 9 and 4 respectively.\n\n\
Default: 3\n\
Recommended: 16 (animation)")
		self.frameEncodingRefSpinBox.setStyleSheet(
			'QToolTip {padding: -1px; opacity: 255}')

		self.frameEncodingSceneChangeLabel = QLabel('Scene Change Sensitivity')
		self.frameEncodingSceneChangeSpinBox = QSpinBox()
		self.frameEncodingSceneChangeSpinBox.setMinimum(0)
		self.frameEncodingSceneChangeSpinBox.setMaximum(100)
		self.frameEncodingSceneChangeSpinBox.setToolTip(
"--scenecut <integer>\n\
Sets the threshold for I/IDR frame placement (scene change detection). For every\n\
frame, x264 calculates a metric to estimate how different it is from the previous frame.\n\
If the value calculated is lower than the scenecut value, a ’scene-cut’ is detected. An\n\
I-frame is placed if it has been less than –min-keyint frames since the last IDR frame,\n\
otherwise an IDR frame is placed.\n\n\
Default: 40\n\
Recommended: 40")
		self.frameEncodingSceneChangeSpinBox.setStyleSheet(
			'QToolTip {padding: -1px; opacity: 255}')
		
	def deblockingStateChanged(self):
		if self.deblockingCheckBox.isChecked():
			self.deblockingStrLabel.setEnabled(True)
			self.deblockingThresholdLabel.setEnabled(True)
			self.deblockingStrSpinBox.setEnabled(True)
			self.deblockingThresholdSpinBox.setEnabled(True)
		else:
			self.deblockingStrLabel.setEnabled(False)
			self.deblockingThresholdLabel.setEnabled(False)
			self.deblockingStrSpinBox.setEnabled(False)
			self.deblockingThresholdSpinBox.setEnabled(False)

	def bframeNumberChanged(self):
		if self.bframeNumberSpinBox.value() == 0:
			self.bframeWeightCheckBox.setEnabled(False)
			self.bframeBiasLabel.setEnabled(False)
			self.bframeBiasSpinBox.setEnabled(False)
			self.bframeAdaptiveLabel.setEnabled(False)
			self.bframeAdaptiveComboBox.setEnabled(False)
			self.bframePyramidLabel.setEnabled(False)
			self.bframePyramidComboBox.setEnabled(False)
		else:
			self.bframeWeightCheckBox.setEnabled(True)
			self.bframeBiasLabel.setEnabled(True)
			self.bframeBiasSpinBox.setEnabled(True)
			self.bframeAdaptiveLabel.setEnabled(True)
			self.bframeAdaptiveComboBox.setEnabled(True)
			self.bframePyramidLabel.setEnabled(True)
			self.bframePyramidComboBox.setEnabled(True)



	"""
	Creating the Rate Control Widgets
	"""
	def setRateControlTab(self):
		print('Setting Rate Control Tab')

		self.qpMinLabel = QLabel('Min')
		self.qpMaxLabel = QLabel('Max')

		self.qpIFrameLabel = QLabel('I-frame')

		self.qpIMinSpinBox = QSpinBox()
		self.qpIMinSpinBox.setMinimum(0)
		self.qpIMinSpinBox.setMaximum(50)
		self.qpIMinSpinBox.setAlignment(Qt.AlignHCenter)
		self.qpIMinSpinBox.setToolTip(
"--qp-min <integer>[:<integer>:<integer>]\n\
Defines the minimum quantizer used. The lower the value, the closer\n\
the output is to the source. The first value is for I frames.\n\n\
Default: 0\n\
Recommended: 0")
		self.qpIMinSpinBox.setStyleSheet(
			'QToolTip {padding: -1px; opacity: 255}')

		self.qpIMaxSpinBox = QSpinBox()
		self.qpIMaxSpinBox.setMinimum(1)
		self.qpIMaxSpinBox.setMaximum(100)
		self.qpIMaxSpinBox.setAlignment(Qt.AlignHCenter)
		self.qpIMaxSpinBox.setToolTip(
"--qp-max <integer>[:<integer>:<integer>]\n\
Defines the maximum quantizer used. Users may want to set the value lower (30-40)\n\
but adjustments are not necessary. The first value is for I frames.\n\n\
Default: 81\n\
Recommended: 30-50")
		self.qpIMaxSpinBox.setStyleSheet(
			'QToolTip {padding: -1px; opacity: 255}')

		self.qpPFrameLabel = QLabel('P-frame')

		self.qpPMinSpinBox = QSpinBox()
		self.qpPMinSpinBox.setMinimum(0)
		self.qpPMinSpinBox.setMaximum(50)
		self.qpPMinSpinBox.setAlignment(Qt.AlignHCenter)
		self.qpPMinSpinBox.setToolTip(
"--qp-min <integer>[:<integer>:<integer>]\n\
Defines the minimum quantizer used. The lower the value, the closer\n\
the output is to the source. The second value is for P frames.\n\n\
Default: 0\n\
Recommended: 0")
		self.qpPMinSpinBox.setStyleSheet(
			'QToolTip {padding: -1px; opacity: 255}')

		self.qpPMaxSpinBox = QSpinBox()
		self.qpPMaxSpinBox.setMinimum(1)
		self.qpPMaxSpinBox.setMaximum(100)
		self.qpPMaxSpinBox.setAlignment(Qt.AlignHCenter)
		self.qpPMaxSpinBox.setToolTip(
"--qp-max <integer>[:<integer>:<integer>]\n\
Defines the maximum quantizer used. Users may want to set the value lower (30-40)\n\
but adjustments are not necessary. The second value is for P frames.\n\n\
Default: 81\n\
Recommended: 30-50")
		self.qpPMaxSpinBox.setStyleSheet(
			'QToolTip {padding: -1px; opacity: 255}')

		self.qpBFrameLabel = QLabel('B-frame')

		self.qpBMinSpinBox = QSpinBox()
		self.qpBMinSpinBox.setMinimum(0)
		self.qpBMinSpinBox.setMaximum(50)
		self.qpBMinSpinBox.setAlignment(Qt.AlignHCenter)
		self.qpBMinSpinBox.setToolTip(
"--qp-min <integer>[:<integer>:<integer>]\n\
Defines the minimum quantizer used. The lower the value, the closer\n\
the output is to the source. The third value is for B frames.\n\n\
Default: 0\n\
Recommended: 0")
		self.qpBMinSpinBox.setStyleSheet(
			'QToolTip {padding: -1px; opacity: 255}')

		self.qpBMaxSpinBox = QSpinBox()
		self.qpBMaxSpinBox.setMinimum(1)
		self.qpBMaxSpinBox.setMaximum(100)
		self.qpBMaxSpinBox.setAlignment(Qt.AlignHCenter)
		self.qpBMaxSpinBox.setToolTip(
"--qp-max <integer>[:<integer>:<integer>]\n\
Defines the maximum quantizer used. Users may want to set the value lower (30-40)\n\
but adjustments are not necessary. The second value is for B frames.\n\n\
Default: 81\n\
Recommended: 30-50")
		self.qpBMaxSpinBox.setStyleSheet(
			'QToolTip {padding: -1px; opacity: 255}')

		self.qpStepLabel = QLabel('Max QP Step')
		self.qpStepSpinBox = QSpinBox()
		self.qpStepSpinBox.setMinimum(1)
		self.qpStepSpinBox.setMaximum(50)
		self.qpStepSpinBox.setToolTip(
"--qpstep <integer>\n\
Caps the maximum change in quantizer between two frames.\n\
This will reduce the amount of any large jump in quality of the output.\n\n\
Default: 4\n\
Recommended: 4")
		self.qpStepSpinBox.setStyleSheet(
			'QToolTip {padding: -1px; opacity: 255}')

		self.qCompLabel = QLabel('Quantizer Compression')
		self.qCompSpinBox = QDoubleSpinBox()
		self.qCompSpinBox.setMinimum(0.0)
		self.qCompSpinBox.setMaximum(1)
		self.qCompSpinBox.setDecimals(2)
		self.qCompSpinBox.setSingleStep(0.05)
		self.qCompSpinBox.setToolTip(
"--qpcomp <float>\n\
Quantizer curve compression factor. A value of 0.0 = Constant bitrate,\n\
1.0 = Constant Quantizer. Qcomp trades off the ratio of bits allocated\n\
to 'expensive' or highmotion vs 'cheap' low-motion frames. A qcomp of\n\
0.0 would make the quality of high-motion scenes look terrible while\n\
low-motion scenes would look great but with wasted bitrate. With a qcomp\n\
of 1.0, high-motion scenes would look great however a lot of bitrate is\n\
wasted on each frame as well since these scenes have a lot of changing frames.\n\n\
Values: 0.0-1.0\n\
Default: 0.60\n\
Recommended: 0.60")
		self.qCompSpinBox.setStyleSheet(
			'QToolTip {padding: -1px; opacity: 255}')

		self.qpRatioLabel = QLabel('Quantizer Ratio')
		self.qpIPRatioLabel = QLabel('I-frame:P-frame')
		self.qpIPRatioSpinBox = QDoubleSpinBox()
		self.qpIPRatioSpinBox.setMinimum(1.0)
		self.qpIPRatioSpinBox.setMaximum(10.0)
		self.qpIPRatioSpinBox.setDecimals(2)
		self.qpIPRatioSpinBox.setSingleStep(0.05)
		self.qpIPRatioSpinBox.setToolTip(
"--ipratio <float>\n\
Sets the target average increase in quality for I frames to P frames. A higher value\n\
would increase the quality of I frames but lower the quality of P and B frames.\n\n\
Default: 1.40\n\
Recommended: 1.40")
		self.qpIPRatioSpinBox.setStyleSheet(
			'QToolTip {padding: -1px; opacity: 255}')

		self.qpPBRatioLabel = QLabel('P-frame:B-frame')
		self.qpPBRatioSpinBox = QDoubleSpinBox()
		self.qpPBRatioSpinBox.setMinimum(1.0)
		self.qpPBRatioSpinBox.setMaximum(10.0)
		self.qpPBRatioSpinBox.setDecimals(2)
		self.qpPBRatioSpinBox.setSingleStep(0.05)
		self.qpPBRatioSpinBox.setToolTip(
"--pbratio <float>\n\
Sets the target average increase in quality for P frames to B frames. A higher\n\
value would increase the quality of P frames but lower the quality of B frames.\n\n\
Default: 1.30\n\
Recommended: 1.30")
		self.qpPBRatioSpinBox.setStyleSheet(
			'QToolTip {padding: -1px; opacity: 255}')

		self.aqModeLabel = QLabel('AQ Mode')
		self.aqModeComboBox = QComboBox()
		self.aqModeComboBox.addItem('Disabled')
		self.aqModeComboBox.addItem('Variance AQ')
		self.aqModeComboBox.addItem('Auto-variance AQ')
		self.aqModeComboBox.addItem('Auto-variance AQ mod1')
		self.aqModeComboBox.addItem('Auto-variance AQ mod2')
		self.aqModeComboBox.currentIndexChanged.connect(
			self.aqModeValueChanged)
		self.aqModeComboBox.setToolTip(
"--aq-mode <integer>\n\
Adaptive Quantization Mode is used to better distribute the available bits in the video.\n\n\
Values:\n\
	0: Do not use AQ.\n\
	1: Variance AQ which allows AQ to redistribute bits across video and within frames.\n\
	2: Auto-variance AQ which attempts to adapt strength per frame\n\
	    (experimental – tends to over reallocate bits)\n\
	3: Auto-variance AQ mod1, with bias towards dark scenes and grainy scenes.\n\
	    Recommended as grainy and dark scenes generally requires a higher\n\
	    bitrate to maintain quality.\n\
	4: Auto-variance AQ mod2 (experimental, improves algorithm of aq-mode of 2).\n\
Default: 1\n\
Recommended: 3")
		self.aqModeComboBox.setStyleSheet(
			'QToolTip {padding: -1px; opacity: 255}')

		self.aqStrengthLabel = QLabel('AQ Strength')
		self.aqStrengthSpinBox = QDoubleSpinBox()
		self.aqStrengthSpinBox.setDecimals(1)
		self.aqStrengthSpinBox.setMinimum(0.0)
		self.aqStrengthSpinBox.setMaximum(2.0)
		self.aqStrengthSpinBox.setSingleStep(0.1)
		self.aqStrengthSpinBox.setToolTip(
"--aq-strength <float>\n\
Sets the amount of bias towards low detail (‘flat’) macroblocks.\n\
Reduces blocking and blurring in flat textured areas.\n\
A higher value is recommended for grainy or animated sources.\n\n\
Default: 1.0\n\
Recommended: 1.30")
		self.aqStrengthSpinBox.setStyleSheet(
			'QToolTip {padding: -1px; opacity: 255}')

		self.mbTreeCheckBox = QCheckBox('MB-Tree')
		self.mbTreeCheckBox.setToolTip(
"--no-mbtree (to disable)\n\
Enables/disables Macroblock-Tree Rate Control. It tracks the change from future to past\n\
blocks across motion vectors. Therefore MB-Tree will only lower quality on the complex\n\
parts of the scene instead of on the entire scene. Static frames will remain high quality.\n\
MB-Tree greatly improves the overall quality and should always be enabled.\n\n\
Default: enabled\n\
Recommended: enabled")
		self.mbTreeCheckBox.setStyleSheet(
			'QToolTip {padding: -1px; opacity: 255}')

		self.frameLookaheadLabel = QLabel('Frame Lookahead')
		self.frameLookaheadSpinBox = QSpinBox()
		self.frameLookaheadSpinBox.setMinimum(0)
		self.frameLookaheadSpinBox.setMaximum(100)
		self.frameLookaheadSpinBox.setToolTip(
"--rc-lookahead <integer>\n\
This setting sets the number of frames for the encoder to consider as well as\n\
other factors before making a decision on the current frame type and quality.\n\n\
Default: 40\n\
Recommended: 40")
		self.frameLookaheadSpinBox.setStyleSheet(
			'QToolTip {padding: -1px; opacity: 255}')

	def aqModeValueChanged(self):
		if self.aqModeComboBox.currentIndex() == 0:
			self.aqStrengthLabel.setEnabled(False)
			self.aqStrengthSpinBox.setEnabled(False)
		else:
			self.aqStrengthLabel.setEnabled(True)
			self.aqStrengthSpinBox.setEnabled(True)


	"""
	Creating the Analysis Widgets
	"""
	def setAdvancedTab(self):
		print('Setting the Advanced Tab')

		self.meMethodLabel = QLabel('M.E. Method')
		self.meMethodComboBox = QComboBox()
		self.meMethodComboBox.addItem('Diamond')
		self.meMethodComboBox.addItem('Hexagon')
		self.meMethodComboBox.addItem('Multi-Hexagon')
		self.meMethodComboBox.addItem('Exhaustive')
		self.meMethodComboBox.addItem('Hadamard Exhaustive')
		self.meMethodComboBox.setToolTip(
"--me <string>\n\
Sets the full-pixel motion estimation method.\n\n\
Values:\n\
	-dia: (diamond) The simplest search starting at the best predictor and checks\n\
	  the motion vectors at a pixel upwards, left, down, and to the right. Picks\n\
	  the best and repeats the process until it no longer finds any better vector.\n\
	-hex: (hexagon) Similar to dia but uses a 2-range search of 6 surrounding pixels.\n\
	  Considerably more efficient than dia and hardly any slower, a good choice for\n\
	  general encoding.\n\
	-umh: (uneven multi-hex) Considerably slower than hex but searches a complex\n\
	  multi-hexagon pattern in order to avoid missing harder to find motion vectors.\n\
	-esa: (exhaustive) An intelligent search of the entire motion space\n\
	  within merange of the best predictor. Similar to a brute force method.\n\
	  Considerably slower than umh and without much benefit.\n\
	-tesa: (transformed exhaustive) Algorithm that attempts to appromiate the\n\
	  effect of running a Hadamard transform comparison at each motion vector,\n\
	  like exhaustive but better and slower.\n\
Default: hex\n\
Recommended: hex, umh")
		self.meMethodComboBox.setStyleSheet(
			'QToolTip {padding: -1px; opacity: 255}')
		
		self.meRangeLabel = QLabel('M.E. Range')
		self.meRangeSpinBox = QSpinBox()
		self.meRangeSpinBox.setMinimum(4)
		self.meRangeSpinBox.setMaximum(64)
		self.meRangeSpinBox.setToolTip(
"--merange <integer>\n\
Sets the max range of the motion search in pixels for the next frame. A high\n\
merange (>64) is unlikely to find any new motion vectors that are useful as\n\
the search will start at the predicted motion vector so ‘good’ motion vectors\n\
are usually found close to the predicted one.\n\n\
Default: 16\n\
Recommended: 16, 16+ (hex, umh)")
		self.meRangeSpinBox.setStyleSheet(
			'QToolTip {padding: -1px; opacity: 255}')

		self.subpixelRefinementLabel = QLabel('Subpixel Refinement')
		self.subPixelRefinementComboBox = QComboBox()
		self.subPixelRefinementComboBox.addItem('0: Full Pixel Only')
		self.subPixelRefinementComboBox.addItem('1: Quarter Pixel SAD')
		self.subPixelRefinementComboBox.addItem('2: Quarter Pixel SATD')
		self.subPixelRefinementComboBox.addItem('3: Half Pixel then QPel')
		self.subPixelRefinementComboBox.addItem('4: Always Quarter Pixel')
		self.subPixelRefinementComboBox.addItem('5: Multi QPel + Bidir ME')
		self.subPixelRefinementComboBox.addItem('6: RD on I/P Frames')
		self.subPixelRefinementComboBox.addItem('7: RD on all Frames')
		self.subPixelRefinementComboBox.addItem('8: RD Refine I/P Frames')
		self.subPixelRefinementComboBox.addItem('9: RD Refine all Frames')
		self.subPixelRefinementComboBox.addItem('10: Quarter Pixel-RD')
		self.subPixelRefinementComboBox.addItem('11: Full RD')
		self.subPixelRefinementComboBox.currentIndexChanged.connect(
			self.subPixelRefinementValueChanged)
		self.subPixelRefinementComboBox.setToolTip(
"--subme <integer>\n\
Sets the subpixel estimation complexity. Higher values are better as it reduces\n\
artifacts and retains fine details. Important encoding parameter, which determines\n\
which algorithms are used for subpixel motion searching and partition decision.\n\
Levels 1-5 controls the subpixel refinement strength.\n\
Level 6 enables Rate-Distortion Optimization (RDO) for mode decision which\n\
helps improve video quality in video compression. RDO levels considerably\n\
slow down encoding speed.\n\
Level 8 enables RDO for motion vectors and intra-prediction modes.\n\n\
Values:\n\
	0: Full Pixel only\n\
	1: Quarter Pixel (QPel) SAD 1 iteration\n\
	2: QPel SATD 2 iteration\n\
	3: Half Pixel (HPel) on MB then QPel\n\
	4: Always QPel\n\
	5: Multi QPel and bi-directional motion estimation\n\
	6: RD mode decision on I/P frames\n\
	7: RD on all frames\n\
	8: RD refinement after RD mode decision on I/P frames\n\
	9: RD refinement on all frames\n\
	10: QP-RD (requires –-trellis=2, --aq-mode>0)\n\
	11: Full RD\n\
Default: 7\n\
Recommended: 7-10")
		self.subPixelRefinementComboBox.setStyleSheet(
			'QToolTip {padding: -1px; opacity: 255}')

		self.motionVectorPredictionLabel = QLabel('Motion Vector Prediction')
		self.motionVectorPredictionComboBox = QComboBox()
		self.motionVectorPredictionComboBox.addItem('None')
		self.motionVectorPredictionComboBox.addItem('Spatial')
		self.motionVectorPredictionComboBox.addItem('Temporal')
		self.motionVectorPredictionComboBox.addItem('Auto')
		self.motionVectorPredictionComboBox.setToolTip(
"--direct <string>\n\
Sets the prediction mode for ‘direct’ motion vectors. Direct prediction tells x264\n\
what method to use when applying motion estimation for certain parts of a B-frame.\n\n\
Values:\n\
	-none: Disables direct motion vectors (not recommended, waste bits and looks worse).\n\
	-spatial: Tells x264 to predict motion based on other parts of the same frame.\n\
	-temporal: Predicts motion based on the following P-frame.\n\
	-auto: switches between prediction modes depending on which performed the best so far.\n\
Default: spatial\n\
Recommended: auto")
		self.motionVectorPredictionComboBox.setStyleSheet(
			'QToolTip {padding: -1px; opacity: 255}')

		self.trellisLabel = QLabel('Trellis')
		self.trellisComboBox = QComboBox()
		self.trellisComboBox.addItem('Disabled')
		self.trellisComboBox.addItem('Final MB')
		self.trellisComboBox.addItem('Always')
		self.trellisComboBox.currentIndexChanged.connect(
			self.trellisValueChanged)
		self.trellisComboBox.setToolTip(
"--trellis <integer>\n\
Increases hard-edge details by increasing efficiency in data compression\n\
at a somewhat slower speed. Usually improves overall quality of encodes.\n\
Values:\n\
	0: Disabled\n\
	1: Enabled only on final encode of a macroblock\n\
	2: Enabled on all mode decisions\n\
Default: 1\n\
Recommended: 1, 2")
		self.trellisComboBox.setStyleSheet(
			'QToolTip {padding: -1px; opacity: 255}')

		self.psyrdStrengthLabel = QLabel('Psy-RD Strength')
		self.psyrdStrengthSpinBox = QDoubleSpinBox()
		self.psyrdStrengthSpinBox.setMinimum(0.0)
		self.psyrdStrengthSpinBox.setMaximum(2.0)
		self.psyrdStrengthSpinBox.setDecimals(1)
		self.psyrdStrengthSpinBox.setSingleStep(0.1)
		self.psyrdStrengthSpinBox.setToolTip(
"--psy-rd <float>:<float>\n\
The first value is the Psy-RD strength, representing\n\
the amount of bias in favor of detail retention.\n\
psy-rd strength (requires --subme>=6)\n\n\
Default: 1.0\n\
Recommended: ~0.5 (animation)")
		self.psyrdStrengthSpinBox.setStyleSheet(
			'QToolTip {padding: -1px; opacity: 255}')

		self.psyTrellisStrengthLabel = QLabel('Psy-Trellis Strength')
		self.psyTrellisStrengthSpinBox = QDoubleSpinBox()
		self.psyTrellisStrengthSpinBox.setMinimum(0.0)
		self.psyTrellisStrengthSpinBox.setMaximum(2.0)
		self.psyTrellisStrengthSpinBox.setDecimals(1)
		self.psyTrellisStrengthSpinBox.setSingleStep(0.1)
		self.psyTrellisStrengthSpinBox.setToolTip(
"--psy-rd <float>:<float>\n\
The second value is psy-trellis. The higher the value,\n\
the more detail and sharpness can be retained but also\n\
increases the risk of unwanted artifacts.\n\
psy-trellis strength (requires --trellis>=1)\n\n\
Default: 0.0\n\
Recommended: ~0.6 (animation)")
		self.psyTrellisStrengthSpinBox.setStyleSheet(
			'QToolTip {padding: -1px; opacity: 255}')

		self.fastPSkipCheckBox = QCheckBox('Fast P-Skip')
		self.fastPSkipCheckBox.setToolTip(
"--no-fast-pskip (to disable)\n\
Enables/disables early skip detection on P-frames. Disabling pskip detection\n\
increases encoding speed but may cause artifacts in areas of solid\n\
color or gradients such as dark scenes or sky.\n\n\
Default: enabled\n\
Recommended: enabled")
		self.fastPSkipCheckBox.setStyleSheet(
			'QToolTip {padding: -1px; opacity: 255}')

		self.resizeCheckBox = QCheckBox('Resize Video')
		self.resizeCheckBox.stateChanged.connect(
			self.resizeStateChanged)
		self.resizeCheckBox.setToolTip(
"--video-filter, --vf resize:[width=<integer>,height=<integer>][,method=<string>]\n\
Enables/disables video resizing using the specified method and resolution.\n\n\
Default: disabled")
		self.resizeCheckBox.setStyleSheet(
			'QToolTip {padding: -1px; opacity: 255}')

		self.resizeMethodLabel = QLabel('Resize Method')
		self.resizeMethodComboBox = QComboBox()
		self.resizeMethodComboBox.addItem('fastbilinear')
		self.resizeMethodComboBox.addItem('bilinear')
		self.resizeMethodComboBox.addItem('bicubic')
		self.resizeMethodComboBox.addItem('experimental')
		self.resizeMethodComboBox.addItem('point')
		self.resizeMethodComboBox.addItem('area')
		self.resizeMethodComboBox.addItem('bicublin')
		self.resizeMethodComboBox.addItem('gauss')
		self.resizeMethodComboBox.addItem('sinc')
		self.resizeMethodComboBox.addItem('lanczos')
		self.resizeMethodComboBox.addItem('spline')
		self.resizeMethodComboBox.setToolTip(
"method=<string>\n\
Sets the method to use for resizing.\n\n\
Values: fastbilinear, bilinear, bicubic, experimental, point,\n\
	area, bicublin, gauss, sinc, lanczos, spline\n\
Default: disabled\n\
Recommended: bicubic or gauss, bilinear (downscaling) or\n\
	cubic, spline, lanczos (upscaling)")
		self.resizeMethodComboBox.setStyleSheet(
			'QToolTip {padding: -1px; opacity: 255}')

		self.resizeResolutionLabel = QLabel('Resolution')
		self.resizeWidthLabel = QLabel('Width')
		self.resizeWidthSpinBox = QSpinBox()
		self.resizeWidthSpinBox.setMinimum(320)
		self.resizeWidthSpinBox.setMaximum(4096)
		self.resizeWidthSpinBox.setSingleStep(2)

		self.resizeHeightLabel = QLabel('Height')
		self.resizeHeightSpinBox = QSpinBox()
		self.resizeHeightSpinBox.setMinimum(200)
		self.resizeHeightSpinBox.setMaximum(2160)
		self.resizeHeightSpinBox.setSingleStep(2)


	def subPixelRefinementValueChanged(self):
		if self.subPixelRefinementComboBox.currentIndex() == 10:
			self.trellisComboBox.setCurrentIndex(2)
			self.trellisComboBox.model().item(0).setEnabled(False)
			self.trellisComboBox.model().item(1).setEnabled(False)
		else:
			self.trellisComboBox.model().item(0).setEnabled(True)
			self.trellisComboBox.model().item(1).setEnabled(True)

		if self.subPixelRefinementComboBox.currentIndex() < 6:
			self.psyrdStrengthLabel.setEnabled(False)
			self.psyrdStrengthSpinBox.setEnabled(False)
			self.psyTrellisStrengthLabel.setEnabled(False)
			self.psyTrellisStrengthSpinBox.setEnabled(False)
		else:
			self.psyrdStrengthLabel.setEnabled(True)
			self.psyrdStrengthSpinBox.setEnabled(True)
			self.psyTrellisStrengthLabel.setEnabled(True)
			self.psyTrellisStrengthSpinBox.setEnabled(True)

	def trellisValueChanged(self):
		if self.trellisComboBox.currentIndex() == 0:
			self.psyTrellisStrengthLabel.setEnabled(False)
			self.psyTrellisStrengthSpinBox.setEnabled(False)
			self.psyTrellisStrengthSpinBox.setValue(0.0)
		else:
			self.psyTrellisStrengthLabel.setEnabled(True)
			self.psyTrellisStrengthSpinBox.setEnabled(True)

	def resizeStateChanged(self):
		if self.resizeCheckBox.isChecked():
			self.resizeMethodLabel.setEnabled(True)
			self.resizeMethodComboBox.setEnabled(True)
			self.resizeResolutionLabel.setEnabled(True)
			self.resizeWidthLabel.setEnabled(True)
			self.resizeWidthSpinBox.setEnabled(True)
			self.resizeHeightLabel.setEnabled(True)
			self.resizeHeightSpinBox.setEnabled(True)
		else:
			self.resizeMethodLabel.setEnabled(False)
			self.resizeMethodComboBox.setEnabled(False)
			self.resizeResolutionLabel.setEnabled(False)
			self.resizeWidthLabel.setEnabled(False)
			self.resizeWidthSpinBox.setEnabled(False)
			self.resizeHeightLabel.setEnabled(False)
			self.resizeHeightSpinBox.setEnabled(False)


	def setMiscTab(self):
		print('Setting the Misc Tab')

		self.audioSourceCheckBox = QCheckBox('Use Source Tracks')
		self.audioSourceCheckBox.stateChanged.connect(
			self.audioStateChanged)
		self.audioSourceCheckBox.setToolTip(
"Uses source audio tracks or encode audio into AAC format.\n\n\
Default: enabled (uses source tracks)\n\
Recommended: enabled (source tracks are already AAC), disabled (FLAC)")
		self.audioSourceCheckBox.setStyleSheet(
			'QToolTip {padding: -1px; opacity: 255}')

		self.audioQualityLabel = QLabel('AAC Quality')
		self.audioQualitySpinBox = QDoubleSpinBox()
		self.audioQualitySpinBox.setMinimum(0.00)
		self.audioQualitySpinBox.setMaximum(1.00)
		self.audioQualitySpinBox.setSingleStep(0.05)
		self.audioQualitySpinBox.setToolTip(
"Sets the target quality of the output audio.\n\
A higher value increases quality and file size.\n\n\
Default: 0.50\n\
Recommended: 0.50")
		self.audioQualitySpinBox.setStyleSheet(
			'QToolTip {padding: -1px; opacity: 255}')

		self.customCmdLineTextEdit = QTextEdit()
		self.customCmdLineTextEdit.setWordWrapMode(QTextOption.WordWrap)
		self.customCmdLineTextEdit.setSizePolicy(
			QSizePolicy.Ignored, QSizePolicy.Ignored)
		self.customCmdLineTextEdit.textChanged.connect(self.customCmdLineUpdated)

		self.cmdLineOutputTextBrowser = QTextEdit()
		self.cmdLineOutputTextBrowser.setWordWrapMode(QTextOption.WordWrap)
		self.cmdLineOutputTextBrowser.setReadOnly(True)
		self.cmdLineOutputTextBrowser.setSizePolicy(
			QSizePolicy.Ignored, QSizePolicy.Ignored)
		self.cmdLineOutputTextBrowser.viewport().setCursor(Qt.ArrowCursor)

		self.cmdLineDisplayTextBrowser = QTextEdit()
		self.cmdLineDisplayTextBrowser.setWordWrapMode(QTextOption.WordWrap)
		self.cmdLineDisplayTextBrowser.setReadOnly(True)
		self.cmdLineDisplayTextBrowser.setSizePolicy(
			QSizePolicy.Ignored, QSizePolicy.Ignored)
		self.cmdLineDisplayTextBrowser.viewport().setCursor(Qt.ArrowCursor)

	def audioStateChanged(self):
		if self.audioSourceCheckBox.isChecked():
			self.audioQualityLabel.setEnabled(False)
			self.audioQualitySpinBox.setEnabled(False)
		else:
			self.audioQualityLabel.setEnabled(True)
			self.audioQualitySpinBox.setEnabled(True)

	def customCmdLineUpdated(self):
		self.cmdLineDisplayTextBrowser.setText(
			self.cmdLineOutputTextBrowser.toPlainText() +
			self.customCmdLineTextEdit.toPlainText().strip())

	"""
	Setting the layout of widgets
	"""
	def layoutMainGrid(self):
		grid = QGridLayout()
		grid.setSpacing(10)

		grid.addWidget(self.tabs, 0, 0, 49, 50)

		grid.addWidget(self.profileLabel, 49, 0, 1, 4)
		grid.addWidget(self.profileComboBox, 49, 4, 1, 33)
		grid.addWidget(self.renameProfileButton, 49, 37, 1, 1)
		grid.addWidget(self.addProfileButton, 49, 38, 1, 3)
		grid.addWidget(self.deleteProfileButton, 49, 41, 1, 3)
		grid.addWidget(self.saveProfileButton, 49, 44, 1, 3)
		grid.addWidget(self.restoreProfileButton, 49, 47, 1, 3)

		self.settingsWindow = QDialog(self.mainWindow, 
			Qt.WindowCloseButtonHint)
		self.settingsWindow.setWindowIcon(QIcon(os.path.normpath(
			'./Icons/transparent.png')))
		self.settingsWindow.setWindowTitle('Encoding Settings')
		self.settingsWindow.setMinimumSize(590, 450)

		self.settingsWindow.setFixedSize(self.settingsWindow.size())
		self.settingsWindow.setLayout(grid)

	def layoutCommonGrid(self):
		emptyCell = QLabel('')
		emptyCell1= QLabel('')

		encodingModeGroup = QGroupBox('Encoding Mode')
		grid1 = QGridLayout()
		grid1.addWidget(self.encodingModeComboBox, 0, 0, 1, 6)
		grid1.addWidget(emptyCell, 0, 6, 1, 1)
		grid1.addWidget(self.encodingModeValueLabel, 0, 7, 1, 1)
		grid1.addWidget(self.encodingModeValueDoubleSpinBox, 0, 8, 1, 1)
		encodingModeGroup.setLayout(grid1)

		tuneGroup = QGroupBox('Tuning')
		grid2 = QGridLayout()
		grid2.addWidget(self.tuningComboBox)
		tuneGroup.setLayout(grid2)

		presetGroup = QGroupBox('Preset')
		grid3 = QGridLayout()
		grid3.addWidget(self.presetLabel, 0, 1, 2, 9)
		grid3.addWidget(self.presetSlider, 2, 0, 2, 10)
		presetGroup.setLayout(grid3)

		self.AVCprofileGroup = QGroupBox('AVC Profile')
		grid4 = QGridLayout()
		grid4.addWidget(self.AVCprofileComboBox)
		self.AVCprofileGroup.setLayout(grid4)

		levelGroup = QGroupBox('Level')
		grid5 = QGridLayout()
		grid5.addWidget(self.levelComboBox)
		levelGroup.setLayout(grid5)

		commonGrid = QGridLayout()
		commonGrid.setSpacing(5)

		commonGrid.addWidget(emptyCell1, 0, 0)
		commonGrid.addWidget(encodingModeGroup, 1, 0, 1, 8)
		commonGrid.addWidget(tuneGroup, 1, 8, 1, 2)
		commonGrid.addWidget(presetGroup, 2, 0, 2, 8)
		commonGrid.addWidget(self.AVCprofileGroup, 2, 8, 1, 2)
		commonGrid.addWidget(levelGroup, 3, 8, 1, 2)
		commonGrid.addWidget(self.bitDepthCheckBox, 4, 0, 2, 1)
		commonGrid.addWidget(self.quickSettingsCheckBox, 5, 0, 2, 1)
		
		self.tab1.setLayout(commonGrid)

	def layoutFrameTypeGrid(self):
		emptyCell = QLabel('')
		emptyCell1 = QLabel('')

		deblockingGroup = QGroupBox('Deblocking')
		grid1 = QGridLayout()
		grid1.addWidget(self.deblockingCheckBox, 0, 0)
		grid1.addWidget(self.deblockingStrLabel, 1, 0, 1, 2)
		grid1.addWidget(self.deblockingStrSpinBox, 1, 2, 1, 1)
		grid1.addWidget(self.deblockingThresholdLabel, 2, 0, 1, 2)
		grid1.addWidget(self.deblockingThresholdSpinBox, 2, 2, 1, 1)
		deblockingGroup.setLayout(grid1)

		gopGroup = QGroupBox('GOP Size')
		grid2 = QGridLayout()
		grid2.addWidget(self.gopMaxSizeLabel, 0, 0, 1, 2)
		grid2.addWidget(self.gopMaxSizeSpinBox, 0, 2, 1, 1)
		grid2.addWidget(self.gopMinSizeLabel, 1, 0, 1, 2)
		grid2.addWidget(self.gopMinSizeSpinBox, 1, 2, 1, 1)
		gopGroup.setLayout(grid2)

		bframeGroup = QGroupBox('B-Frames')
		grid3 = QGridLayout()
		grid3.addWidget(self.bframeWeightCheckBox, 0, 0, 2, 3)
		grid3.addWidget(self.bframeNumberLabel, 2, 0, 2, 2)
		grid3.addWidget(self.bframeNumberSpinBox, 2, 2, 2, 1)
		grid3.addWidget(self.bframeBiasLabel, 4, 0, 2, 2)
		grid3.addWidget(self.bframeBiasSpinBox, 4, 2, 2, 1)
		grid3.addWidget(emptyCell1, 6, 0, 1, 1)
		grid3.addWidget(self.bframeAdaptiveLabel, 7, 0, 2, 2)
		grid3.addWidget(self.bframeAdaptiveComboBox, 7, 2, 2, 1)
		grid3.addWidget(self.bframePyramidLabel, 9, 0, 2, 2)
		grid3.addWidget(self.bframePyramidComboBox, 9, 2, 2, 1)
		bframeGroup.setLayout(grid3)

		frameEncodingGroup = QGroupBox('Frame Encoding')
		grid4 = QGridLayout()
		grid4.addWidget(self.frameEncodingRefLabel, 0, 0, 1, 3)
		grid4.addWidget(self.frameEncodingRefSpinBox, 0, 3, 1, 1)
		grid4.addWidget(emptyCell, 0, 4, 1, 1)
		grid4.addWidget(self.frameEncodingSceneChangeLabel, 0, 5, 1, 3)
		grid4.addWidget(self.frameEncodingSceneChangeSpinBox, 0, 8, 1, 1)
		frameEncodingGroup.setLayout(grid4)

		frametypeTabGrid = QGridLayout()
		frametypeTabGrid.setSpacing(5)

		frametypeTabGrid.addWidget(deblockingGroup, 0, 0, 5, 3)
		frametypeTabGrid.addWidget(gopGroup, 5, 0, 3, 3)
		# frametypeTabGrid.addWidget(self.cabacCheckBox, 7, 1, 1, 1)
		frametypeTabGrid.addWidget(bframeGroup, 0, 3, 8, 3)
		frametypeTabGrid.addWidget(frameEncodingGroup, 8, 0, 2, 6)

		self.tab2.setLayout(frametypeTabGrid)

	def layoutRateControlGrid(self):
		emptyCell = QLabel('')

		qpGroup = QGroupBox('Quantizers')
		grid1 = QGridLayout()
		
		grid1.addWidget(self.qpMinLabel, 0, 10, 1, 10)
		grid1.addWidget(self.qpMaxLabel, 0, 20, 1, 10)

		self.qpMinLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
		self.qpMaxLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

		self.qpIFrameLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
		grid1.addWidget(self.qpIFrameLabel, 1, 3, 1, 7)
		grid1.addWidget(self.qpIMinSpinBox, 1, 10, 1, 10)
		grid1.addWidget(self.qpIMaxSpinBox, 1, 20, 1, 10)

		self.qpPFrameLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
		grid1.addWidget(self.qpPFrameLabel, 2, 3, 1, 7)
		grid1.addWidget(self.qpPMinSpinBox, 2, 10, 1, 10)
		grid1.addWidget(self.qpPMaxSpinBox, 2, 20, 1, 10)

		self.qpBFrameLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
		grid1.addWidget(self.qpBFrameLabel, 3, 3, 1, 7)
		grid1.addWidget(self.qpBMinSpinBox, 3, 10, 1, 10)
		grid1.addWidget(self.qpBMaxSpinBox, 3, 20, 1, 10)

		self.qpStepLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
		grid1.addWidget(self.qpStepLabel, 0, 37, 1, 10)
		self.qpStepSpinBox.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
		grid1.addWidget(self.qpStepSpinBox, 1, 37, 1, 10)

		self.qCompLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
		grid1.addWidget(self.qCompLabel, 2, 34, 1, 16)
		self.qCompSpinBox.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
		grid1.addWidget(self.qCompSpinBox, 3, 37, 1, 10)

		grid1.addWidget(emptyCell, 4, 0, 1, 50)

		grid1.addWidget(self.qpRatioLabel, 5, 0, 1, 50)
		self.qpRatioLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

		grid1.addWidget(self.qpIPRatioLabel, 6, 2, 1, 10)
		grid1.addWidget(self.qpIPRatioSpinBox, 6, 12, 1, 10)

		grid1.addWidget(self.qpPBRatioLabel, 6, 28, 1, 10)
		grid1.addWidget(self.qpPBRatioSpinBox, 6, 38, 1, 10)
		qpGroup.setLayout(grid1)

		aqGroup = QGroupBox('Adaptive Quantizers')
		grid2 = QGridLayout()
		grid2.addWidget(self.aqModeLabel, 0, 0, 1, 1)
		grid2.addWidget(self.aqModeComboBox, 0, 1, 1, 2)
		grid2.addWidget(self.aqStrengthLabel, 1, 0, 1, 1)
		grid2.addWidget(self.aqStrengthSpinBox, 1, 2, 1, 1)
		aqGroup.setLayout(grid2)

		mbTreeGroup = QGroupBox('Macroblock-Tree')
		grid3 = QGridLayout()
		grid3.addWidget(self.mbTreeCheckBox, 0, 0, 1, 1)
		grid3.addWidget(self.frameLookaheadLabel, 1, 0, 1, 2)
		grid3.addWidget(self.frameLookaheadSpinBox, 1, 2, 1, 1)
		mbTreeGroup.setLayout(grid3)

		rateControlGrid = QGridLayout()
		rateControlGrid.setSpacing(5)

		rateControlGrid.addWidget(qpGroup, 0, 0, 15, 10)
		rateControlGrid.addWidget(aqGroup, 15, 0, 6, 5)
		rateControlGrid.addWidget(mbTreeGroup, 15, 5, 6, 5)

		self.tab3.setLayout(rateControlGrid)

	def layoutAdvancedGrid(self):
		emptyCell = QLabel('')

		meGroup = QGroupBox('Motion Estimation')
		grid1 = QGridLayout()

		grid1.addWidget(self.meMethodLabel, 0, 0, 1, 11)
		grid1.addWidget(self.meMethodComboBox, 0, 11, 1, 9)

		grid1.addWidget(self.meRangeLabel, 1, 0, 1, 10)
		grid1.addWidget(self.meRangeSpinBox, 1, 16, 1, 4)

		grid1.addWidget(self.motionVectorPredictionLabel, 2, 0, 1, 11)
		grid1.addWidget(self.motionVectorPredictionComboBox, 2, 15, 1, 5)

		grid1.addWidget(self.subpixelRefinementLabel, 3, 0, 1, 11)
		grid1.addWidget(self.subPixelRefinementComboBox, 3, 11, 1, 9)
		meGroup.setLayout(grid1)

		detailGroup = QGroupBox('Detail')
		grid2 = QGridLayout()

		grid2.addWidget(self.trellisLabel, 0, 0, 1, 10)
		grid2.addWidget(self.trellisComboBox, 0, 10, 1, 10)

		grid2.addWidget(self.psyrdStrengthLabel, 1, 0, 1, 12)
		grid2.addWidget(self.psyrdStrengthSpinBox, 1, 12, 1, 8)

		grid2.addWidget(self.psyTrellisStrengthLabel, 2, 0, 1, 12)
		grid2.addWidget(self.psyTrellisStrengthSpinBox, 2, 12, 1, 8)

		grid2.addWidget(self.fastPSkipCheckBox, 3, 0, 1, 12)
		detailGroup.setLayout(grid2)

		resizeGroup = QGroupBox('Video Resize')
		grid3 = QGridLayout()

		grid3.addWidget(self.resizeCheckBox, 0, 0, 1, 10)
		grid3.addWidget(self.resizeMethodLabel, 1, 0, 1, 10)
		grid3.addWidget(self.resizeMethodComboBox, 1, 10, 1, 10)

		grid3.addWidget(emptyCell, 0, 20, 1, 4)

		grid3.addWidget(self.resizeResolutionLabel, 1, 24, 1, 6)
		grid3.addWidget(self.resizeWidthLabel, 0, 30, 1, 10)
		grid3.addWidget(self.resizeWidthSpinBox, 1, 30, 1, 10)

		grid3.addWidget(self.resizeHeightLabel, 0, 40, 1, 10)
		grid3.addWidget(self.resizeHeightSpinBox, 1, 40, 1, 10)

		self.resizeWidthLabel.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
		self.resizeHeightLabel.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
		self.resizeWidthSpinBox.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
		self.resizeHeightSpinBox.setAlignment(Qt.AlignHCenter | 
			Qt.AlignVCenter)

		resizeGroup.setLayout(grid3)

		advancedGrid = QGridLayout()
		advancedGrid.setSpacing(5)

		advancedGrid.addWidget(meGroup, 0, 0, 25, 30)
		advancedGrid.addWidget(detailGroup, 0, 30, 25, 20)
		advancedGrid.addWidget(resizeGroup, 25, 0, 10, 50)

		self.tab4.setLayout(advancedGrid)


	def layoutMiscGrid(self):
		emptyCell = QLabel('')
		emptyCell1 = QLabel('')

		audioGroup = QGroupBox('Audio')
		grid1 = QGridLayout()
		grid1.addWidget(self.audioSourceCheckBox, 0, 0, 1, 20)
		grid1.addWidget(emptyCell, 0, 20, 1, 10)
		grid1.addWidget(self.audioQualityLabel, 0, 35, 1, 5)
		grid1.addWidget(self.audioQualitySpinBox, 0, 40, 1, 10)
		audioGroup.setLayout(grid1)


		customCmdGroup = QGroupBox('Custom Command Line')
		grid2 = QGridLayout()
		grid2.setSpacing(10)

		grid2.addWidget(self.customCmdLineTextEdit, 0, 0)
		customCmdGroup.setLayout(grid2)

		cmdOuputGroup = QGroupBox('Command Line Output')
		grid3 = QGridLayout()
		grid3.setSpacing(10)

		grid3.addWidget(self.cmdLineDisplayTextBrowser, 0, 0)
		cmdOuputGroup.setLayout(grid3)

		miscGrid = QGridLayout()
		miscGrid.setSpacing(5)

		miscGrid.addWidget(audioGroup, 0, 1, 1, 8)
		miscGrid.addWidget(emptyCell1, 1, 0, 1, 10)
		miscGrid.addWidget(customCmdGroup, 2, 1, 2, 8)
		miscGrid.addWidget(cmdOuputGroup, 5, 0, 4, 10)

		self.tab5.setLayout(miscGrid)



	"""
	Profile Load Settings methods
	"""
	def loadProfileSettings(self):
		if self.profileComboBox.currentText() == '':
			return None

		config = configparser.ConfigParser()
		config.read(os.path.normpath('./profiles/' + 
			self.profileComboBox.currentText() + '.ini'))

		print("reading from " + self.profileComboBox.currentText() + '.ini')

		if config.getint('Common', 'EncodingMode') == 0:
			self.encodingModeComboBox.setCurrentIndex(0)

			self.encodingModeValueDoubleSpinBox.setMinimum(0)
			self.encodingModeValueDoubleSpinBox.setMaximum(81)
			self.encodingModeValueDoubleSpinBox.setDecimals(0)
			self.encodingModeValueDoubleSpinBox.setSingleStep(1)

			self.encodingModeValueLabel.setText('Quantizer')
			self.encodingModeValueDoubleSpinBox.setValue(
				config.getfloat('Common', 'EncodingQuality'))
		elif config.getint('Common', 'EncodingMode') == 1:
			self.encodingModeComboBox.setCurrentIndex(1)

			self.encodingModeValueDoubleSpinBox.setMinimum(0)
			self.encodingModeValueDoubleSpinBox.setMaximum(51)
			self.encodingModeValueDoubleSpinBox.setDecimals(1)
			self.encodingModeValueDoubleSpinBox.setSingleStep(0.1)

			self.encodingModeValueLabel.setText('Quality')
			self.encodingModeValueDoubleSpinBox.setValue(
				config.getfloat('Common', 'EncodingQuality'))

		self.tuningComboBox.setCurrentIndex(config.getint('Common', 'Tuning'))

		self.presetSlider.setValue(config.getint('Common', 'Preset'))

		self.AVCprofileComboBox.setCurrentIndex(
			config.getint('Common', 'AVCProfile'))

		self.levelComboBox.setCurrentIndex(config.getint('Common', 'Level'))

		self.bitDepthCheckBox.setChecked(
			config.getboolean('Common', '10BitDepth'))

		if self.bitDepthCheckBox.isChecked():
			self.AVCprofileGroup.setEnabled(False)

		self.quickSettingsCheckBox.setChecked(
			config.getboolean('Common', 'QuickSettings'))

		if self.quickSettingsCheckBox.isChecked():
			self.tabs.removeTab(1)
			self.tabs.removeTab(1)
			self.tabs.removeTab(1)
			self.tabs.removeTab(1)
			self.tabs.addTab(self.tab2, ' Frame-Type ')
			self.tabs.addTab(self.tab3, ' Rate Control ')
			self.tabs.addTab(self.tab4, ' Advanced ')
			self.tabs.addTab(self.tab5, ' Misc ')
		else:
			self.tabs.removeTab(1)
			self.tabs.removeTab(1)
			self.tabs.removeTab(1)
			self.tabs.removeTab(1)
			self.tabs.addTab(self.tab5, ' Misc ')

		self.loadFrameTypeSettings(config)
		self.loadRateControlSettings(config)
		self.loadAdvancedSettings(config)
		self.loadMiscSettings(config)

	def loadFrameTypeSettings(self, config):
		self.deblockingCheckBox.setChecked(
			config.getboolean('Frame Type', 'Deblocking'))

		if self.deblockingCheckBox.isChecked() == False:
			self.deblockingStrLabel.setEnabled(False)
			self.deblockingThresholdLabel.setEnabled(False)
			self.deblockingStrSpinBox.setEnabled(False)
			self.deblockingThresholdSpinBox.setEnabled(False)

		self.deblockingStrSpinBox.setValue(
			config.getint('Frame Type', 'DeblockingStrength'))
		self.deblockingThresholdSpinBox.setValue(
			config.getint('Frame Type', 'DeblockingThreshold'))

		self.gopMaxSizeSpinBox.setValue(
			config.getint('Frame Type', 'GOPMaxSize'))
		self.gopMinSizeSpinBox.setValue(
			config.getint('Frame Type', 'GOPMinSize'))

		self.bframeWeightCheckBox.setChecked(
			config.getboolean('Frame Type', 'BFrameWeighted'))
		self.bframeNumberSpinBox.setValue(
			config.getint('Frame Type', 'BFrameNumber'))
		self.bframeBiasSpinBox.setValue(
			config.getint('Frame Type', 'BFrameBias'))
		self.bframeAdaptiveComboBox.setCurrentIndex(
			config.getint('Frame Type', 'BFrameAdaptive'))
		self.bframePyramidComboBox.setCurrentIndex(
			config.getint('Frame Type', 'BFramePyramid'))

		self.frameEncodingRefSpinBox.setValue(
			config.getint('Frame Type', 'References'))
		self.frameEncodingSceneChangeSpinBox.setValue(
			config.getint('Frame Type', 'SceneCut'))

	def loadRateControlSettings(self, config):
		self.qpIMinSpinBox.setValue(
			config.getint('Rate Control', 'IframeQPMin'))
		self.qpIMaxSpinBox.setValue(
			config.getint('Rate Control', 'IframeQPMax'))

		self.qpPMinSpinBox.setValue(
			config.getint('Rate Control', 'PframeQPMin'))
		self.qpPMaxSpinBox.setValue(
			config.getint('Rate Control', 'PframeQPMax'))

		self.qpBMinSpinBox.setValue(
			config.getint('Rate Control', 'BframeQPMin'))
		self.qpBMaxSpinBox.setValue(
			config.getint('Rate Control', 'BframeQPMax'))

		self.qpStepSpinBox.setValue(config.getint('Rate Control', 'QPStep'))
		self.qCompSpinBox.setValue(config.getfloat('Rate Control', 'QPComp'))

		self.qpIPRatioSpinBox.setValue(
			config.getfloat('Rate Control', 'IPRatio'))
		self.qpPBRatioSpinBox.setValue(
			config.getfloat('Rate Control', 'PBRatio'))

		self.aqModeComboBox.setCurrentIndex(
			config.getint('Rate Control', 'AQMode'))
		self.aqStrengthSpinBox.setValue(
			config.getfloat('Rate Control', 'AQStrength'))

		if self.aqModeComboBox.currentIndex == 0:
			self.aqStrengthLabel.setEnabled(False)
			self.aqStrengthSpinBox.setEnabled(False)

		self.mbTreeCheckBox.setChecked(
			config.getboolean('Rate Control', 'MBTree'))
		self.frameLookaheadSpinBox.setValue(
			config.getint('Rate Control', 'FrameLookahead'))

	def loadAdvancedSettings(self, config):
		self.meRangeSpinBox.setValue(config.getint('Advanced', 'MeRange'))
		self.meMethodComboBox.setCurrentIndex(
			config.getint('Advanced', 'MeMethod'))
		self.subPixelRefinementComboBox.setCurrentIndex(
			config.getint('Advanced', 'SubME'))
		self.motionVectorPredictionComboBox.setCurrentIndex(
			config.getint('Advanced', 'MVPrediction'))

		self.trellisComboBox.setCurrentIndex(
			config.getint('Advanced', 'trellis'))
		self.psyrdStrengthSpinBox.setValue(
			config.getfloat('Advanced', 'PsyRDStr'))
		self.psyTrellisStrengthSpinBox.setValue(
			config.getfloat('Advanced', 'PsyTrellisStr'))
		self.fastPSkipCheckBox.setChecked(
			config.getboolean('Advanced', 'FastPSkip'))

		self.resizeCheckBox.setChecked(config.getboolean('Advanced', 'Resize'))
		self.resizeMethodComboBox.setCurrentIndex(
			config.getint('Advanced', 'ResizeMethod'))
		self.resizeWidthSpinBox.setValue(config.getint('Advanced', 'Width'))
		self.resizeHeightSpinBox.setValue(config.getint('Advanced', 'Height'))

		if self.subPixelRefinementComboBox.currentIndex() == 10:
			self.trellisComboBox.setCurrentIndex(2)
			self.trellisComboBox.model().item(0).setEnabled(False)
			self.trellisComboBox.model().item(1).setEnabled(False)
		elif self.subPixelRefinementComboBox.currentIndex() < 6:
			self.psyrdStrengthLabel.setEnabled(False)
			self.psyrdStrengthSpinBox.setEnabled(False)
			self.psyTrellisStrengthLabel.setEnabled(False)
			self.psyTrellisStrengthSpinBox.setEnabled(False)

		if self.trellisComboBox.currentIndex() == 0:
			self.psyTrellisStrengthLabel.setEnabled(False)
			self.psyTrellisStrengthSpinBox.setEnabled(False)

		if self.resizeCheckBox.isChecked() == False:
			self.resizeMethodLabel.setEnabled(False)
			self.resizeMethodComboBox.setEnabled(False)
			self.resizeResolutionLabel.setEnabled(False)
			self.resizeWidthLabel.setEnabled(False)
			self.resizeWidthSpinBox.setEnabled(False)
			self.resizeHeightLabel.setEnabled(False)
			self.resizeHeightSpinBox.setEnabled(False)

	def loadMiscSettings(self, config):
		self.audioSourceCheckBox.setChecked(
			config.getboolean('Misc', 'audioSource'))
		self.audioQualitySpinBox.setValue(
			config.getfloat('Misc', 'audioQuality'))
		self.customCmdLineTextEdit.setText(config.get('Misc', 'customCmdLine'))
		self.cmdLineOutputTextBrowser.setText(
			config.get('Misc', 'commandLineOutput'))

		self.customCmdLineTextEdit.setPlainText(
			config.get('Misc', 'customCmdLine'))

		self.cmdLineDisplayTextBrowser.setText(config.get('Misc', 'commandLineOutput') + config.get('Misc', 'customCmdLine'))

		if self.audioSourceCheckBox.isChecked():
			self.audioQualityLabel.setEnabled(False)
			self.audioQualitySpinBox.setEnabled(False)

	"""
	Profile handling methods
	"""
	def renameProfile(self):
		originalText = self.profileComboBox.currentText()
		originalFileName = originalText + '.ini'

		renameDialog = QInputDialog()

		text, ok = renameDialog.getText(self.settingsWindow, 'Rename Profile',
			'Enter new profile name:', text=originalText, 
			flags=Qt.WindowCloseButtonHint)
		
		if ok and text != originalText:
			if self.checkExistingProfile(text) is False:
				for fname in os.listdir('./profiles'):
					if fname == originalFileName:
						os.rename(os.path.normpath('./profiles/' + fname), 
							(os.path.normpath('./profiles/' + text + '.ini')))

						self.refreshProfileList(text)

	def addProfile(self):
		addProfileDialog = QInputDialog()

		text, ok = addProfileDialog.getText(self.settingsWindow, 'Add Profile',
			'Please name new profile:', flags=Qt.WindowCloseButtonHint)

		if ok and text != None and self.checkExistingProfile(text) is False:
			self.defaultConfig(text)
			self.deleteProfileButton.setEnabled(True)

			self.refreshProfileList(text)

	def refreshProfileList(self, selected = None):
		print('refreshing profile list')

		self.findProfiles()
		self.profileComboBox.setCurrentIndex(
			self.profileComboBox.findText(selected))

	def deleteProfile(self):
		deleteProfileDialog = QMessageBox(self.settingsWindow)
		deleteProfileDialog.setWindowTitle('Delete Profile')

		deleteProfileDialog.setText("Are you sure you want to delete '" + 
			self.profileComboBox.currentText() + "'")

		deleteProfileDialog.setStandardButtons(
			QMessageBox.Yes | QMessageBox.No)
		deleteProfileDialog.setDefaultButton(QMessageBox.No)

		if (deleteProfileDialog.exec_() == QMessageBox.Yes):
			os.remove(os.path.normpath('./profiles/' + 
				self.profileComboBox.currentText()) + '.ini')

			self.profileComboBox.removeItem(
				self.profileComboBox.findText(
					self.profileComboBox.currentText()))
			self.disableDeleteButton()

			self.mainWindow.findProfiles()

	def saveProfile(self):
		profileName = self.profileComboBox.currentText()

		config = configparser.ConfigParser()
		config.read(os.path.normpath('./profiles/' + profileName + '.ini'))

		if platform.machine() == 'AMD64':
			config['System']['Architecture'] = '64'
		else:
			config['System']['Architecture'] = '32'

		config['System']['Threads'] = str(multiprocessing.cpu_count())

		config['Common']['EncodingMode'] = str(
			self.encodingModeComboBox.currentIndex())
		config['Common']['EncodingQuality'] = str(
			round(self.encodingModeValueDoubleSpinBox.value(), 1))

		config['Common']['Tuning'] = str(self.tuningComboBox.currentIndex())
		config['Common']['Preset'] = str(self.presetSlider.value())
		config['Common']['AVCProfile'] = str(
			self.AVCprofileComboBox.currentIndex())
		config['Common']['Level'] = str(self.levelComboBox.currentIndex())
		config['Common']['10BitDepth'] = str(self.bitDepthCheckBox.isChecked())
		config['Common']['QuickSettings'] = str(
			self.quickSettingsCheckBox.isChecked())

		config['Frame Type']['Deblocking'] = str(
			self.deblockingCheckBox.isChecked())
		config['Frame Type']['DeblockingStrength'] = str(
			self.deblockingStrSpinBox.value())
		config['Frame Type']['DeblockingThreshold'] = str(
			self.deblockingThresholdSpinBox.value())
		config['Frame Type']['GOPMaxSize'] = str(
			self.gopMaxSizeSpinBox.value())
		config['Frame Type']['GOPMinSize'] = str(
			self.gopMinSizeSpinBox.value())
		config['Frame Type']['BFrameWeighted'] = str(
			self.bframeWeightCheckBox.isChecked())
		config['Frame Type']['BFrameNumber'] = str(
			self.bframeNumberSpinBox.value())
		config['Frame Type']['BFrameBias'] = str(
			self.bframeBiasSpinBox.value())
		config['Frame Type']['BFrameAdaptive'] = str(
			self.bframeAdaptiveComboBox.currentIndex())
		config['Frame Type']['BFramePyramid'] = str(
			self.bframePyramidComboBox.currentIndex())
		config['Frame Type']['References'] = str(
			self.frameEncodingRefSpinBox.value())
		config['Frame Type']['SceneCut'] = str(
			self.frameEncodingSceneChangeSpinBox.value())

		config['Rate Control']['IframeQPMin'] = str(self.qpIMinSpinBox.value())
		config['Rate Control']['IframeQPMax'] = str(self.qpIMaxSpinBox.value())
		config['Rate Control']['PframeQPMin'] = str(self.qpPMinSpinBox.value())
		config['Rate Control']['PframeQPMax'] = str(self.qpPMaxSpinBox.value())
		config['Rate Control']['BframeQPMin'] = str(self.qpBMinSpinBox.value())
		config['Rate Control']['BframeQPMax'] = str(self.qpBMaxSpinBox.value())
		config['Rate Control']['QPStep'] = str(self.qpStepSpinBox.value())
		config['Rate Control']['QPComp'] = str(
			round(self.qCompSpinBox.value(), 2))
		config['Rate Control']['IPRatio'] = str(
			round(self.qpIPRatioSpinBox.value(), 2))
		config['Rate Control']['PBRatio'] = str(
			round(self.qpPBRatioSpinBox.value(), 2))
		config['Rate Control']['AQMode'] = str(
			self.aqModeComboBox.currentIndex())
		config['Rate Control']['AQStrength'] = str(
			round(self.aqStrengthSpinBox.value(), 1))
		config['Rate Control']['MBTree'] = str(self.mbTreeCheckBox.isChecked())
		config['Rate Control']['FrameLookahead'] = str(
			self.frameLookaheadSpinBox.value())

		config['Advanced']['MERange'] = str(self.meRangeSpinBox.value())
		config['Advanced']['MeMethod'] = str(
			self.meMethodComboBox.currentIndex())
		config['Advanced']['SubME'] = str(
			self.subPixelRefinementComboBox.currentIndex())
		config['Advanced']['MVPrediction'] = str(
			self.motionVectorPredictionComboBox.currentIndex())
		config['Advanced']['Trellis'] = str(
			self.trellisComboBox.currentIndex())
		config['Advanced']['PsyRDStr'] = str(
			round(self.psyrdStrengthSpinBox.value(), 1))
		config['Advanced']['PsyTrellisStr'] = str(
			round(self.psyTrellisStrengthSpinBox.value(), 1))
		config['Advanced']['FastPSkip'] = str(
			self.fastPSkipCheckBox.isChecked())
		config['Advanced']['Resize'] = str(self.resizeCheckBox.isChecked())
		config['Advanced']['ResizeMethod'] = str(
			self.resizeMethodComboBox.currentIndex())
		config['Advanced']['Width'] = str(self.resizeWidthSpinBox.value())
		config['Advanced']['Height'] = str(self.resizeHeightSpinBox.value())

		config['Misc']['AudioSource'] = str(
			self.audioSourceCheckBox.isChecked())
		config['Misc']['AudioQuality'] = str(
			round(self.audioQualitySpinBox.value(), 2))
		config['Misc']['CustomCmdLine'] = (
			self.customCmdLineTextEdit.toPlainText())

		self.updateCmdLineOutput(config)
		config['Misc']['CustomCmdLine'] = (
			self.customCmdLineTextEdit.toPlainText().strip())
		config['Misc']['CommandLineOutput'] = (
			self.cmdLineOutputTextBrowser.toPlainText())


		with open('./profiles/' + profileName + '.ini', 'w') as configfile:
			config.write(configfile)

		print(profileName + ' settings saved.')

	def findProfiles(self):
		self.profileComboBox.clear()
		for profile in os.listdir('./profiles'):
			if profile.endswith('.ini'):
				self.profileComboBox.addItem(profile[:-4])

	def checkExistingProfile(self, name):
		invalidFileNameDialog = QMessageBox(self.settingsWindow)

		if name == '':
			invalidFileNameDialog.setWindowTitle('Invalid Name')
			invalidFileNameDialog.setText('Profile names cannot be empty.')
			invalidFileNameDialog.exec_()
			return True

		for profile in os.listdir('./profiles'):
			if profile.endswith('.ini') and profile == name + '.ini':
				invalidFileNameDialog.setWindowTitle('Invalid Name')
				invalidFileNameDialog.setText('Profile names must be unique.')
				invalidFileNameDialog.exec_()
				return True

		return False


	"""
	Creates x264 cmd paramters by reading config file
	"""
	def updateCmdLineOutput(self, config):
		cmdOutput = ''

		if config.getint('System', 'Architecture') == 64:
			cmdOutput += 'x264_64'
		else:
			cmdOutput += 'x264_32'

		if self.bitDepthCheckBox.isChecked():
			cmdOutput += '_tMod-10bit-all.exe '
		else:
			cmdOutput += '_tMod-8bit-all.exe '

		cmdOutput += ('--threads ' + str(config.getint('System', 'Threads')) 
			+ ' ')

		cmdOutput += self.updateCommonCmdLine()

		if self.quickSettingsCheckBox.isChecked():
			cmdOutput += self.updateFrameTypeCmdLine()
			cmdOutput += self.updateRateControlCmdLine()
			cmdOutput += self.updateAdvancedCmdLine()

		self.cmdLineOutputTextBrowser.setText(cmdOutput)
		self.cmdLineDisplayTextBrowser.setText(cmdOutput + 
			config.get('Misc', 'customCmdLine'))

	def updateCommonCmdLine(self):
		cmdOutput = ''

		if not self.bitDepthCheckBox.isChecked():
			selection = self.AVCprofileComboBox.currentIndex()
			if selection != 2:
				if selection == 0:
					cmdOutput += '--profile baseline '
				elif selection == 1:
					cmdOutput += '--profile main '

		selection = self.presetSlider.value()
		if selection != 5:
			cmdOutput += '--preset '
			if selection == 0:
				cmdOutput += 'ultrafast '
			elif selection == 1:
				cmdOutput += 'superfast '
			elif selection == 2:
				cmdOutput += 'veryfast '
			elif selection == 3:
				cmdOutput += 'faster '
			elif selection == 4:
				cmdOutput += 'fast '
			elif selection == 6:
				cmdOutput += 'slow '
			elif selection == 7:
				cmdOutput += 'slower '
			elif selection == 8:
				cmdOutput += 'veryslow '
			elif selection == 9:
				cmdOutput += 'placebo '

		selection = self.levelComboBox.currentIndex()
		if selection != 0:
			cmdOutput += '--level '
			if selection == 1:
				cmdOutput += '1 '
			elif selection == 2:
				cmdOutput += '1b '
			elif selection == 3:
				cmdOutput += '1.1 '
			elif selection == 4:
				cmdOutput += '1.2 '
			elif selection == 5:
				cmdOutput += '1.3 '
			elif selection == 6:
				cmdOutput += '2 '
			elif selection == 7:
				cmdOutput += '2.1 '
			elif selection == 8:
				cmdOutput += '2.2 '
			elif selection == 9:
				cmdOutput += '3 '
			elif selection == 10:
				cmdOutput += '3.1 '
			elif selection == 11:
				cmdOutput += '3.2 '
			elif selection == 12:
				cmdOutput += '4 '
			elif selection == 13:
				cmdOutput += '4.1 '
			elif selection == 14:
				cmdOutput += '4.2 '
			elif selection == 15:
				cmdOutput += '5 '
			elif selection == 16:
				cmdOutput += '5.1 '
			elif selection == 17:
				cmdOutput += '5.2 '

		selection = self.tuningComboBox.currentIndex()
		if selection != 0:
			cmdOutput += '--tune '
			if selection == 1:
				cmdOutput += 'film '
			elif selection == 2:
				cmdOutput += 'animation '
			else:
				cmdOutput += 'grain '

		selection = round(self.encodingModeValueDoubleSpinBox.value(), 1)
		if selection != 23.0:
			if self.encodingModeComboBox.currentIndex() == 0:
				cmdOutput += ('--qp ' + str(round(selection, 0)) + ' ')
			else:
				cmdOutput += ('--crf ' + str(round(selection, 1)) + ' ')

		return cmdOutput

	def updateFrameTypeCmdLine(self):
		cmdOutput = ''

		selection = self.frameEncodingSceneChangeSpinBox.value()
		if selection != 40:
			cmdOutput += '--scenecut ' + str(selection) + ' '
		elif self.presetSlider.value() == 0:
			cmdOutput += '--scenecut ' + str(selection) + ' '

		selection = self.frameEncodingRefSpinBox.value()
		# if selection != 3:
		cmdOutput += '--ref ' + str(selection) + ' '

		selection = self.deblockingStrSpinBox.value()
		selection1 = self.deblockingThresholdSpinBox.value()
		if self.deblockingCheckBox.isChecked():
			if selection != 0 or selection1 != 0:
				cmdOutput += '--deblock '
				cmdOutput += str(selection) + ':' + str(selection1) + ' '
			elif self.tuningComboBox.currentIndex() != 0:
				cmdOutput += '--deblock '
				cmdOutput += str(selection) + ':' + str(selection1) + ' '
		else:
			cmdOutput += '--no-deblock '

		selection = self.gopMaxSizeSpinBox.value()
		if selection != 250:
			cmdOutput += '--keyint ' + str(selection) + ' '

		selection = self.gopMinSizeSpinBox.value()
		if selection != 0:
			cmdOutput += '--min-keyint ' + str(selection) + ' '

		selection = self.bframeNumberSpinBox.value()
		# if selection != 3:
		cmdOutput += '--bframes ' + str(selection) + ' '

		if selection != 0:
			selection1 = self.bframeAdaptiveComboBox.currentIndex()
			# if selection1 != 1:
			cmdOutput += '--b-adapt ' + str(selection1) + ' '

			selection1 = self.bframeBiasSpinBox.value()
			if selection1 != 0:
				cmdOutput += '--b-bias ' + str(selection1) + ' '

			selection1 = self.bframePyramidComboBox.currentIndex()
			if selection1 != 2:
				cmdOutput += '--b-pyramid '
				if selection1 == 0:
					cmdOutput += 'none '
				elif selection1 == 1:
					cmdOutput += 'strict '

		if not self.bframeWeightCheckBox.isChecked():
			cmdOutput += '--no-weightb '

		return cmdOutput

	def updateRateControlCmdLine(self):
		cmdOutput = ''

		if not self.mbTreeCheckBox.isChecked():
			cmdOutput += '--no-mbtree '

		selection = self.frameLookaheadSpinBox.value()
		# if selection != 40:
		cmdOutput += '--rc-lookahead ' + str(selection) + ' '

		selection = self.qpIMinSpinBox.value()
		selection1 = self.qpPMinSpinBox.value()
		selection2 = self.qpBMinSpinBox.value()
		if selection != 0 or selection1 != 0 or selection2 != 0:
			if selection == selection1 and selection1 == selection2:
				cmdOutput += '--qpmin ' + str(selection) + ' '
			else:
				cmdOutput += ('--qpmin ' + str(selection) + ':' + 
					str(selection1) + ':' + str(selection2) + ' ')

		selection = self.qpIMaxSpinBox.value()
		selection1 = self.qpPMaxSpinBox.value()
		selection2 = self.qpBMaxSpinBox.value()
		if selection != 81 or selection1 != 81 or selection2 != 81:
			if selection == selection1 and selection1 == selection2:
				cmdOutput += '--qpmax ' + str(selection) + ' '
			else:
				cmdOutput += ('--qpmax ' + str(selection) + ':' + 
					str(selection1) + ':' + str(selection2) + ' ')

		selection = self.qpStepSpinBox.value()
		if selection != 4:
			cmdOutput += '--qpstep ' + str(selection) + ' '

		selection = round(self.qCompSpinBox.value(), 2)
		if selection != 0.60:
			cmdOutput += '--qcomp ' + str(selection) + ' '
		elif self.tuningComboBox.currentIndex() == 3:
			cmdOutput += '--qcomp ' + str(selection) + ' '

		selection = round(self.qpIPRatioSpinBox.value(), 2)
		selection1 = self.tuningComboBox.currentIndex()

		if selection != 1.40:
			cmdOutput += '--ipratio ' + str(selection) + ' '
		elif selection1 == 3:
			cmdOutput += '--ipratio ' + str(selection) + ' '

		selection = round(self.qpPBRatioSpinBox.value(), 2)
		if selection != 1.30:
			cmdOutput += '--pbratio ' + str(selection) + ' '
		elif selection1 == 3:
			cmdOutput += '--pbratio ' + str(selection) + ' '

		selection = self.aqModeComboBox.currentIndex()
		if selection != 1:
			cmdOutput += '--aq-mode ' + str(selection) + ' '
		elif self.presetSlider.value() == 0:
			cmdOutput += '--aq-mode ' + str(selection) + ' '

		selection = round(self.aqStrengthSpinBox.value(), 1)
		if selection != 1.0:
			cmdOutput += '--aq-strength ' + str(selection) + ' '
		elif selection1 != 0:
			cmdOutput += '--aq-strength ' + str(selection) + ' '

		return cmdOutput

	def updateAdvancedCmdLine(self):
		cmdOutput = ''

		selection = self.meMethodComboBox.currentIndex()
		if selection == 0:
			cmdOutput += '--me dia '
		if selection == 1:
			cmdOutput += '--me hex '
		if selection == 2:
			cmdOutput += '--me umh '
		if selection == 3:
			cmdOutput += '--me esa '
		if selection == 4:
			cmdOutput += '--me tesa '

		selection = self.meRangeSpinBox.value()
		if selection != 16:
			cmdOutput += '--merange ' + str(selection) + ' '
		elif self.presetSlider.value() >= 8:
			cmdOutput += '--merange ' + str(selection) + ' '

		selection = self.motionVectorPredictionComboBox.currentIndex()
		if selection != 1:
			if selection == 0:
				cmdOutput += '--direct none '
			if selection == 2:
				cmdOutput += '--direct temporal '
			if selection == 3:
				cmdOutput += '--direct auto '
		elif self.presetSlider.value() >= 6:
			cmdOutput += '--direct spatial '

		selection = self.subPixelRefinementComboBox.currentIndex()
		# if selection != 7:
		cmdOutput += '--subme ' + str(selection) + ' '

		selection1 = self.trellisComboBox.currentIndex()
		# if selection1 != 1:
		cmdOutput += '--trellis ' + str(selection1) + ' '

		selection1 = round(self.psyrdStrengthSpinBox.value(), 1)
		selection2 = round(self.psyTrellisStrengthSpinBox.value(), 1)
		if selection >= 6:
			if selection1 != 1.0 or selection2 != 0.0:
				cmdOutput += ('--psy-rd ' + str(selection1) + ':' + 
					str(selection2) + ' ')
			elif self.tuningComboBox.currentIndex() != 0:
				cmdOutput += ('--psy-rd ' + str(selection1) + ':' + 
					str(selection2) + ' ')

		if not self.fastPSkipCheckBox.isChecked():
			cmdOutput += '--no-fast-pskip '

		if self.resizeCheckBox.isChecked():
			cmdOutput += ('--video-filter resize:width=' + 
				str(self.resizeWidthSpinBox.value()) + ',height=' +
				str(self.resizeHeightSpinBox.value()))

			if self.resizeMethodComboBox.currentIndex() != 2:
				cmdOutput += (',method=' + 
					self.resizeMethodComboBox.currentText())

			cmdOutput += ' '

		return cmdOutput


	"""
	Profile default creation method
	"""
	def defaultConfig(self, profileName):
		config = configparser.ConfigParser()
		config.read(os.path.normpath('./profiles/' + profileName + '.ini'))

		config['System'] = {}

		config['System']['Threads'] = str(multiprocessing.cpu_count())

		config['Common'] = {}
		config['Common']['EncodingMode'] = '1'
		config['Common']['EncodingQuality'] = '23.0'
		config['Common']['Tuning'] = '0'
		config['Common']['Preset'] = '5'
		config['Common']['AVCProfile'] = '2'
		config['Common']['Level'] = '0'
		config['Common']['10BitDepth'] = 'False'
		config['Common']['QuickSettings'] = 'False'

		config['Frame Type'] = {}
		config['Frame Type']['Deblocking'] = 'True'
		config['Frame Type']['DeblockingStrength'] = '0'
		config['Frame Type']['DeblockingThreshold'] = '0'
		config['Frame Type']['GOPMaxSize'] = '250'
		config['Frame Type']['GOPMinSize'] = '0'
		config['Frame Type']['BFrameWeighted'] = 'True'
		config['Frame Type']['BFrameNumber'] = '3'
		config['Frame Type']['BFrameBias'] = '0'
		config['Frame Type']['BFrameAdaptive'] = '1'
		config['Frame Type']['BFramePyramid'] = '2'
		config['Frame Type']['References'] = '3'
		config['Frame Type']['SceneCut'] = '40'

		config['Rate Control'] = {}
		config['Rate Control']['IframeQPMin'] = '0'
		config['Rate Control']['PframeQPMin'] = '0'
		config['Rate Control']['BframeQPMin'] = '0'
		config['Rate Control']['IframeQPMax'] = '81'
		config['Rate Control']['PframeQPMax'] = '81'
		config['Rate Control']['BframeQPMax'] = '81'
		config['Rate Control']['QPStep'] = '4'
		config['Rate Control']['QPComp'] = '0.60'
		config['Rate Control']['IPRatio'] = '1.40'
		config['Rate Control']['PBRatio'] = '1.30'
		config['Rate Control']['AQMode'] = '1'
		config['Rate Control']['AQStrength'] = '1.0'
		config['Rate Control']['MBTree'] = 'True'
		config['Rate Control']['FrameLookahead'] = '40'

		config['Advanced'] = {}
		config['Advanced']['MERange'] = '16'
		config['Advanced']['MEMethod'] = '1'
		config['Advanced']['SubME'] = '7'
		config['Advanced']['MVPrediction'] = '1'
		config['Advanced']['Trellis'] = '1'
		config['Advanced']['PsyRDStr'] = '1.0'
		config['Advanced']['PsyTrellisStr'] = '0.0'
		config['Advanced']['FastPSkip'] = 'True'
		config['Advanced']['Resize'] = 'False'
		config['Advanced']['ResizeMethod'] = '2'
		config['Advanced']['Width'] = '1280'
		config['Advanced']['Height'] = '720'

		config['Misc'] = {}
		config['Misc']['AudioSource'] = 'True'
		config['Misc']['AudioQuality'] = '0.5'
		config['Misc']['CustomCmdLine'] = ''

		if platform.machine() == 'AMD64':
			config['System']['Architecture'] = '64'
			config['Misc']['CommandLineOutput'] = 'x264_64'
		else:
			config['System']['Architecture'] = '32'
			config['Misc']['CommandLineOutput'] = 'x264_32'

		config['Misc']['CommandLineOutput'] += ('_tMod-8bit-all.exe ' +
				'--threads ' + str(config.getint('System', 'Threads')))

		with open('./profiles/' + profileName + '.ini', 'w') as configfile:
			config.write(configfile)