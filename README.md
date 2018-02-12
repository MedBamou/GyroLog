# GyroLog

A simple PyQt3D app I originally wrote to display the data collected by the optical fiber gyroscope from the Menhir rocket, [launched](https://www.youtube.com/watch?v=VAV17hzAZ-k) by the [Groupe Aérospatial de l'Université Laval](https://www.facebook.com/groupeaerospatialul/) at [Spaceport America Cup](https://www.spaceportamericacup.com/) 2017. It's not very well optimized but it does the job. All axes follow the right-hand rule.

Unfortunately, the laser power system failed at ignition due to a blown MOSFET, so we did not manage to record flight data, but the rocket launched and landed fine. The app instead reads the log file from our Blackbird rocket launched in 2015, which was recorded by a commercial electronic gyroscope.

![screenshot](https://user-images.githubusercontent.com/1380241/36082161-b0865056-0f74-11e8-850b-04cf99390773.png)

How to run: `python gyrolog.py` then press the play button bottom-right, right-click to rotate, scroll to zoom.

Recommended distribution: [WinPython 3.6+ Qt5](https://winpython.github.io/)

Required:

	Python 3
	pyqt5 (5.8+)
	pyqt3d (5.8+)

This project is licensed under the [GNU GPL v3](http://tldrlegal.com/l/gpl-3.0). Copyright © 2016 - 2018 AgentRev
