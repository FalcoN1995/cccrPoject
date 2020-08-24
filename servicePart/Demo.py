import sys, os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QUrl
from PIL import Image
from reportlab.pdfgen import canvas
from PyPDF3 import PdfFileReader, PdfFileWriter


class ListBoxWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.resize(600, 600)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()

            links = []

            for url in event.mimeData().urls():
                if url.isLocalFile():
                    links.append(str(url.toLocalFile()))
                else:
                    links.append(str(url.toString()))
            print(links)
            print(self)
            self.addItems(links)
        else:
            event.ignore()

class AppDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1200, 600)
        self.setWindowTitle('Statusbar')

        self.itemListBox_view = ListBoxWidget(self)

        self.lb = QLabel('', self)
        self.lb.setGeometry(850,100,300,50)
        self.pb = QPushButton("Get full path of a file", self)
        self.pb.setGeometry(850,200,150,50)

        self.pb.clicked.connect(self.get_file_name)

        self.btn = QPushButton('Merge', self)
        self.btn.setGeometry(850,400,200,50)
        print(self.getSelectedItem())

        self.btn.clicked.connect(lambda : self.makeWatermarkPDF())

    def get_file_name(self):
        filename = QFileDialog.getOpenFileName()
        if filename[0]:
            fname, ext = os.path.splitext(filename[0])
            if ext == '.png':
                self.lb.setText(filename[0])
            else:
                QMessageBox.about(self, "Warning", "you can select .png file.")
        else:
            QMessageBox.about(self, "Warning", "You don't select anything.")

    def getSelectedItem(self):
        item = QListWidgetItem(self.itemListBox_view.currentItem())
        return item.text()

    def makeWatermarkPDF(self):
        image = Image.open(self.lb.text(), 'r')
        clearImage = self.clearWhiteBackground(image)
        if sys.platform == 'linux':
            clearImage.save(os.getcwd() + '/clearSample.png')
        elif sys.platform == 'window':
            clearImage.save(os.getcwd() + '\clearSample.png')
        else:
            QMessageBox.about(self, "Warning", "Operating system is currently not supported.")
            exit(1)

        if sys.platform == 'linux':
            self.imageToPDF(os.getcwd() + '/clearSample.png', os.getcwd() + '/watermarkImage.pdf')
        else:
            self.imageToPDF(os.getcwd() + '\clearSample.png', os.getcwd() + '\watermarkImage.pdf')
        self.selectedList = self.itemListBox_view.selectedItems()
        print(self.selectedList)
        print(self.itemListBox_view.count())

        items = []
        for i in range(self.itemListBox_view.count()):
            items.append(self.itemListBox_view.item(i).text())
            print(items)
        if sys.platform == 'linux':
            for j in range(self.itemListBox_view.count()):
                self.pdfMerge(os.getcwd() + '/complete' + str(j)+ '.pdf', items[j], os.getcwd() + '/watermarkImage.pdf')
        else:
            for j in range(self.itemListBox_view.count()):
                self.pdfMerge(os.getcwd() + '\complete' + str(j)+ '.pdf', items[j], os.getcwd() + '\watermarkImage.pdf')
        self.itemListBox_view.clear()

    def clearWhiteBackground(self, inputImage):
        image = inputImage.convert('RGBA')

        imageData = inputImage.getdata()

        newImageData = []

        for pixel in imageData:
            if pixel[0] > 240 and pixel[1] > 240 and pixel[2] > 240:
                newImageData.append((0, 0, 0, 0))
            else:
                newImageData.append(pixel)

        image.putdata(newImageData)
        image.putalpha(128)

        return image

    def imageToPDF(self, imagePath, pdfPath):
        newCanvas = canvas.Canvas(pdfPath, pagesize=Image.open(imagePath, 'r').size)

        newCanvas.drawImage(image=imagePath, x=0, y=0, mask='auto')

        newCanvas.save()

    def pdfMerge(self, savePath, pdfPath, watermarkPdfPath):
        pdfFile = open(pdfPath, 'rb')
        pdfReader = PdfFileReader(pdfFile, strict=False)

        watermarkPdfFile = open(watermarkPdfPath, 'rb')
        watermarkPdf = PdfFileReader(watermarkPdfFile, strict=False).getPage(0)

        pdfWriter = PdfFileWriter()

        for pageNum in range(pdfReader.numPages):
            pageObj = pdfReader.getPage(pageNum)

            x = (pageObj.mediaBox[2] - watermarkPdf.mediaBox[2]) / 2
            y = (pageObj.mediaBox[3] - watermarkPdf.mediaBox[3]) / 2

            pageObj.mergeTranslatedPage(page2=watermarkPdf, tx=x, ty=y, expand=False)

            pdfWriter.addPage(pageObj)

        resultFile = open(savePath, 'wb')
        pdfWriter.write(resultFile)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = AppDemo()
    demo.show()
    sys.exit(app.exec_())

