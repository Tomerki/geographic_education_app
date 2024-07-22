import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import NavBar from "./Navbar";
import { fetchHard, insert_score } from "./api";

function HardQuiz() {
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState([]);
  const [currentAnswers, setCurrentAnswers] = useState([]);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [endGame, setEndGame] = useState(false);

  useEffect(() => {
    fetchHard().then((value) => {
      let temp_question = [];
      let temp_answer = {};
      let temp_current_answer = {};
      value.forEach((item) => {
        temp_question.push(item["question"]);
        temp_answer[item["question"]] = [];
        temp_answer[item["question"]].push({
          5: item["answers"].correct_answer,
        });
        temp_answer[item["question"]].push({ 0: item["answers"].w1 });
        temp_answer[item["question"]].push({ 0: item["answers"].w2 });
        temp_answer[item["question"]].push({ 0: item["answers"].w3 });
        temp_current_answer[item["question"]] = [];
        temp_current_answer[item["question"]].push(
          item["answers"].correct_answer
        );
        shuffleOptions(temp_answer[item["question"]]);
      });
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

  if (questions.length === 0) {
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
                {questions.map((question, questionIndex) => (
                  <>
                    <h3>
                      {question} {currentAnswers[question]}
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
                {questions.map((question, questionIndex) => (
                  <>
                    <h2>{question}</h2>
                    {answers[question].map((option, optionIndex) => (
                      <div className="form-check" key={optionIndex}>
                        <input
                          className="form-check-input"
                          type="radio"
                          name={`flexRadioDefault_${questionIndex}`}
                          id={`flexRadioDefault_${questionIndex}_${optionIndex}`}
                          value={Object.keys(option)[0]}
                          onChange={() =>
                            handleOptionChange(
                              questionIndex,
                              Object.keys(option)[0]
                            )
                          }
                        />
                        <label
                          className="form-check-label"
                          htmlFor={`flexRadioDefault_${question}_${optionIndex}`}
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
                  await insert_score(calculateScore(), 3);
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

export default HardQuiz;
