import React, { useState } from "react";
import "./css/Home.css";
import NavBar from "./Navbar";
import { Link } from "react-router-dom";

function Play() {
  const [level, setLevel] = useState("");
  if (level === "") {
    return (
      <>
        <NavBar />
        <div className="home">
          <div className="home_page">
            <div className="home_body">
              <h1 className="home_title">Games Area</h1>
              <h2>Click on the Level you want to play </h2>
              <div>
                <button
                  type="button"
                  class="btn btn-dark"
                  onClick={() => setLevel("Easy")}
                >
                  Easy
                </button>

                <span className="button-space"></span>
                <button
                  type="button"
                  class="btn btn-dark"
                  onClick={() => setLevel("Medium")}
                >
                  Medium
                </button>

                <span className="button-space"></span>

                <button
                  type="button"
                  class="btn btn-dark"
                  onClick={() => setLevel("Hard")}
                >
                  Hard
                </button>
              </div>
            </div>
          </div>
        </div>
      </>
    );
  } else if (level === "Easy") {
    return (
      <>
        <NavBar />
        <div className="home">
          <div className="home_page">
            <div className="home_body">
              <h1 className="home_title">Games Area</h1>
              <h2>Level : {level}</h2>
              <div>
                <Link to="/easy">
                  <button type="button" class="btn btn-primary">
                    Start
                  </button>
                </Link>

                <span className="button-space"></span>

                <button
                  type="button"
                  class="btn btn-secondary"
                  onClick={() => setLevel("")}
                >
                  Choose a different level
                </button>
              </div>
            </div>
          </div>
        </div>
      </>
    );
  } else if (level === "Hard") {
    return (
      <>
        <NavBar />
        <div className="home">
          <div className="home_page">
            <div className="home_body">
              <h1 className="home_title">Games Area</h1>
              <h2>Level : {level}</h2>
              <div>
                <Link to="/hard">
                  <button type="button" class="btn btn-primary">
                    Start
                  </button>
                </Link>

                <span className="button-space"></span>

                <button
                  type="button"
                  class="btn btn-secondary"
                  onClick={() => setLevel("")}
                >
                  Choose a different level
                </button>
              </div>
            </div>
          </div>
        </div>
      </>
    );
  } else if (level === "Medium") {
    return (
      <>
        <NavBar />
        <div className="home">
          <div className="home_page">
            <div className="home_body">
              <h1 className="home_title">Games Area</h1>
              <h2>Level : {level}</h2>
              <div>
                <Link to="/medium">
                  <button type="button" class="btn btn-primary">
                    Start
                  </button>
                </Link>

                <span className="button-space"></span>

                <button
                  type="button"
                  class="btn btn-secondary"
                  onClick={() => setLevel("")}
                >
                  Choose a different level
                </button>
              </div>
            </div>
          </div>
        </div>
      </>
    );
  }
}

export default Play;
