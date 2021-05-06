import sqlite3

TABLE_NAME = "chat"
DB = "Database\\messages_db.db"


class Query:
    queries = {
        "insert_message": """INSERT INTO {table} {column} VALUES {data}""",
        "delete_message": """DELETE FROM {table} WHERE id={id} AND {type}='{name}'""",
        "update_all_statuses": """UPDATE {table} SET read = 1 WHERE receiver='{user}'""",
        "update_one_status": """UPDATE {table} SET read = 1 WHERE receiver='{user}' AND id={id}""",
        "get": """SELECT message from {table} WHERE {filter}"""
    }

    def __init__(self):
        self.sqlite_connection = None
        self.cursor = None

    def connection(self):
        """
        The function opens the connection to the sqliteDB of the project, does not return anything
        """
        try:
            self.sqlite_connection = sqlite3.connect(DB)
            self.cursor = self.sqlite_connection.cursor()
            print("Successfully Connected to SQLite")
        except sqlite3.Error as error:
            if self.sqlite_connection:
                self.sqlite_connection.close()
                print("The SQLite connection is closed")
            raise Exception(str(error))

    def disconnection(self):
        """
        The function closes the connection to the sqliteDB of the project, does not return anything
        """
        try:
            if self.cursor:
                self.cursor.close()
            if self.sqlite_connection:
                self.sqlite_connection.close()
            print("The SQLite connection is closed")
        except sqlite3.Error as error:
            raise Exception(str(error))

    def insert(self, **kwargs):
        """
        The function gets kwargs that contain details of message from sender to receiver and inserts into table in DB
        :param kwargs: includes - receiver (str), sender (str), subject (str), message (str), creation_date (str)
        :return: the function does not return anything
        """
        kwargs.update({"read": 0})
        try:
            keys = tuple(kwargs.keys())
            values = tuple(kwargs.values())
            sqlite_insert_query = Query.queries.get('insert_message').format(table=TABLE_NAME, column=keys, data=values)
            self.cursor.execute(sqlite_insert_query)
            self.sqlite_connection.commit()
        except sqlite3.Error as error:
            self.disconnection()
            raise Exception(f"Failed to insert data into sqlite table, {error}")

    def delete(self, **kwargs):
        """
        The function gets kwargs that contain details of message (id, type of user - sender|receiver and username)
         and deletes a relevant message (by the details) from the table in DB
        :param kwargs: includes - id (int), type (str), user (str)
        :return: the function does not return anything
        """
        try:
            sqlite_delete_query = Query.queries.get('delete_message').format(table=TABLE_NAME, id=kwargs.get('id'),
                                                                             type=kwargs.get('type'),
                                                                             name=kwargs.get('user'))

            self.cursor.execute(sqlite_delete_query)
            self.sqlite_connection.commit()
        except sqlite3.Error as error:
            self.disconnection()
            raise Exception(f"Failed to delete data from sqlite table, {error}")

    def get_messages_for_user(self, user):
        """
        :param user: the function gets a receiver name - user (str)
        :return: the function returns all messages for the user that it gets
        """
        try:
            filter_of_query = f"receiver=\'{user}\'"
            sqlite_get_messages_from_user_query = Query.queries.get('get').format(table=TABLE_NAME,
                                                                                  filter=filter_of_query)
            self.cursor.execute(sqlite_get_messages_from_user_query)
            all_messages = self.cursor.fetchall()
            self.sqlite_connection.commit()
            return self.mapping_messages_list(all_messages)
        except sqlite3.Error as error:
            raise Exception(f"Failed to get data from sqlite table, {error}")

    def get_unread_messages_for_user(self, user):
        """
        :param user: the function gets a receiver name - user (str)
        :return: the function returns all the unread messages (by selecting read=0 in the table) for the user that it
         gets
        """
        try:
            filter_of_query = f"receiver=\'{user}\' AND read=0"
            sqlite_get_messages_from_user_query = Query.queries.get('get').format(table=TABLE_NAME,
                                                                                  filter=filter_of_query)
            self.cursor.execute(sqlite_get_messages_from_user_query)
            all_messages = self.cursor.fetchall()
            self.sqlite_connection.commit()
            return self.mapping_messages_list(all_messages)
        except sqlite3.Error as error:
            raise Exception(f"Failed to get data from sqlite table, {error}")

    def get_specific_message(self, id):
        """
        :param id: the function gets an id of a message (int)
        :return: the function returns the relevant message from the table that has the same id the function gets
        """
        try:
            filter_of_query = f"id=\'{id}\'"
            sqlite_get_messages_from_user_query = Query.queries.get('get').format(table=TABLE_NAME,
                                                                                  filter=filter_of_query)
            self.cursor.execute(sqlite_get_messages_from_user_query)
            all_messages = self.cursor.fetchall()
            self.sqlite_connection.commit()
            return self.mapping_messages_list(all_messages)
        except sqlite3.Error as error:
            raise Exception(f"Failed to get data from sqlite table, {error}")

    def update_reading_status(self, user):
        """
        :param user: the function gets a receiver name - user (str)
        The function updates all the reading statuses of the user it gets to be 1 (which means the messages were read)
        in the table in db
        :return: the function does not return anything
        """
        try:
            sqlite_update_query = Query.queries.get('update_all_statuses').format(table=TABLE_NAME, user=user)
            self.cursor.execute(sqlite_update_query)
            self.sqlite_connection.commit()
        except sqlite3.Error as error:
            raise Exception(f"Failed to update data in sqlite table, {error}")

    def update_one_reading_status(self, id, user):
        """
        :param id: the function gets an id of a message (int)
        :param user: the function gets a receiver name - user (str)
        The function updates the reading status of the user with the id it gets to be 1 (which means the specific
        message was read) in the table in db
        :return: the function does not return anything
        """
        try:
            sqlite_update_query = Query.queries.get('update_one_status').format(table=TABLE_NAME, user=user, id=id)
            self.cursor.execute(sqlite_update_query)
            self.sqlite_connection.commit()
        except sqlite3.Error as error:
            raise Exception(f"Failed to update data in sqlite table, {error}")

    @staticmethod
    def mapping_messages_list(data):
        """
        :param data: a list of tuples
        :return: the function returns a neat list without tuples, after mapping as a string!
        """
        return ','.join(list(map(lambda x: x[0], data)))

    @staticmethod
    def input_checking(data):
        """
        :param data: the function gets data from the client|postman as a json
        :return: the function returns an error list that it's purpose to test if the input of the user is empty and
         need to be changed or the input has no errors (empty errors_list). Also, in case of Exception the function
         returns the Exception as an error
        """
        try:
            errors_list = []
            for index in data.items():
                if index[1] == "":
                    errors_list.append(index[0])
            return errors_list
        except Exception as error:
            return error
