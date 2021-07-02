import sqlite3


class Database:
    def __init__(self, path_to_db="data/main.db"):
        self.path_to_db = path_to_db
    
    @property
    def connection(self):
        return sqlite3.connect(self.path_to_db)
    
    def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = ()
        connection = self.connection
        connection.set_trace_callback(logger)
        cursor = connection.cursor()
        data = None
        cursor.execute(sql, parameters)
        
        if commit:
            connection.commit()
        if fetchall:
            data = cursor.fetchall()
        if fetchone:
            data = cursor.fetchone()
        connection.close()
        return data
    
    def create_table_users(self):
        sql = """
        CREATE TABLE Users (
            user_id int NOT NULL,
            username varchar(255) NOT NULL,
            phone_number int NOT NULL
            );"""
        self.execute(sql, commit=True)

    def create_table_bot(self):
        sql = """
            CREATE TABLE Bot (
            status varchar(255)
            );"""
        self.execute(sql, commit=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ?" for item in parameters
        ])
        return sql, tuple(parameters.values())

    def add_user(self, user_id: int, username, phone_number=0):
        # SQL_EXAMPLE = "INSERT INTO Users(user_id, username, phone_number) VALUES(1, '@ddddd', 380999111111)"
        sql = """
        INSERT INTO Users (user_id, username, phone_number) VALUES(?, ?, ?)
        """
        self.execute(sql, parameters=(user_id, username, phone_number), commit=True)

    def select_all_users(self) -> list:
        # return list of users
        sql = """
        SELECT * FROM Users
        """
        return self.execute(sql, fetchall=True)

    def select_user(self, **kwargs):
        sql = """SELECT * FROM Users WHERE """
        sql, parameters = self.format_args(sql, kwargs)
    
        return self.execute(sql, parameters=parameters, fetchone=True)

    def add_bot_status(self, status):
        # status= open/close
        sql = """
        INSERT INTO Bot(status) VALUES(?)
        """
        self.execute(sql, parameters=(status,), commit=True)

    def update_bot_status(self, status):
        # status= open/close
        sql = f"""
        UPDATE Bot SET status=?
        """
        self.execute(sql, parameters=(status,), commit=True)

    def select_bot_status(self):
        return self.execute("""SELECT status FROM Bot""", fetchone=True)
    
    def delete_users(self):
        self.execute("DELETE FROM Users WHERE TRUE", commit=True)


def logger(statement):
    print(f"""\n
_____________________________________________________
Executing:
{statement}
_____________________________________________________
""")
