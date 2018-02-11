from PyQt5 import uic

fp = open('gyro_ui.py', "w", encoding="utf-8")
uic.compileUi('gyro.ui', fp)
fp.close()
