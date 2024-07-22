import React, { useEffect, useState } from "react";
import { Accordion, Card } from "react-bootstrap";
import { Link } from "react-router-dom";
import Country from "./Country";
import "./css/Home.css";
import NavBar from "./Navbar";
import { getCountries } from "./api";

function Study() {
  const [countriesArray, setCountriesArray] = useState([]);
  const [search, setSearch] = useState("");

  useEffect(() => {
    getCountries("").then((v) => setCountriesArray(v));
  }, []);

  useEffect(() => {
    getCountries(search).then((v) => setCountriesArray(v));
  }, [search]);

  return (
    <>
      <NavBar />
      <div className="home">
        <div className="home_page">
          <div className="home_body" style={{ textAlign: "center" }}>
            <h1 className="home_title">Study Area</h1>
            <Link to="/map">
              <button>Learn with map</button>
            </Link>
            <h2>Click on the country you would like to learn about</h2>
            <div>
              <form className="form-inline md-form mr-auto mb-4">
                <input
                  className="form-control mr-sm-2"
                  type="text"
                  placeholder="Search Country"
                  aria-label="Search"
                  value={search}
                  onChange={(e) => {
                    setSearch(e.target.value);
                  }}
                />
              </form>
            </div>
            <Accordion>
              {countriesArray.map((item, index) => (
                <Accordion.Item key={index} eventKey={index.toString()}>
                  <Accordion.Header>{item["country_name"]}</Accordion.Header>
                  <Accordion.Body collapsible="true">
                    <Card>
                      <Card.Body>
                        <Country country={item} />
                      </Card.Body>
                    </Card>
                  </Accordion.Body>
                </Accordion.Item>
              ))}
            </Accordion>
          </div>
        </div>
      </div>
    </>
  );
}

export default Study;
