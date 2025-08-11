import sys
from PyQt5.QtWidgets import QApplication
from ui import ReactorSimulatorWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    sim = ReactorSimulatorWindow()
    sim.show()
    sys.exit(app.exec_())
