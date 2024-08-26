import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="bkurz4fsfjjj6hlkgxoe-mysql.services.clever-cloud.com",
        user="uirhtuqeqqzuschs",
        password="YI3BZDWf1H0VgXi5tvfN",
        database="bkurz4fsfjjj6hlkgxoe",
        port=3306
    )
