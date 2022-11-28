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

def create_database(connection):
    cursor = connection.cursor()
    query = "CREATE DATABASE Discord"
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


def create_table(db_connection):
    try:
        query = "CREATE TABLE IF NOT EXISTS offenses (user_id BIGINT, number_of_offenses INT);"
        execute_query(db_connection, query)
        print("Creation Successful.")
    except:
        print("Creation Failed.")

def insert_new_user(usr, db_connection):
    query = "INSERT INTO offenses (user_id, number_of_offenses) VALUES ({}, '{}')".format(usr.id, 1)
    execute_query(db_connection, query)

def update_offense_count(usr, db_connection, ofs):
    update = """
             UPDATE offenses 
             SET number_of_offenses = {} 
             WHERE user_id = {}
             """.format(ofs+1, usr.id)
    execute_query(db_connection, update)

def insert_server_setting(db_connection, sense, limit, alert_channel, server_id):
    query = "INSERT INTO settings (server, offense_limit, sensitivity, alert_channel) VALUES ({}, {}, {}, {})".format(server_id, limit, sense, alert_channel)
    execute_query(db_connection, query)

def update_settings(db_connection, sense, limit, alert_channel, server_id):
    update = """
             UPDATE settings 
             SET offense_limit = {}
             WHERE server = {}
             """.format(limit, server_id)
    execute_query(db_connection, update)

    update = """
            UPDATE settings
            SET sensitivity = {}
            WHERE server = {}
            """.format(sense, server_id)
    execute_query(db_connection, update)

    update = """
            UPDATE settings
            SET alert_channel = {}
            WHERE server = {}
            """.format(alert_channel, server_id)
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

def fetch_all_setttings_data(db_connection):
    fetch = """
            SELECT *
            FROM settings;
            """
    return read_query(db_connection, fetch)

def get_offenses(db_connection, usr):
    fetch = """
            SELECT number_of_offenses 
            FROM offenses 
            WHERE user_id = {}
            """.format(usr.id)
    return read_query(db_connection, fetch)

def create_setting_table(db_connection):
    query = "CREATE TABLE IF NOT EXISTS settings (server BIGINT, offense_limit INT, sensitivity FLOAT, alert_channel BIGINT);"
    execute_query(db_connection, query)


