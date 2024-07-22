import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import NavBar from "./Navbar";
import { fetchEasy, insert_score } from "./api";

function EasyQuiz() {
  const [countryData, setCountryData] = useState([]);
  const [questions, setQuestions] = useState({});
  const [answers, setAnswers] = useState([]);
  const [currentAnswers, setCurrentAnswers] = useState([]);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [endGame, setEndGame] = useState(false);

  useEffect(() => {
    fetchEasy().then((value) => {
      const country_name = value[0]["country_name"];
      let temp_question = {
        capital: "What is the capital of " + country_name + "?",
        continent: "On which continent is " + country_name + "?",
        number_of_cities: "How many cisites there are in " + country_name + "?",
        random_city: "Which city is belong to " + country_name + "?",
        place_in_world_by_area:
          country_name + " is the _th largest in terms of area",
        place_in_world_by_population:
          country_name + " is the _th largest in terms of population on 2022",
        currency: "What is the currency of " + country_name + "?",
        city_not_in_country:
          "Which of the following cities is not in " + country_name + "?",
        growth_rate:
          "How many times has the population increased from 1970 to 2022 in " +
          country_name +
          "?",
        number_of_states: "How many states there are in " + country_name + "?",
      };

      let temp_answer = {
        capital: [],
        continent: [],
        number_of_cities: [],
        random_city: [],
        place_in_world_by_area: [],
        place_in_world_by_population: [],
        currency: [],
        city_not_in_country: [],
        growth_rate: [],
        number_of_states: [],
      };

      let temp_current_answer = {
        capital: [],
        continent: [],
        number_of_cities: [],
        random_city: [],
        place_in_world_by_area: [],
        place_in_world_by_population: [],
        currency: [],
        city_not_in_country: [],
        growth_rate: [],
        number_of_states: [],
      };

      value.forEach((item) => {
        Object.keys(item).forEach((key) => {
          if (temp_answer.hasOwnProperty(key) && item[key] !== undefined) {
            // Check if the item[key] is an object and has the structure we expect
            if (typeof item[key] === "object" && item[key] !== null) {
              // Push all values (correct and wrong answers) from the object to the array
              temp_answer[key].push({ 10: item[key].correct_answer });
              temp_answer[key].push({ 0: item[key].w1 });
              temp_answer[key].push({ 0: item[key].w2 });
              temp_answer[key].push({ 0: item[key].w3 });
              temp_current_answer[key].push(item[key].correct_answer);
              shuffleOptions(temp_answer[key]);
            }
          }
        });
      });

      setCountryData(value);
      setQuestions(temp_question);
      setAnswers(temp_answer);
      setCurrentAnswers(temp_current_answer);
    });
  }, []);

  const shuffleOptions = (options) => {
    for (let i = options.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [options[i], options[j]] = [options[j], options[i]];
    }
    return options;
  };

  const handleOptionChange = (questionKey, value) => {
    setSelectedAnswers({
      ...selectedAnswers,
      [questionKey]: value,
    });
  };

  const calculateScore = () => {
    let score = 0;
    Object.keys(selectedAnswers).forEach((key) => {
      score += parseInt(selectedAnswers[key]);
    });
    return score;
  };

  if (countryData.length === 0) {
    return (
      <>
        <div className="home">
          <div className="home_page">
            <div className="home_body">
              <h1 className="home_title"> Loading... </h1>
            </div>
          </div>
        </div>
      </>
    );
  } else if (endGame === true) {
    return (
      <>
        <NavBar />
        <div className="home">
          <div className="home_page">
            <div className="home_body">
              <h1 className="home_title">
                {" "}
                Your score is: {calculateScore()}{" "}
              </h1>
              <br></br>
              <form>
                {Object.keys(questions).map((key) => (
                  <>
                    <h3>
                      {questions[key]} : {currentAnswers[key]}
                    </h3>
                  </>
                ))}
              </form>
              <Link to="/games">
                <button type="button" class="btn btn-dark">
                  go back to game's area
                </button>
              </Link>
            </div>
          </div>
        </div>
      </>
    );
  } else {
    return (
      <>
        <NavBar />
        <div className="home">
          <div className="home_page">
            <div className="home_body">
              <form>
                {Object.keys(questions).map((key) => (
                  <>
                    <h2>{questions[key]}</h2>
                    {answers[key].map((option, optionIndex) => (
                      <div className="form-check" key={optionIndex}>
                        <input
                          className="form-check-input"
                          type="radio"
                          name={`flexRadioDefault_${key}`}
                          id={`flexRadioDefault_${key}_${optionIndex}`}
                          value={Object.keys(option)[0]}
                          onChange={() =>
                            handleOptionChange(key, Object.keys(option)[0])
                          }
                        />
                        <label
                          className="form-check-label"
                          htmlFor={`flexRadioDefault_${key}_${optionIndex}`}
                        >
                          {Object.values(option)[0]}
                        </label>
                      </div>
                    ))}
                  </>
                ))}
              </form>
              <button
                type="button"
                class="btn btn-dark"
                onClick={async () => {
                  await insert_score(calculateScore(), 1);
                  setEndGame(() => true);
                }}
              >
                Send
              </button>
            </div>
          </div>
        </div>
      </>
    );
  }
}

export default EasyQuiz;
