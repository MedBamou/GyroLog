#!/usr/bin/python
# -*- coding: utf-8 -*-

# GAUL 2017 - Phil

import csv


class GyroTick:
	launchTime = 865.9
	angSpeedX_calibrate = -0.03
	angSpeedY_calibrate = 0.02
	angSpeedZ_calibrate = 0.09

	angX = 0.0
	angY = 0.0
	angZ = 0.0
	listIndex = 0

	@staticmethod
	def clampAngle(ang):
		ang = ((ang % 360) + 360) % 360
		return (ang if ang <= 180 else ang - 360)

	def getAngX(self):
		return self.clampAngle(self.angX)

	def getAngY(self):
		return self.clampAngle(self.angY)

	def getAngZ(self):
		return self.clampAngle(self.angZ)

	def __init__(self, csvRow):
		self.time = float(csvRow[0]) - self.launchTime
		self.angSpeedX = float(csvRow[1]) + self.angSpeedX_calibrate
		self.angSpeedY = float(csvRow[2]) + self.angSpeedY_calibrate
		self.angSpeedZ = float(csvRow[3]) + self.angSpeedZ_calibrate
		self.accelX = float(csvRow[4])
		self.accelY = float(csvRow[5])
		self.accelZ = float(csvRow[6])
		self.magnetX = float(csvRow[7])
		self.magnetY = float(csvRow[8])
		self.magnetZ = float(csvRow[9])
		self.altitude = float(csvRow[10])
		self.latitude = float(csvRow[11])
		self.longitude = float(csvRow[12])
		self.state = int(csvRow[13])


class GyroLog:
	tickList = []

	_fieldNames = ['time','angSpeedX','angSpeedY','angSpeedZ','accelX','accelY','accelZ','magnetX','magnetY','magnetZ','altitude','latitude','longitude','state']
	_csvDialect = csv.Sniffer().sniff(','.join(_fieldNames))

	def __init__(self, csvPath):
		with open(csvPath,'r') as csvFile:
			csvReader = csv.reader(csvFile, dialect=self._csvDialect) #fieldnames=fieldNames,
			next(csvReader, None)

			for row in csvReader:
				oTickCurr = GyroTick(row)

				if self.tickList:
					oTickPrev = self.tickList[-1]
				else:
					oTickPrev = oTickCurr

				self.tickList.append(oTickCurr)
				oTickCurr.listIndex = len(self.tickList) - 1

				# compute angle values via midpoint Riemann sum (dead reckoning)
				fTimespan = oTickCurr.time - oTickPrev.time
				oTickCurr.angX = oTickPrev.angX + fTimespan * (oTickPrev.angSpeedX + oTickCurr.angSpeedX) / 2
				oTickCurr.angY = oTickPrev.angY + fTimespan * (oTickPrev.angSpeedY + oTickCurr.angSpeedY) / 2
				oTickCurr.angZ = oTickPrev.angZ + fTimespan * (oTickPrev.angSpeedZ + oTickCurr.angSpeedZ) / 2


	def seekTime(self, fTime, iTickStart=0, iTickEnd=0):
		if iTickEnd <= 0:
			iTickEnd = len(self.tickList)

		iTickMid = iTickStart + ((iTickEnd - iTickStart) // 2)

		# Find closest tick by recursive approximation
		for tickRange in [[iTickStart,iTickMid],[iTickMid+1,iTickEnd]]:
			iTick1 = tickRange[0]
			iTick2 = tickRange[1]
			oTick1 = self.tickList[iTick1]
			oTick2 = self.tickList[iTick2]

			if iTick1 == iTick2:
				return oTick1 # found closest
			elif oTick1.time <= fTime <= oTick2.time:
				return self.seekTime(fTime, iTick1, iTick2)

	def seekNextTick(self, oTick):
		if oTick.listIndex == len(self.tickList) - 1:
			return None
		return self.tickList[oTick.listIndex + 1]

	def seekTimeFwd(self, fTime, oTickStart=None):
		if not oTickStart:
			oTickStart = self.tickList[0]

		oTickCurr = None
		oTickNext = oTickStart

		while oTickNext is not None and (oTickNext.time < fTime or oTickCurr is None):
			oTickCurr = oTickNext
			oTickNext = self.seekNextTick(oTickCurr)

		return oTickNext
