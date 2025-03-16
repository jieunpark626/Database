import pymysql as pms

def db_connect():
    connection = pms.connect(
        host='localhost',
        port=3306,
        user='root',
        password='pkh9411qaz23!',
        db='music_streaming',
        charset='utf8'
    )
    return connection
