import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
import game_queries
import random
import string
import os
from datetime import datetime, timedelta
from Database import db_pool

app = Flask(__name__)
CORS(app)


@app.route('/user', methods=['POST'])
def get_user():
    """
    Given a user's username and password, this function returns the user's data from the dataset.
    :return: Json.
    """
    # Get parameters from the request body
    user_name = request.json.get('username')
    password = request.json.get('password')

    # Validate parameters
    if not user_name or not password:
        return jsonify({'error': 'Missing parameters'}), 400

    connection = db_pool.get_connection()
    cursor = connection.cursor(dictionary=True)
    data = (user_name, password)

    # Executing a SQL query that returns all the user's data in the dataset, given the user's username and password.
    cursor.execute("SELECT * FROM user WHERE user_name = %s AND password = %s;", data)
    result = cursor.fetchall()

    cursor.close()
    connection.close()
    return jsonify(result[0] if result else None)


@app.route('/user/<user_name>', methods=['GET'])
def get_home_page(user_name):
    """
    A function that returns the home page, given a username.
    :param user_name: string.
    :return: Json.
    """

    # A query that returns the user's first name and last name as his/hers name, the user's country and the country's
    # continent, capital, currency, symbol of currency, number of cities in the country, and the number of people in
    # the country  (the population in 2022).
    query = """SELECT CONCAT(user.first_name , " " , user.last_name) AS name,
            country.country_name ,country.continent, capital.capital_name,
            currency.currency_name, currency.symbol,
            COUNT(city.city_id) AS city_counter, population.population as population_2022 
            FROM user 
            LEFT JOIN country ON (country.country_id = user.country_id)
            LEFT JOIN capital ON (country.country_id = capital.country_id)
            LEFT JOIN currency ON (country.currency_id = currency.currency_id)
            LEFT JOIN population ON (country.country_id = population.country_id)
            LEFT JOIN city ON (country.country_id = city.country_id)
            WHERE user.user_name = %s
            AND population.year = 2022
            GROUP BY user.user_id;"""
    params = (user_name,)

    connection = db_pool.get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(query, params)
        result = cursor.fetchall()
    except Exception as e:
        # Handle exception
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

    return jsonify(result[0] if result else None)


@app.route('/scores/<user_name>', methods=['GET'])
def get_user_scores(user_name):
    """
    A function that returns the user's game scores.
    :param user_name: string.
    :return: Json.
    """

    # Get parameters from the request body
    thirty_days_ago = datetime.now() - timedelta(days=30)
    thirty_days_ago_str = thirty_days_ago.strftime('%Y-%m-%d')
    now_str = datetime.now().strftime('%Y-%m-%d')
    results = {1: {}, 2: {}, 3: {}}
    for i in range(1, 4):
        data = (user_name, i, thirty_days_ago_str, now_str)

        # A query that returns the game scores of a user.
        query = """SELECT score.* FROM score
                       INNER JOIN user ON (score.user_id = user.user_id)
                       WHERE user.user_name = %s
                       AND difficulty = %s
                       AND date BETWEEN DATE(%s) AND DATE(%s)
                       ORDER BY date ASC;"""

        connection = db_pool.get_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute(query, data)
            result = cursor.fetchall()
            results[i] = result
        except Exception as e:
            # Handle exception
            return jsonify({'error': str(e)}), 500
        finally:
            cursor.close()
            connection.close()

    return jsonify(results if results else None)


@app.route('/max_score', methods=['GET'])
def get_max_scores():
    """
    A function that returns the maximal score in the games.
    :return: Json.
    """
    # Get parameters from the request body
    thirty_days_ago = datetime.now() - timedelta(days=30)
    thirty_days_ago_str = thirty_days_ago.strftime('%Y-%m-%d')
    now_str = datetime.now().strftime('%Y-%m-%d')
    results = {1: {}, 2: {}, 3: {}}
    for i in range(1, 4):
        data = (now_str, i, now_str, i,)

        # A query that returns the username and the user's name (first name and last name) that got the maximal score in
        # the game, and the date of achievement.
        query = """SELECT user.user_name,user.first_name,user.last_name, MAX(score) AS max_score, MAX(date) AS date_time
                    FROM score
                    JOIN user ON (score.user_id = user.user_id)
                    AND DATE(date) = %s
                    AND difficulty = %s
                    GROUP BY user.user_name,user.first_name,user.last_name
                    HAVING max_score IN (SELECT MAX(score)
                                        FROM score
                                        JOIN user ON (score.user_id = user.user_id)
                                        AND DATE(date) = %s
                                        AND difficulty = %s)
                    ORDER BY date_time DESC LIMIT 1;"""

        connection = db_pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(query, data)
            result = cursor.fetchall()
            results[i] = result[0]
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            cursor.close()
            connection.close()

    return jsonify(results if results else None)


@app.route('/accomplishments/<user_name>', methods=['GET'])
def get_user_avg_tries_max_scores(user_name):
    """
    A functions that returns the average score, the highest score, and the numbers of tries in a game of a user at each
    level of the game.
    :param user_name: string.
    :return: Json.
    """
    # Get parameters from the request body
    thirty_days_ago = datetime.now() - timedelta(days=30)
    thirty_days_ago_str = thirty_days_ago.strftime('%Y-%m-%d')
    now_str = datetime.now().strftime('%Y-%m-%d')

    # A query that returns the level played in the game (field difficulty), the number of tries in the game, the average
    # score of the user, the highest score in the game, the date that the highest score was achieved at the easy level,
    # the date that the highest score was achieved at the medium level, and the date that the highest score was achieved
    # at the hard level.
    query = """SELECT x.difficulty,best_score as max ,date_of_best_score as date_of_max,avg, tries FROM 
                (SELECT
                    difficulty,
                    MAX(score) AS best_score,
                    MAX(CASE WHEN date = max_date THEN date END) AS date_of_best_score,
                    max_date AS max_date
                FROM
                    (SELECT
                        s1.difficulty,
                        s1.score,
                        s1.date,
                        MAX(s1.date) OVER (PARTITION BY s1.difficulty) AS max_date
                    FROM
                        score s1
                    JOIN
                        (SELECT
                            difficulty,
                            MAX(score) AS best_score
                        FROM
                            score
                        WHERE
                            user_id = (SELECT user_id FROM user WHERE user_name = %s)
                            AND difficulty IN (1, 2, 3)
                            AND date BETWEEN%s AND %s
                        GROUP BY
                            difficulty) s2 ON s1.difficulty = s2.difficulty AND s1.score = s2.best_score
                    WHERE
                        s1.user_id = (SELECT user_id FROM user WHERE user_name = %s)
                        AND s1.date BETWEEN %s AND %s) AS best_scores
                GROUP BY
                    difficulty, max_date) as x,
                
                (SELECT
                    difficulty,
                    AVG(score) AS avg,
                    count(score) AS tries
                FROM
                    score
                WHERE
                    user_id = (SELECT user_id FROM user WHERE user_name = %s)
                    AND difficulty IN (1, 2, 3)
                    AND date BETWEEN %s AND %s
                GROUP BY
                    difficulty) as y
                WHERE x.difficulty = y.difficulty
                ORDER BY x.difficulty ASC;"""

    data = (user_name,thirty_days_ago_str, now_str, user_name,thirty_days_ago_str, now_str, user_name, thirty_days_ago_str, now_str,)

    connection = db_pool.get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(query, data)
        result = cursor.fetchall()
    except Exception as e:
        # Handle exception
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

    results = {1: result[0], 2: result[1], 3: result[2]}
    return jsonify(results if result else None)


@app.route('/country/<country_name>', methods=['GET'])
def get_country_data(country_name):
    """
    Returns the data of a given country.
    :param country_name: string.
    :return: Json.
    """

    # A query that returns a country's name, area, it's continent, currency, population of 2022, the average number of
    # the rate of the population's increase from 1970 to 2022, and the number of cities.
    query = """select country.country_name, country.country_area, country.continent, currency.currency_name, population_2022.population,
		              ROUND(AVG((population_2022.population - population_1970.population) / population_1970.population * 100)) AS avg_increase_rate,
                      capital.capital_name, COUNT(city.city_id) AS number_of_cities
               from country, city, currency, population as population_2022, population as population_1970, capital
               where country.country_id = population_1970.country_id and
					 country.country_id = population_2022.country_id and
                     country.country_id = capital.country_id and
                     country.country_id = city.country_id and
                     country.currency_id = currency.currency_id and
                     country.country_name =  %s
                     and population_1970.year =  1970 and population_2022.year =  2022
                group by country.country_name, country.country_area, country.continent, currency.currency_name,
                         population_2022.population,population_1970.population,capital.capital_name;"""

    data = (country_name,)
    connection = db_pool.get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, data)
        result = cursor.fetchall()
    except Exception as e:
        # Handle exception
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

    return jsonify(result[0] if result else None)


@app.route('/country', methods=['GET'])
def get_all_countries():
    """
    A function that returns all the countries in the dataset.
    :return: Json.
    """
    param_value = request.args.get('s', None)

    if param_value:
        # A query that returns the data of a country, given the country's name -
        # the country's name, it's area, in which continent the country is located at, it's currency, the average rate
        # of population growth from 1970 to 2022, it's capital and the number of cities in the country.
        query = """select country.country_name, country.country_area, country.continent, currency.currency_name,
		           ROUND(AVG((population_2022.population - population_1970.population) / population_1970.population * 100)) AS avg_increase_rate,
                   population_2022.population as population_2022, capital.capital_name, COUNT(city.city_id) AS number_of_cities
               from country, currency, population as population_2022, population as population_1970, capital, city
               where country.country_id = population_1970.country_id and
					country.country_id = population_2022.country_id and
                     country.country_id = capital.country_id and
                     country.currency_id = currency.currency_id and
                     country.country_id = city.country_id and
                     country.country_name LIKE %s
                     and population_1970.year =  1970 and population_2022.year =  2022
                group by country.country_name, country.country_area, country.continent, currency.currency_name,
                         population_2022.population,population_1970.population,capital.capital_name;"""
        params = (param_value + '%',)
    else:
        # A query that returns the data of a country, when the country's name isn't given -
        # the country's name, it's area, in which continent the country is located at, it's currency, the average rate
        # of population growth from 1970 to 2022, it's capital and the number of cities in the country.
        query = """select country.country_name, country.country_area, country.continent, currency.currency_name,
		           ROUND(AVG((population_2022.population - population_1970.population) / population_1970.population * 100)) AS avg_increase_rate,
                   population_2022.population as population_2022, capital.capital_name, COUNT(city.city_id) AS number_of_cities
               from country, currency, population as population_2022, population as population_1970, capital, city
               where country.country_id = population_1970.country_id and
					country.country_id = population_2022.country_id and
                     country.country_id = capital.country_id and
                     country.currency_id = currency.currency_id and
                     country.country_id = city.country_id and
                     population_1970.year =  1970 and population_2022.year =  2022
                group by country.country_name, country.country_area, country.continent, currency.currency_name,
                         population_2022.population,population_1970.population,capital.capital_name;"""
        params = None

    connection = db_pool.get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        result = cursor.fetchall()
    except Exception as e:
        # Handle exception
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()
    return jsonify(result if result else None)


@app.route('/questions', methods=['GET'])
def get_questions():
    """
    A function that returns a list of questions that will show in the game in the easy level.
    :return: Json.
    """
    # First batch of EASY questions.
    # A query that returns each time four random countries, and some details about them such as their names, their ids,
    # name of capital etc.
    query = """SELECT
                    sq.country_name, 
                    sq.country_id,
                    sq.capital,
                    sq.continent,
                    sq.number_of_cities,
                    sq.random_city,
                    sq.place_in_world_by_area,
                    sq.place_in_world_by_population
                FROM (
                    SELECT 
                        c.country_name,
                        c.country_id,
                        ca.capital_name AS capital,
                        c.continent,
                        COUNT(ci.city_id) AS number_of_cities,
                        (SELECT city_name FROM city WHERE country_id = c.country_id ORDER BY RAND() LIMIT 1) AS random_city,
                        RANK() OVER (ORDER BY c.country_area DESC) AS place_in_world_by_area,
                        RANK() OVER (ORDER BY p.population DESC) AS place_in_world_by_population,
                        DENSE_RANK() OVER (PARTITION BY c.continent ORDER BY RAND()) AS continent_rank
                    FROM 
                        country c
                    JOIN 
                        capital ca ON c.country_id = ca.country_id
                    JOIN 
                        city ci ON c.country_id = ci.country_id
                    JOIN 
                        population p ON c.country_id = p.country_id
                    WHERE p.year = 2022
                    GROUP BY 
                        c.country_id
                ) AS sq
                WHERE sq.continent_rank = 1
                ORDER BY RAND()
                LIMIT 4;"""

    connection = db_pool.get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        new_result = helper(result)
    except Exception as e:
        # Handle exception
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

    # First query returns the currency, and it's symbol, of four countries (the first output will be treated as the
    # right answer - of one known country and 3 more random countries).
    # Second query returns the id and name of four cities (of one known country and 3 more random countries).
    # Third query returns the average change in growth between the years of 2022 and 1970 of four countries ("").
    # Fourth query returns the number of different state in a country of four countries ("").
    qureis = ["""(SELECT currency.currency_name, currency.symbol 
                    FROM country LEFT JOIN currency 
                    ON(country.currency_id = currency.currency_id)
                    WHERE country.country_id = %s) 
                    UNION 
                    (SELECT DISTINCT currency.currency_name, currency.symbol 
                    FROM currency
                    WHERE currency.currency_id NOT IN (
                    SELECT currency.currency_id FROM country LEFT JOIN currency 
                    ON(country.currency_id = currency.currency_id) 
                    WHERE country.country_id = %s
                    )
                    ORDER BY RAND()
                    LIMIT 3); """,
              """(SELECT city.city_id, city.city_name
                      FROM city
                      WHERE city.country_id <> %s
                      ORDER BY RAND()
                      LIMIT 1)
                      UNION 
                      (SELECT DISTINCT city.city_id, city.city_name
                      FROM country LEFT JOIN city 
                      ON(country.country_id = city.country_id)
                      WHERE country.country_id = %s
                      ORDER BY RAND()
                      LIMIT 3);""",
              """(SELECT (population_2022.population / population_1970.population) as growth_avg
                      FROM population as population_2022 ,population as population_1970
                      WHERE population_2022.country_id = %s AND population_1970.country_id = population_2022.country_id
                      AND population_2022.year = 2022 AND population_1970.year = 1970 LIMIT 1)
                      UNION 
                      (SELECT DISTINCT
                      (population_2022.population / population_1970.population) as growth_avg
                      FROM population as population_2022 ,population as population_1970
                      WHERE population_2022.country_id <> %s AND population_2022.country_id = population_1970.country_id
                      AND population_2022.year = 2022 AND population_1970.year = 1970
                      ORDER BY RAND()
                      LIMIT 3)""",
              """(SELECT COUNT(state.country_id), country_id as counter_states
                      FROM state 
                      WHERE state.country_id = %s
                      GROUP BY state.country_id)
                      UNION
                      (SELECT DISTINCT COUNT(state.country_id), country_id as counter_states
                      FROM state 
                      GROUP BY state.country_id
                      HAVING counter_states NOT IN (
                      SELECT COUNT(state.country_id) as counter FROM state WHERE state.country_id = %s
                      )
                      ORDER BY RAND()
                      LIMIT 3);
                      """]

    new_keys = ['currency', 'city_not_in_country', 'growth_rate', 'number_of_states']
    keys = ['currency_name', 'city_name', 'growth_avg', 'counter_states']
    for i, query in enumerate(qureis):
        connection = db_pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        data = (new_result[0]['country_id'], new_result[0]['country_id'])
        try:
            cursor.execute(query, data)
            result = cursor.fetchall()
            quiz = {f'{new_keys[i]}': {'correct_answer': result[0][keys[i]]}}
            for j, wrong_answer in enumerate(result[1:], start=1):
                quiz[f'{new_keys[i]}'][f'w{j}'] = wrong_answer[keys[i]]
            new_result.append(quiz)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            cursor.close()
            connection.close()

    return jsonify(new_result if new_result else None)


@app.route('/hard_questions', methods=['GET'])
def hard_questions():
    """
    A function that returns all the questions asked in the game in the hard level.
    :return: Json.
    """
    new_results = []
    params = []

    # A query that returns three random countries and their data - the country's id, the name of the country, which
    # continent is the country located at, the capital and the currency.
    query = """SELECT country.country_id, country.country_name, country.continent,
            capital.capital_name, currency.currency_name
            FROM country INNER JOIN capital ON (country.country_id = capital.country_id)
            INNER JOIN currency ON (currency.currency_id = country.currency_id)
            ORDER BY rand()
            LIMIT 3;"""

    connection = db_pool.get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        for i in range(0, 3):
            new_results.append({"question": "What is the currency of " + result[i]["country_name"] + "?"})
            params.append(result[i]["currency_name"])
        for i in range(0, 3):
            new_results.append({"question": "What is the capital of " + result[i]["country_name"] + "?"})
            params.append(result[i]["capital_name"])
        for i in range(0, 3):
            new_results.append({"question": "On which continent is " + result[i]["country_name"] + "?"})
            params.append(result[i]["continent"])

    except Exception as e:
        # Handle exception
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

    # A query that returns three different currencies from a given currency, three capitals different from a given
    # capital, and three different continents from a given continent.
    query = """(SELECT DISTINCT currency.currency_name as var FROM currency WHERE currency_name <> %s ORDER BY rand() LIMIT 3)
                UNION ALL
                (SELECT DISTINCT currency.currency_name as var FROM currency WHERE currency_name <> %s ORDER BY rand() LIMIT 3)
                UNION ALL
                (SELECT DISTINCT currency.currency_name as var FROM currency WHERE currency_name <> %s ORDER BY rand() LIMIT 3)
                UNION ALL 
                (SELECT DISTINCT capital.capital_name as var FROM capital WHERE capital_name <> %s ORDER BY rand() LIMIT 3)
                UNION ALL
                (SELECT DISTINCT capital.capital_name as var FROM capital WHERE capital_name <> %s ORDER BY rand() LIMIT 3)
                UNION ALL
                (SELECT DISTINCT capital.capital_name as var FROM capital WHERE capital_name <> %s ORDER BY rand() LIMIT 3)
                UNION ALL 
                (SELECT DISTINCT country.continent as var FROM country WHERE continent <> %s ORDER BY rand() LIMIT 3)
                UNION ALL
                (SELECT DISTINCT country.continent as var FROM country WHERE continent <> %s ORDER BY rand() LIMIT 3)
                UNION ALL
                (SELECT DISTINCT country.continent as var FROM country WHERE continent <> %s ORDER BY rand() LIMIT 3);"""

    connection = db_pool.get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        result = cursor.fetchall()
        for i in range(0, 9):
            new_results[i]["answers"] = {"correct_answer": params[i], "w1": result[i * 3]["var"],
                                         "w2": result[(i * 3) + 1]["var"],
                                         "w3": result[(i * 3) + 2]["var"]}
    except Exception as e:
        # Handle exception
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

    # A query that returns four random countries and their population (as for the year of 2022).
    query = """(SELECT y.country_name FROM (
                SELECT x.country_name , population.population
                FROM (SELECT country_name, country_id FROM country ORDER BY rand()) as x
                JOIN population ON (x.country_id = population.country_id)
                WHERE population.year = 2022
                ORDER BY rand()
                LIMIT 4) as y
                ORDER BY y.population DESC)

                UNION ALL

                (SELECT x.country_name
                FROM (SELECT country_name, country_area FROM country ORDER BY rand() LIMIT 4) as x
                ORDER BY x.country_area DESC)"""

    connection = db_pool.get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        new_results.append({"question": "Which country has the largest population on 2022?",
                            "answers": {"correct_answer": result[0]["country_name"], "w1": result[1]["country_name"],
                                        "w2": result[2]["country_name"],
                                        "w3": result[3]["country_name"]}})
        new_results.append(
            {"question": "Which country is the largest in terms of territory among the following countries:",
             "answers": {"correct_answer": result[4]["country_name"], "w1": result[5]["country_name"],
                         "w2": result[6]["country_name"],
                         "w3": result[7]["country_name"]}})
    except Exception as e:
        # Handle exception
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

    # A query that returns four random countries and their ranking of their size, by area (compared to the rest of the
    # countries in the world).
    query = """(SELECT a.country_name, a.place_in_world_by_area FROM (select
                c.country_name, RANK() OVER (ORDER BY c.country_area DESC) AS place_in_world_by_area FROM 
                                        country c) as a
                WHERE place_in_world_by_area <= 10
                ORDER BY RAND()
                LIMIT 1)

                UNION ALL

                (SELECT a.country_name, a.place_in_world_by_area FROM (select
                c.country_name, RANK() OVER (ORDER BY c.country_area DESC) AS place_in_world_by_area FROM 
                                        country c) as a
                WHERE place_in_world_by_area > 10
                ORDER BY RAND()
                LIMIT 3)"""

    connection = db_pool.get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        new_results.append(
            {"question": "Which of the following countries is one of the 10 largest countries in terms of area?",
             "answers": {"correct_answer": result[0]["country_name"], "w1": result[1]["country_name"],
                         "w2": result[2]["country_name"],
                         "w3": result[3]["country_name"]}})
    except Exception as e:
        # Handle exception
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

    # A query that returns one random country out of the top 10 most populated countries in the world (ranked by their
    # population) and it's population ranking, and another three other random countries that are NOT part of the 10
    # most populated countries in the world.
    query = """(SELECT DISTINCT a.country_name, a.place_in_world_by_population FROM (select
                c.country_name, RANK() OVER (ORDER BY p.population DESC) AS place_in_world_by_population FROM 
                                        country c JOIN 
                                        population p ON c.country_id = p.country_id
                                    WHERE p.year = 2022
                                    GROUP BY 
                                        c.country_id) as a
                WHERE a.place_in_world_by_population <= 10
                ORDER BY RAND()
                LIMIT 1)

                UNION ALL

                (SELECT DISTINCT a.country_name, a.place_in_world_by_population FROM (select
                c.country_name, RANK() OVER (ORDER BY p.population DESC) AS place_in_world_by_population FROM 
                                        country c JOIN 
                                        population p ON c.country_id = p.country_id
                                    WHERE p.year = 2022
                                    GROUP BY 
                                        c.country_id) as a
                WHERE a.place_in_world_by_population > 10
                ORDER BY RAND()
                LIMIT 3)"""

    connection = db_pool.get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        new_results.append(
            {
                "question": "Which of the following countries is one of the 10 largest countries in terms of population on 2022?",
                "answers": {"correct_answer": result[0]["country_name"], "w1": result[1]["country_name"],
                            "w2": result[2]["country_name"],
                            "w3": result[3]["country_name"]}})
    except Exception as e:
        # Handle exception
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

    # A query that return 12 countries and their data.
    query = """SELECT DISTINCT a.city_name, a.country_id, a_rank, a.country_name from 
                (SELECT city_name, c.country_id, country_name, DENSE_RANK() OVER (PARTITION BY c.country_id ORDER BY RAND()) AS a_rank 
                FROM city c JOIN country as co ON (c.country_id = co.country_id)) as a
                where a.a_rank = 1
                ORDER BY rand()
                LIMIT 12;
                """

    connection = db_pool.get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        new_results.append(
            {
                "question": "Which of the following cities is located in " + result[0]["country_name"] + "?",
                "answers": {"correct_answer": result[0]["city_name"], "w1": result[1]["city_name"],
                            "w2": result[2]["city_name"],
                            "w3": result[3]["city_name"]}})
        new_results.append(
            {
                "question": "Which of the following cities is located in " + result[4]["country_name"] + "?",
                "answers": {"correct_answer": result[4]["city_name"], "w1": result[5]["city_name"],
                            "w2": result[6]["city_name"],
                            "w3": result[7]["city_name"]}})

        new_results.append(
            {
                "question": "Which of the following cities is located in " + result[8]["country_name"] + "?",
                "answers": {"correct_answer": result[8]["city_name"], "w1": result[9]["city_name"],
                            "w2": result[10]["city_name"],
                            "w3": result[11]["city_name"]}})
    except Exception as e:
        # Handle exception
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

    # A query that return 8 countries and their data.
    query = """SELECT DISTINCT a.state_name, a.country_name from 
                (SELECT state_name, s.country_id, country_name, DENSE_RANK() OVER (PARTITION BY s.country_id ORDER BY RAND()) AS a_rank 
                FROM state s JOIN country as co ON (s.country_id = co.country_id)) as a
                where a.a_rank = 1
                ORDER BY rand()
                LIMIT 8;
                   """

    connection = db_pool.get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        new_results.append(
            {
                "question": "Which of the following districts is in " + result[0]["country_name"] + "?",
                "answers": {"correct_answer": result[0]["state_name"], "w1": result[1]["state_name"],
                            "w2": result[2]["state_name"],
                            "w3": result[3]["state_name"]}})
        new_results.append(
            {
                "question": "Which of the following districts is in " + result[4]["country_name"] + "?",
                "answers": {"correct_answer": result[4]["state_name"], "w1": result[5]["state_name"],
                            "w2": result[6]["state_name"],
                            "w3": result[7]["state_name"]}})

    except Exception as e:
        # Handle exception
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

    # A query that returns 8 random currencies.
    query = """SELECT DISTINCT currency_name, symbol FROM currency ORDER BY rand() LIMIT 8;"""

    connection = db_pool.get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        new_results.append(
            {
                "question": "What is the symbol of the currency:  " + result[0]["currency_name"] + "?",
                "answers": {"correct_answer": result[0]["symbol"], "w1": result[1]["symbol"],
                            "w2": result[2]["symbol"],
                            "w3": result[3]["symbol"]}})
        new_results.append(
            {
                "question": "What is the symbol of the currency:  " + result[4]["currency_name"] + "?",
                "answers": {"correct_answer": result[4]["symbol"], "w1": result[5]["symbol"],
                            "w2": result[6]["symbol"],
                            "w3": result[7]["symbol"]}})

    except Exception as e:
        # Handle exception
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()
    return jsonify(new_results if new_results else None)


@app.route('/insert_score', methods=['POST'])
def insert_score():
    """
    A function that inserts the score of a game, given a username, the user's score and the level they played.
    :return: Json.
    """
    user_name = request.json.get('username')
    score = request.json.get('score')
    level = request.json.get('level')

    formatted_time = (datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
    if user_name is None or score is None or level is None:
        return jsonify({'error': 'Missing parameters'}), 400

    connection = db_pool.get_connection()
    cursor = connection.cursor(dictionary=True)

    data = (user_name,)
    # Executing a query that returns a user's id, given the user's username.
    cursor.execute("SELECT user_id FROM user WHERE user_name = %s", data)
    result = cursor.fetchall()
    cursor.close()
    connection.close()

    data = (level, result[0]["user_id"], score, formatted_time,)

    # A query that inserts into the table score the difficulty og a game (which level was played), the user's id of the
    # user who was playing the game, the score of a game, and the date.
    query = """
                INSERT INTO score (difficulty, user_id, score, date) VALUES (%s, %s, %s, %s)
            """
    try:
        connection2 = db_pool.get_connection()
        cursor = connection2.cursor(dictionary=True)
        cursor.execute(query, data)
        connection2.commit()
        cursor.close()
        connection2.close()
        return jsonify({'success': 'score inserted'}), 200
    except Error as e:
        print(f"Error while inserting data: {e}")
        return jsonify({'error': 'problem'}), 400

@app.route('/cities/<country>', methods=['GET'])
def get_country_cities(country):
    """
    A functions that returns all the cities located in a country.
    :param country:
    :return:
    """

    # A query that returns all the cities in a given country (filtered by country's name and id).
    query = """SELECT city.city_name
               FROM city, country
               WHERE country.country_name = %s AND
                     city.country_id = country.country_id;"""

    data = (country,)
    connection = db_pool.get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(query, data)
        result = cursor.fetchall()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()
    return jsonify(result if result else None)



def helper(result):
    new_result = [{'country_name': result[0]['country_name'], 'country_id': result[0]['country_id']}]

    keys = ['capital', 'continent', 'number_of_cities', 'random_city', 'place_in_world_by_area', 'place_in_world_by_population']

    for key in keys:
        quiz = {f'{key}':{'correct_answer': result[0][key]}}
        for i, wrong_answer in enumerate(result[1:], start=1):
            quiz[f'{key}'][f'w{i}'] = wrong_answer[key]
        new_result.append(quiz)
    return new_result


def apply_query(query, params):
    """
    A generic function that executes a given SQL query.
    :param query: A string of a SQL query.
    :param params: Parameters for the SQL query (or () - no parameters).
    :return: list.
    """
    connection, cursor = None, None
    try:
        connection = db_pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params) if params else cursor.execute(query)
        result = cursor.fetchall()
        return result
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def get_random_countries():
    return apply_query(game_queries.random_countries_query, ())


def easy_questions(queries):
    result = get_random_countries()

    new_result = easy_questions_helper(result)  # first_batch

    new_keys = ['currency', 'city_not_in_country', 'growth_rate', 'number_of_states']
    keys = ['currency_name', 'city_name', 'growth_avg', 'counter_states']

    for i, query in enumerate(queries):
        connection = db_pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        data = (new_result[0]['country_id'], new_result[0]['country_id'])
        try:
            cursor.execute(query, data)
            result = cursor.fetchall()
            quiz = {f'{new_keys[i]}': {'correct_answer': result[0][keys[i]]}}
            for j, wrong_answer in enumerate(result[1:], start=1):
                quiz[f'{new_keys[i]}'][f'w{j}'] = wrong_answer[keys[i]]
            new_result.append(quiz)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            cursor.close()
            connection.close()

    return jsonify(new_result if new_result else None)


def get_random_countries_per_continent(continent):
    """
    A function that returns a list of nine random countries in a continent.
    :param continent: A string. Could be one of the following: 'Africa', 'Americas', 'Asia', 'Europe' or 'Oceania'.
    :return: list.
    """
    return apply_query(game_queries.random_countries_per_continent_query, (continent,))


def medium_questions(queries):
    """
    A function that returns all the questions asked in the game in the medium level.
    :param queries: A list of strings. Each string is a SQL query.
    :return: Json (consisting of a question, correct answer, and three other wrong answers).
    """
    continents = ['Africa', 'Americas', 'Asia', 'Europe', 'Oceania']
    continent = random.choice(continents)
    result = get_random_countries_per_continent(continent)

    if 'error' in result:
        return jsonify(None)

    first_batch = medium_questions_first_helper(result, continent)
    second_batch = medium_questions_second_helper(result, game_queries.easy_queries)
    third_batch = medium_questions_third_helper(continent, queries)

    questions = first_batch + second_batch + third_batch
    return jsonify(questions if questions else None)


@app.route('/medium_questions', methods=['GET'])
def get_medium_questions():
    """
    A function that is called when client needs questions of the medium level.
    Returns a list of questions (in Json format).
    :return: Json.
    """
    return medium_questions(game_queries.medium_queries)


def easy_questions_helper(result):
    new_result = [{'country_name': result[0]['country_name'], 'country_id': result[0]['country_id']}]
    keys = ['capital', 'continent', 'number_of_cities', 'random_city', 'place_in_world_by_area',
            'place_in_world_by_population']

    for key in keys:
        quiz = {f'{key}': {'correct_answer': result[0][key]}}
        for i, wrong_answer in enumerate(result[1:], start=1):
            quiz[f'{key}'][f'w{i}'] = wrong_answer[key]
        new_result.append(quiz)
    return new_result


def medium_questions_first_helper(result, continent):
    """
    A function that returns a list of 5 questions, that each one consists of one correct answer and three other wrong
    answer. Each question is about a random country (picked from the 9 available) in the (known) continent.
    :param continent: The value of the current continent.
    :param result: The returns value of random_countries_per_continent_query query, which returns data of 9 countries
    in a known continent.
    :return: list.
    """

    new_result = []
    questions = [
        'What is the capital of {}?',
        'How many cities are there in {}?',
        'Which city belong to {}?',
        '{} is the _th largest country in ' + str(continent) + ' (in terms of area):',
        '{} is the _th most populated country in ' + str(continent) + ' (in terms of population in 2022):'
    ]
    keys = ['capital', 'number_of_cities', 'random_city', 'place_in_continent_by_area',
            'place_in_continent_by_population']

    for key, q in zip(keys, questions):
        correct_answer = random.choice(result)
        wrong_answers = random.sample([elm for elm in result if elm != correct_answer], 3)

        correct_country = correct_answer['country_name']
        correct_key = correct_answer[key]

        question = q.format(correct_country)

        quiz = {f'{question}': {
            'correct_answer': f'{correct_key}'
        }}

        for i, wrong_answer in enumerate(wrong_answers, start=1):
            quiz[f'{question}'][f'w{i}'] = wrong_answer[key]
        new_result.append(quiz)
    return new_result


def medium_questions_second_helper(result, queries):
    """
    A function that returns a list of 4 questions, that each one consists of one correct answer and three other wrong
    answer. Each question is the result of one of the medium level queries - game_queries.medium_queries.
    :param result: The returns value of random_countries_per_continent_query query, which returns data of 9 countries
    in a known continent.
    :param queries: A list of strings. Each string is a SQL query (game_queries.easy_queries).
    :return: list.
    """

    new_result = []
    questions = [
        'What is the currency of {}?',
        'Which of the following cities are not located in {}?',
        'How many times did the population of {} increase from 1970 to 2022?',
        'How many states are there in {}?'
    ]
    keys = ['currency_name', 'city_name', 'growth_avg', 'counter_states']

    for i, query in enumerate(queries):
        key = keys[i]

        correct_answer = random.choice(result)
        correct_country = correct_answer['country_name']
        correct_country_id = correct_answer['country_id']

        params = (correct_country_id, correct_country_id)
        res = apply_query(query, params)

        if 'error' in res:
            return None

        correct_key = res[0][key]
        question = questions[i].format(correct_country)

        quiz = {f'{question}': {
            'correct_answer': f'{correct_key}'
        }}

        for j, wrong_answer in enumerate(res[1:], start=1):
            quiz[f'{question}'][f'w{j}'] = wrong_answer[key]
        new_result.append(quiz)
    return new_result


def medium_questions_third_helper(continent, queries):
    """
    A function that returns a list of 4 questions, that each one consists of one correct answer and three other wrong
    answer. Each question is the result of one of the medium level queries - game_queries.medium_queries.
    :param continent: A string. Could be one of the following: 'Africa', 'Americas', 'Asia', 'Europe' or 'Oceania'.
    :param queries: A list of strings. Each string is a SQL query (game_queries.easy_queries).
    :return: list.
    """
    new_result = []

    questions = [
        f'How many countries are there in {continent}?',
        f'Which country in {continent} has the largest number of cities?',
        f'Which country in {continent} has the largest number of states?',
        f'Which country in {continent} is the largest (in terms of area)?'
    ]
    keys = ['country_count', 'c_name_city', 'c_name_state', 'country_name']

    for i, (query, key) in enumerate(zip(queries, keys)):
        params = (continent, continent) if key == 'country_count' else (continent, continent, continent)
        res = apply_query(query, params)

        if 'error' in res:
            return None

        question = questions[i]
        correct_answer = res[0]
        correct_key = correct_answer[key]

        quiz = {f'{question}': {'correct_answer': f'{correct_key}'}}

        for j, wrong_answer in enumerate(res[1:], start=1):
            quiz[f'{question}'][f'w{j}'] = wrong_answer[key]
        new_result.append(quiz)

        if key == 'c_name_city' or key == 'c_name_state':
            count_key = 'city_count_continent' if key == 'c_name_city' else 'state_count_continent'

            plural_city = 'cities' if correct_key != '1' else 'city'
            plural_state = 'states' if correct_key != '1' else 'state'

            question = (f'How many {plural_city} has the largest country (largest in terms of number of {plural_city}) '
                        f'in {continent}?' if key == 'c_name_city'
                        else
                        f'How many {plural_state} has the largest country (largest in terms of number of {plural_state})'
                        f' in {continent}?')

            correct_key = correct_answer[count_key]
            quiz = {f'{question}': {'correct_answer': f'{correct_key}'}}

            for j, wrong_answer in enumerate(res[1:], start=1):
                quiz[f'{question}'][f'w{j}'] = wrong_answer[count_key]
            new_result.append(quiz)
    return new_result


if __name__ == '__main__':
    app.run()
