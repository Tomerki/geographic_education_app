import React, { useEffect, useState } from "react";
import "./css/Home.css";
import NavBar from "./Navbar";
import Plot from "react-plotly.js";
import {
  fetchUserCountryData,
  fetchUserScoreData,
  fetchUserAccomplishments,
  fetchMaxScores,
} from "./api";

function Home({ username }) {
  const [name, setName] = useState("");
  const [country, setCountry] = useState("");
  const [capital, setCapital] = useState("");
  const [currency, setCurrency] = useState("");
  const [symbol, setSymbol] = useState("");
  const [citiesNum, setCitiesNum] = useState("");
  const [continent, setContinent] = useState("");
  const [population2022, setPopulation2022] = useState("");
  const [scoresFirstLevel, setScoresFirstLevel] = useState([]);
  const [scoresSecondLevel, setScoresSecondLevel] = useState([]);
  const [scoresThirdLevel, setScoresThirdLevel] = useState([]);
  const [accomplishments, setAccomplishments] = useState([]);
  const [maxScores, setMaxScores] = useState([]);

  function updateUserData(res_json) {
    setName(res_json["name"]);
    setCountry(res_json["country_name"]);
    setContinent(res_json["continent"]);
    setCapital(res_json["capital_name"]);
    setCurrency(res_json["currency_name"]);
    setSymbol(res_json["symbol"]);
    setCitiesNum(res_json["city_counter"]);
    setPopulation2022(res_json["population_2022"]);
  }

  function updateUserScoreData(res_json) {
    setScoresFirstLevel(res_json[1]);
    setScoresSecondLevel(res_json[2]);
    setScoresThirdLevel(res_json[3]);
  }

  useEffect(() => {
    fetchUserCountryData(username).then((v) => updateUserData(v));
    fetchUserScoreData(username).then((v) => updateUserScoreData(v));
    fetchUserAccomplishments(username).then((v) => setAccomplishments(v));
    fetchMaxScores().then((v) => setMaxScores(v));
  }, [username]);

  const create_row = (array, index, level) => {
    return (
      <div className="row">
        <div className="col">
          <Plot
            data={processDataForPlotly(array)}
            layout={{
              width: 800,
              height: 400,
              title: "Score Progress Over last 30 days level: " + level,
              xaxis: { title: "Time", showticklabels: false },
              yaxis: { title: "Score" },
            }}
          />
        </div>
        <div className="col">
          {accomplishments[index] && (
            <>
              <h4>AVG score:</h4> {accomplishments[index]["avg"]}
              <br />
              <br />
              <h4>MAX score:</h4> {accomplishments[index]["max"]}
              <br />
              on {accomplishments[index]["date_of_max"]}
              <br />
              <br />
              <h4>Number of tries:</h4>
              {accomplishments[index]["tries"]}
            </>
          )}
        </div>
      </div>
    );
  };
  const processDataForPlotly = (level) => {
    const xData = level.map((entry) => entry.date);
    const yData = level.map((entry) => entry.score);

    return [
      {
        showline: false,
        zeroline: false,
        x: xData,
        y: yData,
        type: "scatter",
        mode: "lines+markers",
        name: "Score Progress",
      },
    ];
  };

  return (
    <>
      <NavBar />
      <div className="home">
        <div className="home_page">
          <div className="home_body">
            <h1 className="home_title"> Hello, {name}! </h1>
            <h2>
              For start, here are 5 nice facts about your country, {country}:
            </h2>
            <ol className="list-group list-group-numbered">
              <li className="list-group-item d-flex justify-content-between align-items-start">
                <div className="ms-2 me-auto">
                  <div className="fw-bold">Capital city: </div>
                  {capital} is the capital city of {country}.
                </div>
              </li>
              <li className="list-group-item d-flex justify-content-between align-items-start">
                <div className="ms-2 me-auto">
                  <div className="fw-bold">Currency: </div>
                  The currency of {country} is called "{currency}"{" "}
                  <p>and the symbol of the currency is: {symbol}.</p>
                </div>
              </li>
              <li className="list-group-item d-flex justify-content-between align-items-start">
                <div className="ms-2 me-auto">
                  <div className="fw-bold">continent: </div>
                  {country} is located on {continent} continent.
                </div>
              </li>
              <li className="list-group-item d-flex justify-content-between align-items-start">
                <div className="ms-2 me-auto">
                  <div className="fw-bold">Number of cities:</div>
                  {country} includes {citiesNum} cities.
                </div>
              </li>
              <li className="list-group-item d-flex justify-content-between align-items-start">
                <div className="ms-2 me-auto">
                  <div className="fw-bold">Population size in 2022:</div>
                  In 2022, {population2022.toLocaleString()} people lived in{" "}
                  {country}.
                </div>
              </li>
            </ol>
            <br></br>
            <h1> Global First Places Per Level, Today :</h1>
            <br></br>
            <div>
              <div>
                <h2>Global First Place on Easy Level- </h2>
                <h4>
                  {maxScores[1] &&
                    maxScores[1]["first_name"] +
                      " " +
                      maxScores[1]["last_name"] +
                      " (" +
                      maxScores[1]["user_name"] +
                      "), score: " +
                      maxScores[2]["max_score"]}
                </h4>
              </div>
              <div>
                <h2>Global First Place on Medium Level- </h2>
                <h4>
                  {maxScores[2] &&
                    maxScores[2]["first_name"] +
                      " " +
                      maxScores[2]["last_name"] +
                      " (" +
                      maxScores[2]["user_name"] +
                      "), score: " +
                      maxScores[2]["max_score"]}
                </h4>
              </div>
              <div>
                <h2>Global First Place on Hard Level- </h2>
                <h4>
                  {maxScores[3] &&
                    maxScores[3]["first_name"] +
                      " " +
                      maxScores[3]["last_name"] +
                      " (" +
                      maxScores[3]["user_name"] +
                      "), score: " +
                      maxScores[2]["max_score"]}
                </h4>
              </div>
            </div>
            <div>
              <br></br>
              <h2>Personal Score Progress Graph Per Level</h2>

              {create_row(scoresFirstLevel, 1, "Easy")}

              <br></br>
              {create_row(scoresSecondLevel, 2, "Medium")}

              <br></br>
              {create_row(scoresThirdLevel, 3, "Hard")}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default Home;
