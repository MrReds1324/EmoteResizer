import sys
from os import path
from time import sleep

from PIL import Image
from PyQt5.QtCore import Qt, QRunnable, pyqtSlot, QThreadPool
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QComboBox

filters = {
    "Hamming": Image.HAMMING,
    "Nearest Neighbor": Image.NEAREST,
    "Box": Image.BOX,
    "Bilinear": Image.BILINEAR,
    "Bicubic": Image.BICUBIC,
    "Lanczos": Image.LANCZOS
}

imageTypes = ['Emote', 'Badge']

# Implements a Worker object that will control resizing and saving images to disk
# This enables us to show which image is currently being resized and saved as it does not block the main GUI thread
class Worker(QRunnable):
    def __init__(self, photo_viewer, urls, selected_image_filter, selected_image_type, *args, **kwargs):
        super(Worker, self).__init__()
        self.selected_image_filter = selected_image_filter
        self.photo_viewer = photo_viewer
        self.urls = urls
        self.selected_image_type = selected_image_type

    @pyqtSlot()
    def run(self):
        for url in self.urls:
            # Treat each url as a local path
            file_path = url.toLocalFile()
            # Open the image as an Pillow Image - this allows us the best photo manipulation
            im = Image.open(file_path)
            # Set the image label with the image
            self.photo_viewer.setPixmap(QPixmap(file_path))

            file_directory = path.dirname(file_path)
            base_file_parts = path.basename(file_path).rsplit('.')

            if self.selected_image_type == 'Emote':
                sizes = [56, 28]
            else:
                sizes = [36, 18]

            for size in sizes:
                # Rebuild basename with image size appended to the end
                if len(base_file_parts) == 2:
                    updated_file_name = f'{base_file_parts[0]}{str(size)}.{base_file_parts[1]}'
                else:
                    updated_file_name = f'{base_file_parts[0]}{str(size)}'
                new_file_path = path.join(file_directory, updated_file_name)

                try:
                    im.copy().resize((size, size), self.selected_image_filter).save(new_file_path)
                except Exception as e:
                    print(e)

            # Sleep to allow time for the image to show on screen
            sleep(1)
        # Reset the text once all photos are finished
        self.photo_viewer.setText('\n\n Drop Image Here \n\n')


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
        self.selected_image_type = imageTypes[0]
        mainLayout = QVBoxLayout()

        self.threadpool = QThreadPool()

        self.photoViewer = ImageLabel()

        self.label = QLabel()
        self.label.setFixedHeight(15)
        self.label.setText('Image Filtering Technique')
        self.label.setAlignment(Qt.AlignCenter)

        self.cb = QComboBox()
        self.cb.addItems(filters.keys())
        self.cb.currentIndexChanged.connect(self.selectionChange)


        self.labelImageType = QLabel()
        self.labelImageType.setFixedHeight(16)
        self.labelImageType.setText('Badge or Emote')
        self.labelImageType.setAlignment(Qt.AlignCenter)

        self.imageType = QComboBox()
        self.imageType.addItems(imageTypes)
        self.imageType.currentIndexChanged.connect(self.selectionChangeEmote)

        self.labelImageType.setBuddy(self.imageType)
        self.setLayout(mainLayout)

        mainLayout.addWidget(self.photoViewer)
        mainLayout.addWidget(self.label)
        mainLayout.addWidget(self.cb)
        mainLayout.addWidget(self.labelImageType)
        mainLayout.addWidget(self.imageType)

    def selectionChange(self):
        self.selected_image_filter = filters.get(self.cb.currentText())

    def selectionChangeEmote(self):
        self.selected_image_type = self.imageType.currentText()

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
            worker = Worker(self.photoViewer, event.mimeData().urls(), self.selected_image_filter, self.selected_image_type)
            self.threadpool.start(worker)

            event.accept()
        else:
            event.ignore()

    # Clear and wait for the threadpool to finish before exiting
    def closeEvent(self, event):
        self.threadpool.clear()
        self.threadpool.waitForDone()

app = QApplication(sys.argv)
resize_app = ResizeApp()
resize_app.setWindowTitle("Emote Resizer")
resize_app.show()
sys.exit(app.exec_())
