import pymssql


# MSSQL 접속
class Payment:
    def __init__(self):
        self.conn = pymssql.connect(server='61.74.166.234', port='1433',
                                    user='server_talk', password='1234',
                                    database='MARKET',
                                    charset='utf8')
        # Connection 으로부터 Cursor 생성
        self.cursor = self.conn.cursor()


    def findProduct(self, code):
        # SQL문 실행
        self.cursor.execute("SELECT product_name, price FROM PRODUCTS WHERE barcode = '"+code+"';")
        # 데이타 하나씩 Fetch하여 출력
        row = self.cursor.fetchone()
        pros = dict()
        while row:
            print(row[0], row[1])
            pros[row[0]] = row[1]   # name 이 key, price 가 value
            row = self.cursor.fetchone()
        return pros

    def findProductByName(self,_name):
        prosArray = dict()
        eng_korNameArray=dict()  # 한글 이름과 영어 이름 이어주는 역할
        for i in _name:
            self.cursor.execute("SELECT product_name, price FROM PRODUCTS WHERE label_name= '" + i + "';")
        # 데이타 하나씩 Fetch하여 출력
            row = self.cursor.fetchone()
            while row:
                print(row[0], row[1])
                eng_korNameArray[i]=row[0]
                prosArray[row[0]] = row[1]  # name 이 key, price 가 value
                row = self.cursor.fetchone()
        return prosArray,eng_korNameArray

    def finishPayment(self):
        # 연결 끊기
        self.conn.close()

if __name__ == "__main__":
    pay=Payment()
    arr={'kkokkalkon72','shrimpcracker90'}
    temp, temp1=pay.findProductByName(arr)
    print("temp: ",temp)
    print("temp1(eng_korNameArray): ",temp1)