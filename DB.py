import pymysql

class DB:
    def __init__(self, hostname, user_name, password, db_name):
        self.hostname = hostname
        self.user_name = user_name
        self.password = password
        self.db_name = db_name
        self.con = pymysql.connect(hostname, user_name, password, db_name, cursorclass=pymysql.cursors.DictCursor,
                                   autocommit=True)
        self.cursor = self.con.cursor()

    def exec_query(self, query: str):
        self.cursor.execute(query)
        return self.cursor

    def exec_template_query(self, template, values: tuple):
        self.cursor.execute(template, values)
