# GyroLog

A simple PyQt3D app I wrote to display the data collected by the optical fiber gyroscope from the Menhir rocket, launched by the [Groupe Aérospatial de l'Université Laval](https://www.facebook.com/groupeaerospatialul/) at Spaceport America Cup 2017. It's not very well optimized and there's a lot of commented code, but it does the job.

Unfortunately, the laser power system failed at ignition due to a blown MOSFET, so we did not manage to record flight data, but the rocket launched and landed fine. The app instead reads the log file from our Blackbird rocket launched in 2015, which was recorded by a commercial electronic gyroscope.

---

How to run: `python main.py` then press the play button bottom-right
Recommended distribution: WinPython3 Qt5
Required:

	python3
	pyqt5 (v5.8+)
	pyqt3d (v5.8+)

---

This project is licensed under the [GNU GPL v3](http://tldrlegal.com/l/gpl-3.0). Copyright © 2017 - 2018 AgentRev
