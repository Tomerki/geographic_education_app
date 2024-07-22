import os
import csv
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
from faker import Faker
import random
from datetime import datetime, timedelta

load_dotenv()


def create_database(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Database created successfully")
    except Error as e:
        print(f"Error: {e}")


def create_table(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Table created successfully")
    except Error as e:
        print(f"Error: {e}")


def alter_table(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Table altered successfully")
    except Error as e:
        print(f"Error while altering table: {e}")


def generate_random_dates(year, start_month, end_month):
    start_date = datetime(year, start_month, 1)
    end_date = datetime(year, end_month + 1, 1) - timedelta(days=1)

    dates_with_random_hours = []

    while start_date <= end_date:
        random_hour = random.randint(0, 23)
        random_minute = random.randint(0, 59)
        random_second = random.randint(0, 59)

        date_with_random_hour = start_date.replace(hour=random_hour, minute=random_minute, second=random_second)
        dates_with_random_hours.append(date_with_random_hour)

        start_date += timedelta(days=1)

    return dates_with_random_hours


def insert_scores(connection, level, user_id):
    dates = generate_random_dates(2024, 2, 7)

    for date in dates:
        score = random.randint(0, 10) * 10
        data = (level, user_id, score, date,)
        try:
            cursor = connection.cursor()
            query = """
                INSERT INTO score (difficulty, user_id, score, date) VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, data)
            connection.commit()
        except Error as e:
            print(f"Error while inserting data: {e}")


def insert_country_id_to_population(connection):
    years = [1970, 1980, 1990, 2000, 2010, 2015, 2020, 2022]
    for year in years:
        try:
            cursor = connection.cursor()
            query = """
                INSERT INTO population (country_id, country_name, year) 
                SELECT country_id, country_name, %s FROM country
            """
            cursor.execute(query, (year,))
            connection.commit()
        except Error as e:
            print(f"Error while inserting data: {e}")


def insert_currency_data(connection):
    with open('countries.csv', 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            data = (row['currency_name'], row['currency_symbol'], row['currency_name'])
            try:
                cursor = connection.cursor()
                query = """
                        INSERT INTO currency (currency_name, symbol)
                        SELECT %s, %s
                        WHERE NOT EXISTS (
                            SELECT 1 FROM currency WHERE currency_name = %s
                        )
                    """
                cursor.execute(query, data)
                connection.commit()
            except Error as e:
                print(f"Error while inserting data: {e}")


def insert_country_data(connection):
    countries_world_population_set = set()
    with open('world_population.csv', 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            countries_world_population_set.add(row['Country/Territory'])
    with open('countries.csv', 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if row['name'] in countries_world_population_set:
                data = (row['id'], row['name'], row['region'], row['currency_name'])
                try:
                    cursor = connection.cursor()
                    query = """INSERT INTO country(country_id, country_name, continent, currency_name) VALUES (%s, %s, %s, %s)"""
                    cursor.execute(query, data)
                    connection.commit()
                except Error as e:
                    print(f"Error while inserting data: {e}")


def update_country_data(connection):
    with open('countries.csv', 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            data = (row['currency_name'], row['id'])
            try:
                cursor = connection.cursor()
                query = """
                        UPDATE country
                        SET country.currency_id = (SELECT currency.currency_id FROM currency WHERE currency.currency_name = %s)
                        WHERE country.country_id = %s
                    """
                cursor.execute(query, data)
                connection.commit()
            except Error as e:
                print(f"Error while inserting data: {e}")


def update_countries_area(connection):
    with open('world_population.csv', 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            data = (row['Area (km²)'], row['Country/Territory'],)
            try:
                cursor = connection.cursor()
                query = """
                                    UPDATE country 
                                    SET country_area = %s
                                    WHERE country_name = %s
                                """
                cursor.execute(query, data)
                connection.commit()
            except Error as e:
                print(f"Error while inserting data: {e}")


def insert_state_data(connection):
    with open('states.csv', 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            data = (row['id'], row['name'], row['country_id'], row['country_id'])
            try:
                cursor = connection.cursor()
                query = """
                        INSERT INTO state (state_id, state_name, country_id)
                        SELECT %s, %s, %s
                        WHERE EXISTS (
                            SELECT 1 FROM country WHERE country_id = %s
                        )
                    """
                cursor.execute(query, data)
                connection.commit()
            except Error as e:
                print(f"Error while inserting data: {e}")


def insert_city_data(connection):
    with open('cities.csv', 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            data = (row['id'], row['name'], row['country_id'], row['state_id'], row['country_id'], row['state_id'])
            try:
                cursor = connection.cursor()
                query = """
                        INSERT INTO city (city_id, city_name, country_id, state_id)
                        SELECT %s, %s, %s, %s
                        WHERE EXISTS (
                            SELECT 1 FROM country WHERE country_id = %s
                        )
                        AND EXISTS (
                            SELECT 1 FROM state WHERE state_id = %s
                        )
                    """
                cursor.execute(query, data)
                connection.commit()
            except Error as e:
                print(f"Error while inserting data: {e}")


def insert_capital_data(connection):
    with open('countries.csv', 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            data = (row['capital'], row['id'], row['id'], row['capital'], row['id'])
            try:
                cursor = connection.cursor()
                query = """
                        INSERT INTO capital (capital_name, country_id)
                        SELECT %s, %s
                        WHERE EXISTS (
                            SELECT 1 FROM country WHERE country_id = %s
                        )
                        AND EXISTS (
                            SELECT 1 FROM city WHERE city.city_name = %s AND city.country_id = %s
                        )
                    """
                cursor.execute(query, data)
                connection.commit()
            except Error as e:
                print(f"Error while inserting data: {e}")


def update_capital_data(connection):
    with open('countries.csv', 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            data = (row['capital'], row['id'], row['id'])
            try:
                cursor = connection.cursor()
                query = """
                        UPDATE capital
                        SET capital.city_id = (SELECT city.city_id FROM city WHERE city.city_name = %s AND city.country_id = %s LIMIT 1)
                        WHERE capital.country_id = %s
                    """
                cursor.execute(query, data)
                connection.commit()
            except Error as e:
                print(f"Error while inserting data: {e}")


def update_population(connection, data):
    try:
        cursor = connection.cursor()

        query = """
                    UPDATE population
                    SET population = %s
                    WHERE country_name = %s AND year = %s
                """
        cursor.execute(query, data)
        connection.commit()
    except Error as e:
        print(f"Error while inserting data: {e}")


def update_countries(connection, data):

    try:
        cursor = connection.cursor()

        query = """
                    UPDATE country 
                    SET country_area = %s
                    WHERE country_name = %s
                """
        cursor.execute(query, data)
        connection.commit()
    except Error as e:
        print(f"Error while inserting data: {e}")


def insert_population_data(connection):
    years = ['1970', '1980', '1990', '2000', '2010', '2015', '2020', '2022']
    with open('world_population.csv', 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            for year in years:
                data = (row[year + ' Population'], row['Country/Territory'], year)
                update_population(connection, data)
            update_countries(connection, (row['Area (km²)'], row['Country/Territory'],))


def insert_users_data(connection):
    fake = Faker()
    try:
        cursor = connection.cursor()

        query = """SELECT country_id FROM country"""
        cursor.execute(query)

        res = cursor.fetchall()
        country_ids = [row[0] for row in res]

        # SQL query to insert data
        insert_query = """
        INSERT INTO user (first_name, last_name, user_name, password, country_id)
        VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(insert_query, ('Best', 'Tester', 'bestester', '123456', '106'))
        # Generate and insert data
        for _ in range(99):
            first_name = fake.first_name()
            last_name = fake.last_name()
            user_name = fake.user_name()
            password = fake.password()
            country_id = random.choice(country_ids)

            cursor.execute(insert_query, (first_name, last_name, user_name, password, country_id))
    except Error as e:
        print(f"Error while inserting data: {e}")


def main(connection):
    if connection is not None:
        insert_currency_data(connection)
        insert_country_data(connection)
        update_country_data(connection)
        ##need to add here delete of currency_name column
        update_countries_area(connection)
        insert_state_data(connection)
        insert_city_data(connection)
        insert_capital_data(connection)
        update_capital_data(connection)
        insert_country_id_to_population(connection)
        insert_population_data(connection)
        ##need to add here delete of country_name column
        insert_users_data(connection)
        for i in range(1, 101):
            insert_scores(connection, 1, i)
            insert_scores(connection, 2, i)
            insert_scores(connection, 3, i)
    connection.commit()


if __name__ == "__main__":
    try:
        # Connect to the MySQL server
        connection = mysql.connector.connect(
            user='root',
            password=os.getenv('MYSQL_ROOT_PASSWORD', os.getenv('MYSQL_ROOT_PASSWORD')),
            host='127.0.0.1',
        )

        if connection.is_connected():

            # Create the 'geography' database
            create_database(connection, "CREATE DATABASE IF NOT EXISTS geography")

            # Connect to the 'geography' database
            connection.database = 'geography'

            # SQL statements to create tables
            table_creation_statements = [
                """CREATE TABLE `country` (
                    `country_id` INT NOT NULL AUTO_INCREMENT,
                    `country_name` VARCHAR(100) NOT NULL,
                    `continent` VARCHAR(45) NOT NULL,
                    `currency_id` INT,
                    `currency_name` VARCHAR(100),
                    `country_area` INT,
                    PRIMARY KEY (`country_id`));""",
                """CREATE TABLE `user` (
                `user_id` INT NOT NULL AUTO_INCREMENT,
                `first_name` VARCHAR(100) NOT NULL,
                `last_name` VARCHAR(100) NOT NULL,
                `user_name` VARCHAR(45) NOT NULL,
                `password` VARCHAR(45) NOT NULL,
                `country_id` INT NOT NULL ,
                PRIMARY KEY (`user_id`));""",
                """
                CREATE TABLE `score` (
                `id` INT NOT NULL AUTO_INCREMENT,
                `difficulty` INT NOT NULL,
                `user_id` INT NOT NULL,
                `score` INT NULL,
                `date` DATETIME NOT NULL,
                PRIMARY KEY (`id`));
                """,
                """
                CREATE TABLE `currency` (
                `currency_id` INT NOT NULL AUTO_INCREMENT,
                `currency_name` VARCHAR(100) NOT NULL,
                `symbol` VARCHAR(45),
                PRIMARY KEY (`currency_id`));
                """,
                """
                CREATE TABLE `population` (
                `country_id` INT,
                `country_name` VARCHAR(100),
                `year` INT,
                `population` INT,
                PRIMARY KEY (`country_id`, `year`));
                """,
                """
                CREATE TABLE `city` (
                `city_id` INT NOT NULL AUTO_INCREMENT,
                `city_name` VARCHAR(100) NOT NULL,
                `country_id` INT NOT NULL,
                `state_id` INT NOT NULL,
                PRIMARY KEY (`city_id`));
                """,
                """
                CREATE TABLE `state` (
                `state_id` INT NOT NULL,
                `state_name` VARCHAR(100) NOT NULL,
                `country_id` INT NOT NULL,
                PRIMARY KEY (`state_id`));
                """,
                """
                CREATE TABLE `capital` (
                `capital_id` INT NOT NULL AUTO_INCREMENT,
                `capital_name` VARCHAR(100) NOT NULL,
                `city_id` INT,
                `country_id` INT NOT NULL UNIQUE,
                PRIMARY KEY (`capital_id`));
                """
            ]

            # Execute the statements to create tables
            for statement in table_creation_statements:
                create_table(connection, statement)

            # Add ALTER TABLE statements here following the same pattern

            alter_table_statements = [
                """ALTER TABLE `user`
                ADD INDEX `user_country_idx` (`country_id` ASC) VISIBLE,
                ADD CONSTRAINT `user_country`
                FOREIGN KEY (`country_id`)
                REFERENCES `country` (`country_id`)
                ON DELETE RESTRICT
                ON UPDATE RESTRICT;""",

                """ALTER TABLE `score`
                ADD INDEX `user_score_idx` (`user_id` ASC) VISIBLE,
                ADD CONSTRAINT `user_score`
                FOREIGN KEY (`user_id`)
                REFERENCES `user` (`user_id`)
                ON DELETE RESTRICT
                ON UPDATE RESTRICT;""",

                """ALTER TABLE `country`
                ADD INDEX `country_currency_idx` (`currency_id` ASC) VISIBLE,
                ADD CONSTRAINT `country_currency`
                FOREIGN KEY (`currency_id`)
                REFERENCES `currency` (`currency_id`)
                ON DELETE RESTRICT
                ON UPDATE RESTRICT;""",

                """ALTER TABLE `population`
                ADD INDEX `population_country_idx` (`country_id` ASC) VISIBLE,
                ADD CONSTRAINT `country_population`
                FOREIGN KEY (`country_id`)
                REFERENCES `country` (`country_id`)
                ON DELETE RESTRICT
                ON UPDATE RESTRICT;""",

                """ALTER TABLE `city`
                ADD INDEX `city_country_idx` (`country_id` ASC) VISIBLE,
                ADD CONSTRAINT `city_country`
                FOREIGN KEY (`country_id`)
                REFERENCES `country` (`country_id`)
                ON DELETE RESTRICT
                ON UPDATE RESTRICT;""",

                """ALTER TABLE `state`
                ADD INDEX `state_country_idx` (`country_id` ASC) VISIBLE,
                ADD CONSTRAINT `state_country`
                FOREIGN KEY (`country_id`)
                REFERENCES `country` (`country_id`)
                ON DELETE RESTRICT
                ON UPDATE RESTRICT;""",

                """ALTER TABLE `city`
                ADD INDEX `city_state_idx` (`state_id` ASC) VISIBLE,
                ADD CONSTRAINT `city_state`
                FOREIGN KEY (`state_id`)
                REFERENCES `state` (`state_id`)
                ON DELETE RESTRICT
                ON UPDATE RESTRICT;""",

                """ALTER TABLE `capital`
                ADD CONSTRAINT `capital_city`
                FOREIGN KEY (`capital_id`)
                REFERENCES `city` (`city_id`)
                ON DELETE RESTRICT
                ON UPDATE RESTRICT,
                ADD CONSTRAINT `capital_country`
                FOREIGN KEY (`country_id`)
                REFERENCES `country` (`country_id`)
                ON DELETE RESTRICT
                ON UPDATE RESTRICT;"""

            ]

            for statement in alter_table_statements:
                alter_table(connection, statement)

            main(connection)

            alter_table_statements = [
                """ ALTER TABLE `country`
                    DROP COLUMN currency_name;
                """,
                """ ALTER TABLE `population`
                    DROP COLUMN country_name;
                """]

            for statement in alter_table_statements:
                alter_table(connection, statement)


    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
    finally:
        if connection.is_connected():
            connection.close()
            print("MySQL connection is closed")
