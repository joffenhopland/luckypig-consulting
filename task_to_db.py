import mysql.connector
import pandas as pd


class db:
    def __init__(self) -> None:
        dbconfig = {'host': '34.121.34.57',
                    'user': 'luckypig2023',
                    'password': 'LuckypigProject#1',
                    'database': 'Luckypig database', }
        self.configuration = dbconfig


    def __enter__(self):
        self.conn = mysql.connector.connect(**self.configuration)
        self.cursor = self.conn.cursor(prepared=True)
        return self
    
    def read_file(self):
        import pandas as pd
        data = pd.read_csv("questions.csv")
        data1 = data.iloc[0]
        print(data1)
    

def main():
    database = db()
    database.read_file()
main()

    