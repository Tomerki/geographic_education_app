import React, { useEffect, useState } from "react";
import "./css/Login.css";
import LoginModal from "./LoginModal";
import "./css/Modal.css";
import { fetch_user } from "./api";

function Login({ userSetter }) {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userName, setUserName] = useState("");
  const [password, setPassword] = useState("");
  const [openModel, setOpenModel] = useState(false);


  useEffect(() => {
    setIsLoggedIn(false);
    if (userName.length > 0 && password.length > 0) {
      setIsLoggedIn((bool) => (bool = true));
    }
  }, [userName, password]);

  return (
    <div className="login">
      <div className="allModals">
        {openModel && <LoginModal close_modal={setOpenModel} />}
      </div>
      <div className="login_page">
        <div className="login_body">
          <h1> Login </h1>
          <form id="loginForm" className="form">
            <div className="login_body_input">
              <input
                placeholder="Username"
                className="login_input"
                type="text"
                value={userName}
                onChange={(e) => {
                  setUserName(e.target.value);
                }}
              />
            </div>
            <div className="login_body_input">
              <input
                placeholder="Password"
                className="login_input"
                id="pass"
                type="password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                }}
              />
            </div>

            <div className="login_buttom">
              <input
                type="button"
                value="login"
                className="btn btn-outline-secondary"
                onClick={async () => {
                  if (isLoggedIn === false) {
                    setOpenModel(true);
                  }
                  let res = await fetch_user(userName, password);
                  let res_json = await res.json();
                  if (res.ok && res_json != null) {
                    localStorage.setItem("username", userName);
                    userSetter(userName);
                  } else {
                    setOpenModel(true);
                  }
                }}
              />
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default Login;
