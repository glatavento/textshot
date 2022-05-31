#!/usr/bin/env python3
import io
import sys
import argparse
from typing import Optional

import pyperclip
from PIL import Image
from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QPixmap

from ocr_wrapper import OcrWrapper, BACKENDS, DEFAULT_BACKEND
from ui import Snipper, notify


class App(QtWidgets.QApplication):
    def __init__(self, lang: Optional[str], ocr_handler: OcrWrapper):
        super().__init__(sys.argv)
        self.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)
        self.lang = lang
        self.ocr_handler = ocr_handler
        if not self.ocr_handler.is_available():
            notify(f"OCR backend {self.ocr_handler.get_name()} not available", level="ERROR")
            self.quit()
            quit(1)

        self._main_window = QtWidgets.QMainWindow()
        self.snipper = Snipper(self._main_window)

        self.snipper.shot_signal.connect(self.onShot)
        self.snipper.quit_signal.connect(self.onQuit)

        self.snipper.show()

    @QtCore.Slot(QPixmap)
    def onShot(self, shot: QPixmap) -> None:
        self.snipper.hide()

        buffer = QtCore.QBuffer()
        buffer.open(QtCore.QBuffer.ReadWrite)
        shot.save(buffer, "PNG")
        buffer.close()
        image = Image.open(io.BytesIO(buffer.data()))
        image.save("shot.png")

        try:
            result = self.ocr_handler.process_image(image, self.lang)
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
    def onQuit(self) -> None:
        self.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='OCR Snipper')
    parser.add_argument('-l', '--lang', nargs='*', help='Language to use for OCR')
    parser.add_argument('-b', '--backend', nargs='?', help='Backend to use for OCR')
    Backend = BACKENDS.get(parser.parse_args().backend)
    if not Backend:
        available_backends = [b for b in BACKENDS.values() if b.is_available()]
        if not available_backends:
            print("ERROR: No backends available")
            quit(1)
        elif DEFAULT_BACKEND.is_available():
            Backend = DEFAULT_BACKEND
        else:
            Backend = available_backends[0]
    args = parser.parse_args()
    app = App(args.lang, Backend())
    app.exec()
