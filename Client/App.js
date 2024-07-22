import React, { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./Login";
import Home from "./Home";
import "./css/App.css";
import Study from "./Study";
import EasyQuiz from "./EasyQuiz";
import HardQuiz from "./HardQuiz";
import MediumQuiz from "./MediumQuiz";
import Play from "./Play";
import MapLearning from "./MapLearning";

function App() {
  const storedUsername = localStorage.getItem("username");
  const [username, setUsername] = useState(storedUsername || "");

  const startApp = () => {
    if (username === "") {
      return (
        <BrowserRouter>
          <Routes>
            <Route
              path="/"
              element={<Login userSetter={setUsername} />}
            ></Route>
          </Routes>
        </BrowserRouter>
      );
    } else {
      return (
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Home username={username} />}></Route>
            <Route path="/study" element={<Study />}></Route>
            <Route path="/games" element={<Play />}></Route>
            <Route path="/easy" element={<EasyQuiz />}></Route>
            <Route path="/medium" element={<MediumQuiz />}></Route>
            <Route path="/hard" element={<HardQuiz />}></Route>
            <Route path="/map" element={<MapLearning />}></Route>
          </Routes>
        </BrowserRouter>
      );
    }
  };
  return startApp();
}

export default App;
