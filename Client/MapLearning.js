import React, { useState } from "react";
import NavBar from "./Navbar";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Modal from "react-bootstrap/Modal";
import { fetchCountryData, fetchCitiesAndShowModal } from "./api";

import { ComposableMap, Geographies, Geography } from "react-simple-maps";

function MapLearning() {
  const [showData, setData] = useState(false);
  const [countryName, setCountryName] = useState("");
  const [capitalName, setCapitalName] = useState("");
  const [population, setPopulation] = useState("");
  const [currencyName, setCrrencyName] = useState("");
  const [continent, setContinent] = useState("");
  const [area, setArea] = useState("");
  const [averageGrowthRate, setAverageGrowthRate] = useState("");
  const [numberOfCities, setNumberOfCities] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [citiesList, setCitiesList] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [errorMsg, setErrorMsg] = useState("Press on coutries to learn!");

  function updateValues(response, country) {
    if (response != null) {
      setCountryName(response["country_name"]);
      setCapitalName(response["capital_name"]);
      setPopulation(response["population"]);
      setCrrencyName(response["currency_name"]);
      setArea(response["country_area"]);
      setContinent(response["continent"]);
      setAverageGrowthRate(response["avg_increase_rate"]);
      setNumberOfCities(response["number_of_cities"]);
      setData(true);
    } else {
      setData(false);
      setErrorMsg(`Sorry, we dont have information about ${country}`);
    }
  }

  const filteredCities = citiesList.filter((city) =>
    city[0].toLowerCase().startsWith(searchQuery.toLowerCase())
  );

  return (
    <div>
      <NavBar />
      {showData ? (
        <Container style={{ textAlign: "center" }}>
          <h1>{countryName}</h1>
          <Row>
            <Col>
              <h4>Avg Growth rate: {averageGrowthRate}%</h4>
            </Col>
            <Col>
              <h4>Capital: {capitalName}</h4>
            </Col>
            <Col>
              <h4>Population: {population.toLocaleString()}</h4>
            </Col>
          </Row>
          <Row>
            <Col>
              <h4>Number of cities: {numberOfCities.toLocaleString()}</h4>
            </Col>
            <Col>
              <h4>Continent: {continent}</h4>
            </Col>
            <Col>
              <h4>Area(km²): {area.toLocaleString()}</h4>
            </Col>
          </Row>
          <Row>
            <Col>
              <h4>Currency: {currencyName}</h4>
            </Col>
          </Row>
          <Row>
            <Col>
              <button
                onClick={() => {
                  fetchCitiesAndShowModal(countryName).then((v) => {
                    setCitiesList(v);
                    setShowModal(true);
                  });
                }}
              >
                Show Cities
              </button>
            </Col>
          </Row>
        </Container>
      ) : (
        <h4 style={{ textAlign: "center" }}>{errorMsg}</h4>
      )}
      <ComposableMap>
        <Geographies geography="/features.json">
          {({ geographies }) =>
            geographies.map((geo) => (
              <Geography
                onClick={() => {
                  fetchCountryData(geo.properties.name).then((v) =>
                    updateValues(v, geo.properties.name)
                  );
                }}
                key={geo.rsmKey}
                geography={geo}
                stroke="#000000"
                style={{
                  default: {
                    fill: "gray",
                    outline: "none",
                  },
                  hover: {
                    fill: "#F53",
                    outline: "none",
                  },
                  pressed: {
                    fill: "#E42",
                    outline: "none",
                  },
                }}
              />
            ))
          }
        </Geographies>
      </ComposableMap>
      <Modal show={showModal} onHide={() => setShowModal(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title>Cities in {countryName}</Modal.Title>
        </Modal.Header>
        <input
          type="text"
          placeholder="Search cities..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        <Modal.Body>
          <ul>
            {filteredCities.map((city, index) => (
              <li key={index}>{city}</li>
            ))}
          </ul>
        </Modal.Body>
      </Modal>
    </div>
  );
}

export default MapLearning;
