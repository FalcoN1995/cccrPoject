import sys, os

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic

from PIL import Image
from reportlab.pdfgen import canvas
from PyPDF3 import PdfFileReader, PdfFileWriter

form_class = uic.loadUiType("listwidgetTest.ui")[0]

class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        #ListWidget의 시그널
        self.itemListBox.itemClicked.connect(self.chkItemClicked)
        self.itemListBox.itemDoubleClicked.connect(self.chkItemDoubleClicked)
        self.itemListBox.currentItemChanged.connect(self.chkCurrentItemChanged)

        #버튼에 기능 연결
        self.btn_addItem_pdf.clicked.connect(self.getPdfFilepath)
        self.btn_addItem_png.clicked.connect(self.getPngFilepath)
        self.btn_createItem.clicked.connect(self.createWMPdf)
        self.btn_removeItem.clicked.connect(self.removeCurrentItem)
        self.btn_clearItem.clicked.connect(self.clearItem)

    #ListWidget의 시그널에 연결된 함수들
    def chkItemClicked(self) :
        print(self.itemListBox.currentItem().text())

    def chkItemDoubleClicked(self) :
        print(str(self.itemListBox.currentRow()) + " : " + self.itemListBox.currentItem().text())

    def chkCurrentItemChanged(self) :
        print("Current Row : " + str(self.itemListBox.currentRow()))

    #항목을 추가, 삽입하는 함수들
    def getPdfFilepath(self) :
        filename = QFileDialog.getOpenFileName()
        if filename[0]:
            fname, ext = os.path.splitext(filename[0])
            if ext == '.pdf':
                self.addItemText = filename[0]
                if self.isExist(self.addItemText):
                    self.itemListBox.addItem(self.addItemText)
                else:
                    QMessageBox.about(self, "Warning", "Already Exist.")
            else:
                QMessageBox.about(self, "Warning", "you can select only .pdf file.")
        else:
            QMessageBox.about(self, "Warning", "You don't select anything.")

    def isExist(self, pdfPath):
        items = []
        for i in range(self.itemListBox.count()):
            items.append(self.itemListBox.item(i).text())
        if pdfPath not in items:
            return True
        else:
            return False

    def getPngFilepath(self):
        filename = QFileDialog.getOpenFileName()
        if filename[0]:
            fname, ext = os.path.splitext(filename[0])
            if ext == '.png':
                self.line_addItem_png.setText(filename[0])
            else:
                QMessageBox.about(self, "Warning", "you can select only .png file.")
        else:
            QMessageBox.about(self, "Warning", "You don't select anything.")

    #Button Function
    def createWMPdf(self):
        image = Image.open(self.line_addItem_png.text(), 'r')
        clearImage = self.clearWhiteBackground(image)
        if sys.platform == 'linux' or sys.platform == 'linux2':
            clearImage.save(os.getcwd() + '/clearSample.png')
        elif sys.platform == 'win32':
            clearImage.save(os.getcwd() + '\clearSample.png')
        else:
            QMessageBox.about(self, "Warning", "Operating system is currently not supported.")
            exit(1)

        if sys.platform == 'linux' or sys.platform == 'linux2':
            self.imageToPDF(os.getcwd() + '/clearSample.png', os.getcwd() + '/watermarkImage.pdf')
        else:
            self.imageToPDF(os.getcwd() + '\clearSample.png', os.getcwd() + '\watermarkImage.pdf')

        items = []
        for i in range(self.itemListBox.count()):
            items.append(self.itemListBox.item(i).text())

        if sys.platform == 'linux' or sys.platform == 'linux2':
            for j in range(self.itemListBox.count()):
                self.pdfMerge(os.getcwd() + '/complete' + str(j) + '.pdf', items[j],
                              os.getcwd() + '/watermarkImage.pdf')
        else:
            for j in range(self.itemListBox.count()):
                self.pdfMerge(os.getcwd() + '\complete' + str(j) + '.pdf', items[j],
                              os.getcwd() + '\watermarkImage.pdf')
        self.itemListBox.clear()

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

    def removeCurrentItem(self) :
        #ListWidget에서 현재 선택한 항목을 삭제할 때는 선택한 항목의 줄을 반환한 후, takeItem함수를 이용해 삭제합니다.
        self.removeItemRow = self.itemListBox.currentRow()
        self.itemListBox.takeItem(self.removeItemRow)

    def clearItem(self) :
        self.itemListBox.clear()


if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()