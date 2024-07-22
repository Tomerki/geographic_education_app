# First batch of EASY questions.
random_countries_query = """SELECT
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
                    (SELECT country_id, MAX(population) AS population FROM population GROUP BY country_id) p ON 
                    c.country_id = p.country_id
                GROUP BY 
                    c.country_id
            ) AS sq
            WHERE sq.continent_rank = 1
            ORDER BY RAND()
            LIMIT 4;"""


# First batch of MEDIUM questions.
# Returns nine random countries, and their data, from a specific continent.
random_countries_per_continent_query = """
SELECT c.country_name, c.country_id, ca.capital_name AS capital, c.continent,
       COUNT(ci.city_id) AS number_of_cities,
       (SELECT city_name FROM city WHERE country_id = c.country_id ORDER BY RAND() LIMIT 1) AS random_city,
       RANK() OVER (PARTITION BY c.continent ORDER BY c.country_area DESC) AS place_in_continent_by_area,
       RANK() OVER (PARTITION BY c.continent ORDER BY p.population DESC) AS place_in_continent_by_population
FROM country c
       JOIN capital ca ON c.country_id = ca.country_id
       JOIN city ci ON c.country_id = ci.country_id
       JOIN population p ON c.country_id = p.country_id
WHERE c.continent = %s
GROUP BY c.country_id, ca.capital_name, c.continent, p.population, c.country_area
ORDER BY RAND()
LIMIT 9;
"""


# A query that returns the currency, and it's symbol, of four countries (the first output will be treated as the right
# # answer - of one known country and 3 more random countries).
currency_query = """
(SELECT currency.currency_name, currency.symbol 
FROM country
    LEFT JOIN currency ON(country.currency_id = currency.currency_id)
WHERE country.country_id = %s) 
UNION 
(SELECT DISTINCT currency.currency_name, currency.symbol 
FROM currency
WHERE currency.currency_id NOT IN (
    SELECT currency.currency_id
    FROM country LEFT JOIN currency ON(country.currency_id = currency.currency_id) 
    WHERE country.country_id = %s)
ORDER BY RAND()
LIMIT 3);
"""

# A query that returns the id and name of four cities (of one known country and 3 more random countries).
city_query = """
(SELECT city.city_id, city.city_name
FROM city
WHERE city.country_id <> %s
ORDER BY RAND()
LIMIT 1)
UNION 
(SELECT DISTINCT city.city_id, city.city_name
FROM country
    LEFT JOIN city ON(country.country_id = city.country_id)
WHERE country.country_id = %s
ORDER BY RAND()
LIMIT 3);
"""

# A query that returns the average change in growth between the years of 2022 and 1970 of four countries (of one known
# country and 3 more random countries).
average_population_query = """
(SELECT (p1.population / p2.population) as growth_avg
FROM population p1
JOIN population p2 ON p1.country_id = p2.country_id
WHERE p1.country_id = %s
  AND p1.year = 2022
  AND p2.year = 1970)
UNION 
(SELECT DISTINCT (p3.population / p4.population) as growth_avg
FROM population p3
JOIN population p4 ON p3.country_id = p4.country_id
WHERE p3.country_id <> %s 
  AND p3.year = 2022
  AND p4.year = 1970
ORDER BY RAND()
LIMIT 3);
"""

# A query that returns the number of different state in a country of four countries (of one known country and 3 more
# random countries).
state_count_query = """
(SELECT COUNT(state.country_id), country_id as counter_states
FROM state 
WHERE state.country_id = %s
GROUP BY state.country_id)
UNION
(SELECT DISTINCT COUNT(state.country_id), country_id as counter_states
FROM state 
GROUP BY state.country_id
HAVING counter_states NOT IN (
    SELECT COUNT(state.country_id) as counter
    FROM state
    WHERE state.country_id = %s)
ORDER BY RAND()
LIMIT 3);
"""


# Returns the number of countries in a known continent, compared to three random continents.
countries_count_per_continent_query = """
(SELECT continent, COUNT(*) AS country_count
FROM country
WHERE continent = %s
GROUP BY continent)
UNION
(SELECT continent, COUNT(*) AS country_count
FROM country
WHERE continent <> %s
GROUP BY continent
ORDER BY RAND()
LIMIT 3);
"""


# Returns the country in the continent with the largest amount of cities, compared to three other random countries,
# with a lower (or equal) number of cities.
cities_count_per_continent_query = """
(SELECT c.country_id, c.country_name AS c_name_city, COUNT(ci.city_id) AS city_count_continent
FROM country c
JOIN city ci ON c.country_id = ci.country_id
WHERE c.continent = %s
GROUP BY c.country_id, c_name_city
ORDER BY city_count_continent DESC
LIMIT 1)
UNION
(SELECT c.country_id, c.country_name AS c_name_city, COUNT(ci.city_id) AS city_count_continent
FROM country c
JOIN city ci ON c.country_id = ci.country_id
WHERE c.continent = %s AND c.country_id != (
  SELECT cc.country_id
  FROM country cc
  JOIN city cit ON cc.country_id = cit.country_id
  WHERE cc.continent = %s
  GROUP BY cc.country_id
  ORDER BY COUNT(cit.city_id) DESC
  LIMIT 1
)
GROUP BY c.country_id, c_name_city
ORDER BY RAND()
LIMIT 3);
"""


# Returns the country in the continent with the largest amount of states, compared to three other random countries,
# with a lower (or equal) number of states.
states_count_per_continent_query = """
(SELECT c.country_id, c.country_name AS c_name_state, COUNT(s.state_id) AS state_count_continent
FROM country c
JOIN state s ON c.country_id = s.country_id
WHERE c.continent = %s
GROUP BY c.country_id, c_name_state
ORDER BY state_count_continent DESC
LIMIT 1)
UNION
(SELECT c.country_id, c.country_name AS c_name_state, COUNT(s.state_id) AS state_count_continent
FROM country c
JOIN state s ON c.country_id = s.country_id
WHERE c.continent = %s AND c.country_id != (
  SELECT cc.country_id
  FROM country cc
  JOIN state ss ON cc.country_id = ss.country_id
  WHERE cc.continent = %s
  GROUP BY cc.country_id
  ORDER BY COUNT(ss.state_id) DESC
  LIMIT 1
)
GROUP BY c.country_id, c_name_state
ORDER BY RAND()
LIMIT 3);
"""


# Returns the biggest country, in terms of area, in a continent, and three other random countries in the same continent.
country_size_per_continent = """
(SELECT country_id, country_name, country_area AS country_size
FROM country
WHERE continent = %s
ORDER BY country_area DESC
LIMIT 1)
UNION
(SELECT country_id, country_name, country_area AS country_size
FROM country
WHERE continent = %s AND country_id != (
  SELECT country_id
  FROM country
  WHERE continent = %s
  ORDER BY country_area DESC
  LIMIT 1
)
ORDER BY RAND()
LIMIT 3);
"""


easy_queries = [currency_query, city_query, average_population_query, state_count_query]
medium_queries = [countries_count_per_continent_query, cities_count_per_continent_query,
                  states_count_per_continent_query, country_size_per_continent]
hard_queries = []
