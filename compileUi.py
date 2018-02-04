from PyQt5 import uic

fp = open('gyroUi.py', "w", encoding="utf-8")
uic.compileUi('gyro.ui', fp)
fp.close()
