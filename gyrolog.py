#!/usr/bin/python
# -*- coding: utf-8 -*-

# GAUL 2017 - Phil

import os, sys
from datetime import *

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.Qt3DCore import *
from PyQt5.Qt3DExtras import *
from PyQt5.Qt3DInput import *
from PyQt5.Qt3DRender import *

from gyro_ui import *
from gyrofile import *


class GyroWorker(QObject):
	tickSignal = pyqtSignal(GyroTick)
	tickIndex = 0
	tickStart = None
	tickCurr = None
	startTime = None

	def __init__(self, parent):
		super(GyroWorker, self).__init__()
		parent.jumpSignal.connect(self.jump)
		parent.stopSignal.connect(self.stop)
		self.gyroLog = parent.gyroLog
		self.timer = QTimer(self)
		self.timer.timeout.connect(self.iter)

	def start(self):
		self.timer.stop()
		self.tickStart = self.gyroLog.tickList[self.tickIndex]
		self.tickCurr = self.tickStart
		self.timer.start(999999)
		self.startTime = datetime.now()
		self.iter()

	@pyqtSlot()
	def iter(self):
		self.tickSignal.emit(self.tickCurr)
		stepTime = (datetime.now() - self.startTime).total_seconds() + self.tickStart.time
		self.tickCurr = self.gyroLog.seekTimeFwd(stepTime, self.tickCurr)

		if self.tickCurr is not None:
			self.timer.setInterval(max(0, self.tickCurr.time - stepTime) * 1000)
		else:
			self.timer.stop()

	@pyqtSlot()
	def stop(self):
		self.timer.stop()

	@pyqtSlot(int, bool)
	def jump(self, tickIndex:int, start:bool=False):
		self.tickIndex = tickIndex

		if start:
			self.start()
		else:
			self.tickSignal.emit(self.gyroLog.tickList[tickIndex])


"""
class RocketZoom(QObject):
	def __init__(self, camera):
		super(RocketZoom, self).__init__()
		self.camera = camera

	def eventFilter(self, obj, event):
		if event.type() == QEvent.Wheel:
			delta = event.angleDelta().y() / -20.0
			lens = self.camera.lens()
			fov = lens.fieldOfView()
			newFov = min(max(fov + delta, 20.0), 120.0)
			lens.setFieldOfView(newFov)
			return True
		return False
"""


class RocketView3D(Qt3DWindow):
	def wheelEvent(self, event:QWheelEvent):
		delta = event.angleDelta().y() / -20.0
		lens = self.camera().lens()
		fov = lens.fieldOfView()
		newFov = min(max(fov + delta,20.0),120.0)
		lens.setFieldOfView(newFov)


def formatTClock(t:float):
	s, ms = divmod(abs(t) * 1000.0, 1000.0)
	m, s = divmod(s, 60.0)
	h, m = divmod(m, 60.0)
	return "T%s%02d:%02d:%02d.%03d" % ("+-"[t<0], h, m, s, ms)


class GyroApp(QWidget, Ui_Form):
	jumpSignal = pyqtSignal(int, bool)
	stopSignal = pyqtSignal()
	currTick = None
	play = False

	def __init__(self, parent=None):
		QWidget.__init__(self)
		self.setupUi(parent)

		parent.setWindowIcon(QIcon("img/GAUL_logo_mini.png"))

		launchTimeFont = self.labelLaunchTime.font()
		launchTimeFont.setFamily("Monospace")
		launchTimeFont.setStyleHint(QFont.TypeWriter)
		self.labelLaunchTime.setFont(launchTimeFont)

		view3D = self.view3D = RocketView3D()
		view3D.renderSettings().setRenderPolicy(QRenderSettings.OnDemand)
		viewContainer = self.viewContainer = QWidget.createWindowContainer(view3D)

		self.horizontalLayout.addWidget(viewContainer)
		self.viewScene, self.rocketTransform = createScene()

		# Camera
		viewCam = self.viewCam = view3D.camera()
		viewCam.lens().setPerspectiveProjection(50.0, 16.0 / 9.0, 0.1, 1000.0)
		viewCam.setPosition(QVector3D(30.0, 30.0, -30.0))
		viewCam.setViewCenter(QVector3D(0.0, 0.0, 0.0))

		# Camera controls
		camCtrl = self.viewCamCtrl = QOrbitCameraController(self.viewScene)
		camCtrl.setLinearSpeed(0)
		camCtrl.setLookSpeed(-200.0)
		camCtrl.setCamera(self.viewCam)

		view3D.setRootEntity(self.viewScene)
		#view3D.installEventFilter(RocketZoom(viewCam))
		view3D.show()

		self.gyroLog = GyroLog('blackbird.csv')

		gyroThread = self.gyroThread = QThread()
		gyroWorker = self.gyroWorker = GyroWorker(self)
		gyroWorker.moveToThread(gyroThread)
		gyroWorker.tickSignal.connect(self.updateTickInfo)
		gyroThread.start()

		self.seekBar.isPressed = False
		self.seekBar.setMaximum(len(self.gyroLog.tickList) - 1)
		self.seekBar.sliderPressed.connect(self.seekBarPressed)
		self.seekBar.sliderReleased.connect(self.seekBarReleased)
		self.seekBar.valueChanged.connect(self.refreshTick)

		self.playButton.pressed.connect(self.playButtonPressed)
		self.refreshTick()


	@pyqtSlot(GyroTick)
	def updateTickInfo(self, tick:GyroTick):
		self.rocketTransform.setRotation(QQuaternion.fromEulerAngles(tick.getAngX() - 90, tick.getAngY(), tick.getAngZ()))
		self.currTick = tick

		if not self.seekBar.isPressed :
			blocked = self.seekBar.blockSignals(True)
			self.seekBar.setValue(tick.listIndex)
			self.seekBar.blockSignals(blocked)

		self.lcdAlt.display(tick.altitude)

		self.lcdRx.display(tick.getAngX())
		self.lcdRy.display(tick.getAngY())
		self.lcdRz.display(tick.getAngZ())

		self.lcdRSx.display(tick.angSpeedX)
		self.lcdRSy.display(tick.angSpeedY)
		self.lcdRSz.display(tick.angSpeedZ)

		self.lcdTick.display(tick.listIndex)
		self.labelLaunchTime.setText(formatTClock(tick.time))


	@pyqtSlot()
	def playButtonPressed(self):
		self.play = not self.play
		self.playButton.setIcon(QIcon("img/pause-icon-2.png" if self.play else "img/play-icon-2.png"))

		if self.play:
			self.refreshTick()
		else:
			self.stopSignal.emit()

	@pyqtSlot()
	def seekBarPressed(self):
		self.stopSignal.emit()
		self.seekBar.isPressed = True

	@pyqtSlot()
	def seekBarReleased(self):
		self.seekBar.isPressed = False
		self.refreshTick()

	@pyqtSlot()
	def refreshTick(self):
		self.jumpSignal.emit(self.seekBar.value(), self.play and not self.seekBar.isPressed)


def createScene():
	rootEntity = QEntity()

	# Full bright (shadeless)
	#rocketMaterial.setAmbient(Qt.red)
	#rocketMaterial.setDiffuse(Qt.red)
	#rocketMaterial.setShininess(0)

	rocketEntity = QEntity(rootEntity)
	rocketMesh = QMesh()
	rocketMesh.setSource(QUrl.fromLocalFile('menhir/m4.obj'))

	rocketTransform = QTransform()

	rocketMaterial = QDiffuseMapMaterial(rootEntity)
	rocketTexture = QTextureImage()
	rocketTexture.setSource(QUrl.fromLocalFile('menhir/m4.png'))
	rocketMaterial.diffuse().addTextureImage(rocketTexture)
	rocketMaterial.setShininess(2.0)
	rocketMaterial.setAmbient(QColor.fromRgbF(0.5, 0.5, 0.5, 1.0))

	rocketEntity.addComponent(rocketMesh)
	rocketEntity.addComponent(rocketTransform)
	rocketEntity.addComponent(rocketMaterial)

	xBarEntity = QEntity(rootEntity)
	xBarMesh = QCylinderMesh()
	xBarMesh.setLength(50)
	xBarMesh.setRadius(0.1)
	xBarMesh.setSlices(4)
	xBarTransform = QTransform()
	xBarTransform.setRotation(QQuaternion.fromEulerAngles(0, 0, 90))
	xBarTransform.setTranslation(QVector3D(xBarMesh.length() / 2, 0, 0))
	xBarMaterial = QPhongMaterial(rootEntity)
	xBarMaterial.setAmbient(Qt.red)
	xBarMaterial.setDiffuse(Qt.red)
	xBarMaterial.setShininess(0)
	xBarEntity.addComponent(xBarMesh)
	xBarEntity.addComponent(xBarTransform)
	xBarEntity.addComponent(xBarMaterial)

	yBarEntity = QEntity(rootEntity)
	yBarMesh = QCylinderMesh()
	yBarMesh.setLength(50)
	yBarMesh.setRadius(0.1)
	yBarMesh.setSlices(4)
	yBarTransform = QTransform()
	yBarTransform.setRotation(QQuaternion.fromEulerAngles(90, 0, 0))
	yBarTransform.setTranslation(QVector3D(0, 0, -yBarMesh.length() / 2))
	yBarMaterial = QPhongMaterial(rootEntity)
	yBarMaterial.setAmbient(Qt.green)
	yBarMaterial.setDiffuse(Qt.green)
	yBarMaterial.setShininess(0)
	yBarEntity.addComponent(yBarMesh)
	yBarEntity.addComponent(yBarTransform)
	yBarEntity.addComponent(yBarMaterial)

	zBarEntity = QEntity(rootEntity)
	zBarMesh = QCylinderMesh()
	zBarMesh.setLength(50)
	zBarMesh.setRadius(0.1)
	zBarMesh.setSlices(4)
	zBarTransform = QTransform()
	zBarTransform.setTranslation(QVector3D(0, zBarMesh.length() / 2, 0))
	zBarMaterial = QPhongMaterial(rootEntity)
	zBarMaterial.setAmbient(Qt.blue)
	zBarMaterial.setDiffuse(Qt.blue)
	zBarMaterial.setShininess(0)
	zBarEntity.addComponent(zBarMesh)
	zBarEntity.addComponent(zBarTransform)
	zBarEntity.addComponent(zBarMaterial)

	return rootEntity, rocketTransform

###

os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
app = QApplication(sys.argv)
mainWindow = QWidget()
appClass = GyroApp(mainWindow)
mainWindow.show()
sys.exit(app.exec_())
