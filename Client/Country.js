import React, { useState } from "react";
import Modal from "react-bootstrap/Modal";
import { fetchCitiesAndShowModal } from "./api";

function Country({ country }) {
  const [showModal, setShowModal] = useState(false);
  const [citiesList, setCitiesList] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");

  const filteredCities = citiesList.filter((city) =>
    city[0].toLowerCase().startsWith(searchQuery.toLowerCase())
  );

  return (
    <>
      <div style={{ textAlign: "center" }}>
        <h1>Country Name: {country["country_name"]}</h1>
        <h4>Capital Name: {country["capital_name"]}</h4>
        <h4>Population: {country["population_2022"].toLocaleString()}</h4>
        <h4>Currency: {country["currency_name"]}</h4>
        <h4>Area(km²): {country["country_area"].toLocaleString()}</h4>
        <h4>Continent: {country["continent"]}</h4>
        <h4>
          Number of cities: {country["number_of_cities"].toLocaleString()}
        </h4>
        <h4>Avg Growth rate: {country["avg_increase_rate"]}%</h4>
        <button
          onClick={() => {
            fetchCitiesAndShowModal(country["country_name"]).then((v) => {
              setCitiesList(v);
              setShowModal(true);
            });
          }}
        >
          Show Cities
        </button>
      </div>
      <Modal show={showModal} onHide={() => setShowModal(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title>Cities in {country["country_name"]}</Modal.Title>
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
    </>
  );
}

export default Country;
