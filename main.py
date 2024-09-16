import sys
from PySide6.QtWidgets import QApplication
from AppFile.singleton import SingletonMainWin


WIN_WIDTH = 2280
WIN_HEIGHT = 1520


def run():
    app = QApplication(sys.argv)

    win = SingletonMainWin(app)
    win.resize(WIN_WIDTH, WIN_HEIGHT)
    win.showMaximized()

    app.exec()


if __name__ == '__main__':
    run()
