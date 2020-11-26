import os
import sys

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PIL import Image

filters = {
    "Hamming": Image.HAMMING,
    "Nearest Neighbor": Image.NEAREST,
    "Box": Image.BOX,
    "Bilinear": Image.BILINEAR,
    "Bicubic": Image.BICUBIC,
    "Lanczos": Image.LANCZOS
}


class ImageLabel(QLabel):
    def __init__(self):
        super().__init__()

        self.setAlignment(Qt.AlignCenter)
        self.setText('\n\n Drop Image Here \n\n')
        self.setStyleSheet('''
            QLabel{
                border: 4px dashed #aaa
            }
        ''')

    def setPixmap(self, image):
        super().setPixmap(image)


class ResizeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(400, 400)
        self.setAcceptDrops(True)
        self.selected_image_filter = Image.HAMMING

        mainLayout = QVBoxLayout()


        self.photoViewer = ImageLabel()

        self.label = QLabel()
        self.label.setFixedHeight(15)
        self.label.setText('Image Filtering Technique')
        self.label.setAlignment(Qt.AlignCenter)

        self.cb = QComboBox()
        self.cb.addItems(filters.keys())
        self.cb.currentIndexChanged.connect(self.selectionChange)
        self.label.setBuddy(self.cb)
        self.setLayout(mainLayout)

        mainLayout.addWidget(self.photoViewer)
        mainLayout.addWidget(self.label)
        mainLayout.addWidget(self.cb)

    def selectionChange(self):
        self.selected_image_filter = filters.get(self.cb.currentText())
    def dragEnterEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasImage:
            event.setDropAction(Qt.CopyAction)
            file_path = event.mimeData().urls()[0].toLocalFile()
            self.resize_save_image(file_path)

            event.accept()
        else:
            event.ignore()

    def resize_save_image(self, file_path):
        original_image = QPixmap(file_path)
        self.photoViewer.setPixmap(original_image)

        file_directory = os.path.dirname(file_path)
        base_file_parts = os.path.basename(file_path).rsplit('.')

        for size in [56, 28]:
            new_image = original_image.scaled(size, size, QtCore.Qt.KeepAspectRatio)
            if len(base_file_parts) == 2:
                updated_file_name = f'{base_file_parts[0]}{str(size)}.{base_file_parts[1]}'
            else:
                updated_file_name = f'{base_file_parts[0]}{str(size)}'
            new_file_path = os.path.join(file_directory, updated_file_name)
            new_image.save(new_file_path)


app = QApplication(sys.argv)
resize_app = ResizeApp()
resize_app.setWindowTitle("Emote Resizer")
resize_app.show()
sys.exit(app.exec_())
