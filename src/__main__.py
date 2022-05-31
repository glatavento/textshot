#!/usr/bin/env python3
import io
import sys
from typing import Optional

import pyperclip
from PIL import Image
from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QPixmap

from ocr_handler import processImage
from ui import Snipper, notify


class App(QtWidgets.QApplication):
    def __init__(self, lang: Optional[str] = None):
        super().__init__(sys.argv)
        self.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)
        self.lang = lang

        self._main_window = QtWidgets.QMainWindow()
        self.snipper = Snipper(self._main_window)

        self.snipper.shot_signal.connect(self.onShot)
        self.snipper.quit_signal.connect(self.onQuit)

        self.snipper.show()

    @QtCore.Slot(QPixmap)
    def onShot(self, shot: QPixmap):
        self.snipper.hide()

        buffer = QtCore.QBuffer()
        buffer.open(QtCore.QBuffer.ReadWrite)
        shot.save(buffer, "PNG")
        buffer.close()
        image = Image.open(io.BytesIO(buffer.data()))
        image.save("shot.png")

        try:
            result = processImage(image, lang=self.lang)
        except RuntimeError as error:
            notify(f"An error occurred when trying to process the image: {error}", level="ERROR")
        else:
            if result:
                pyperclip.copy(result)
                notify(f'Copied \n"{result}"\n to the clipboard')
            else:
                notify(f"Unable to read text from image, did not copy")
        self.quit()

    @QtCore.Slot()
    def onQuit(self):
        self.quit()


if __name__ == "__main__":
    app = App()
    app.exec()
