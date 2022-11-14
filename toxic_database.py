import mysql.connector
from mysql.connector import Error


def create_server_connection(host_name, user_name, user_password):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")

    return connection

def create_database(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Database created successfully")
    except Error as err:
        print(f"Error: '{err}'")

def create_db_connection(host_name, user_name, user_password, db_name):  #very similar to establishing a connection 
    connection = None                                                    #but it connects directly into the database
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")

    return connection

def execute_query(connection, query):  #similar to create database function but this one makes sure
    cursor = connection.cursor(buffered=True)
    try:
        cursor.execute(query)
        connection.commit() #that our commands are implemented with this line
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")

    #this function is very crucial because it allows us to update and delete our database

def read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as err:
        print(f"Error: '{err}'")

def create_db(name, connection):
    query = "CREATE DATABASE {}".format(name)
    execute_query(connection, query)

def create_table(db_connection):
    query = "CREATE TABLE offenses (user_id INT PRIMARY KEY, number_of_offenses INT);" 
    create_database(db_connection, query)

def insert_new_user(user_id, db_connection):
    query = "INSERT INTO offenses(user_id, number_of_offenses)" \
                    "VALUES({}, 1)".format(user_id)
    execute_query(db_connection, query)

def update_offense_count(user_id, db_connection):
    update = """
             UPDATE offenses 
             SET number_of_offenses = number_of_offenses + 1 
             WHERE user_id = {};
             """.format(user_id)
    execute_query(db_connection, update)

def fetch_user_data(user_id, db_connection):
    fetch = """
         SELECT user_id, number_of_offenses
         FROM offenses
         WHERE user_id = {};
         """.format(user_id)
    
    return read_query(db_connection, fetch)

def fetch_all_data(db_connection):
    fetch = """
            SELECT *
            FROM offenses;
            """
    return read_query(db_connection, fetch)


