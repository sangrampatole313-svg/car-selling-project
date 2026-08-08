import mysql.connector
import os
def get_db_connection():

    try:

        connection = mysql.connector.connect(
            host=os.getenv("MYSQLHOST", "localhost"),
            port=int(os.getenv("MYSQLPORT", 3306)),
            user=os.getenv("MYSQLUSER", "root"),
            password=os.getenv("MYSQLPASSWORD", ""),
            database=os.getenv("MYSQLDATABASE", "car_selling")
        )

        return connection

    except mysql.connector.Error as e:

        print(f"[DATABASE ERROR] {e}")

        return None