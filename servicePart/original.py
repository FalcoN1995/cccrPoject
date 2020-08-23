import sys #매개변수를 입력받기 위해 사용
from PIL import Image
from reportlab.pdfgen import canvas
from PyPDF3 import PdfFileReader, PdfFileWriter

def ClearWhiteBackground(image):
    #RGBA로 속성 변경
    image = image.convert('RGBA')

    #해당 이미지의 배열 받아오기
    imageData = image.getdata()

    newImageData = []

    for pixel in imageData:
        if pixel[0] > 240 and pixel[1] > 240 and pixel[2] > 240:
            # rgb값이 240,240,240 이상일 경우(흰색에 가까울 경우) 알파값을 0으로 준다
            newImageData.append((0,0,0,0))
        else:
            # 아닐경우 그대로 쓴다
            newImageData.append(pixel)

    #이미지를 덮어 씌움
    image.putdata(newImageData)
    #투명도 값 (0~255), 절반정도 투명도 
    image.putalpha(128)

    return image

def ImageToPDF(imagePath, pdfPath):
    newCanvas = canvas.Canvas(pdfPath, pagesize=Image.open(imagePath,'r').size)

    newCanvas.drawImage(image=imagePath,x=0,y=0, mask='auto')

    newCanvas.save()

def PDFMerge(savePath, pdfPath, watermarkPdfPath):
    # pdf파일 불러오기
    pdfFile = open(pdfPath,'rb')
    pdfReader = PdfFileReader(pdfFile, strict=False)

    # 워터마크 PDF파일 불러오기
    watermarkPdfFile = open(watermarkPdfPath, 'rb')
    watermarkPdf = PdfFileReader(watermarkPdfFile, strict=False).getPage(0)

    pdfWriter = PdfFileWriter()

    #PDF 페이지 수만큼 반복
    for pageNum in range(pdfReader.numPages):

        #페이지를 불러온다
        pageObj = pdfReader.getPage(pageNum)

        #중앙으로 놓기 위해 좌표를 구한다
        x = (pageObj.mediaBox[2] - watermarkPdf.mediaBox[2]) / 2
        y = (pageObj.mediaBox[3] - watermarkPdf.mediaBox[3]) / 2

        # 워터마크페이지와 합친다
        pageObj.mergeTranslatedPage(page2=watermarkPdf, tx=x, ty=y, expand=False)

        #합친걸 저장할 PDF파일에 추가한다
        pdfWriter.addPage(pageObj)

    #저장
    resultFile = open(savePath, 'wb')
    pdfWriter.write(resultFile)


def Test():
    argList = sys.argv

    image = Image.open(argList[1]+argList[2],'r')
    clearImage = ClearWhiteBackground(image)

    clearImage.save(argList[1]+'clearSample.png')

    ImageToPDF(argList[1]+'clearSample.png', argList[1]+'watermarkImage.pdf')

    PDFMerge(argList[1]+'complete.pdf', argList[1]+argList[3], argList[1]+'watermarkImage.pdf')

Test()
