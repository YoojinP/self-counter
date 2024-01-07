import cv2
import pyzbar.pyzbar as pyzbar


class ReadBarcode:
    def __init__(self):
        self.product_barcode = ""
        self.productList = []
        self.i = 0
        self.count = 0
        self.sendList = False  # ui에 물품리스트를 보냈는지 확인
        self.money=0

    def InitProductList(self):  # 혹시모를 물품리스트 전체 삭제 및 초기화
        self.productList.clear()

    def getProductList(self):  # 인식한 바코드 물품 중 첫번째만 내보내기
        return self.productList.pop(0)

    def showProductList(self):  # 전체 리스트 조회
        print(self.productList[:])

    def readBarcode(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        decoded = pyzbar.decode(gray)
        product_barcode = ""
        for d in decoded:
            x, y, w, h = d.rect
            barcode_data = d.data.decode("utf-8")
            barcode_type = d.type
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
            text = '%s (%s)' % (barcode_data, barcode_type)
            product_barcode = barcode_data
            cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)
        return img, product_barcode

    def moneyReturn(self,img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        decoded = pyzbar.decode(gray)
        for d in decoded:
            x, y, w, h = d.rect
            barcode_data = d.data.decode("utf-8")
            barcode_type = d.type
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
            text = '%s (%s)' % (barcode_data, barcode_type)
            self.money = barcode_data
        return self.money


"""
        if not decoded:
            if product_barcode!="":
                productList.append(product_barcode)
            product_barcode=""

        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        elif key == ord('s'):
            i += 1
            cv2.imwrite('c_%03d.jpg' % i, img)
        elif key==ord('k'):  # k를 누르면 뭐가 인식됐는지 알수있음
            print(productList[:])

"""
