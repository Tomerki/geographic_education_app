const BASE_URL = "http://localhost:5000";
export async function fetchCountryData(countryName) {
  let res = await fetch(`${BASE_URL}/country/${countryName}`);
  if (!res.ok) {
    return null;
  }
  return res.json();
}

export async function fetchCitiesAndShowModal(countryName) {
  let res = await fetch(`${BASE_URL}/cities/${countryName}`);
  if (!res.ok) {
    throw new Error("Network response was not ok fetchCitiesAndShowModal");
  }
  return res.json();
}

export async function getCountries(param) {
  let url = new URL(`${BASE_URL}/country`);

  if (param !== "") {
    url.searchParams.append("s", param);
  }

  let res = await fetch(url);
  if (!res.ok) {
    throw new Error("Network response was not ok getCountries");
  }
  const data = await res.json();
  return data || [];
}

export async function fetchUserCountryData(username) {
  let res = await fetch(`${BASE_URL}/user/${username}`);
  if (!res.ok) {
    throw new Error("Network response was not ok fetchUserCountryData");
  }
  return res.json();
}

export async function fetchUserScoreData(username) {
  let res = await fetch(`${BASE_URL}/scores/${username}`);
  if (!res.ok) {
    throw new Error("Network response was not ok fetchUserScoreData");
  }
  return res.json();
}

export async function fetchUserAccomplishments(username) {
  let res = await fetch(`${BASE_URL}/accomplishments/${username}`);
  if (!res.ok) {
    throw new Error("Network response was not ok fetchUserAccomplishments");
  }
  return res.json();
}

export async function fetchMaxScores() {
  let res = await fetch(`${BASE_URL}/max_score`);
  if (!res.ok) {
    return "";
    // throw new Error("Network response was not ok fetchMaxScores");
  }
  return res.json();
}

export async function fetch_user(username, password) {
  const userData = { username: username, password: password }; // Create an object with the username and password

  const response = await fetch(`${BASE_URL}/user`, {
    method: "POST", // Specify the HTTP method as POST
    headers: {
      "Content-Type": "application/json", // Set the Content-Type header
    },
    body: JSON.stringify(userData), // Convert the data object to JSON string and send it in the body
  });
  return response;
}

export async function fetchEasy() {
  const res = await fetch(`${BASE_URL}/questions`);
  if (!res.ok) {
    throw new Error("Network response was not ok fetchEasy");
  }

  return res.json();
}

export async function insert_score(score, level) {
  const userData = {
    username: localStorage.getItem("username"),
    score: score,
    level: level,
  }; // Create an object with the username and password

  await fetch(`${BASE_URL}/insert_score`, {
    method: "POST", // Specify the HTTP method as POST
    headers: {
      "Content-Type": "application/json", // Set the Content-Type header
    },
    body: JSON.stringify(userData), // Convert the data object to JSON string and send it in the body
  });
}

export async function fetchHard() {
  const res = await fetch(`${BASE_URL}/hard_questions`);
  if (!res.ok) {
    throw new Error("Network response was not ok fetchHard");
  }
  return res.json();
}

export async function fetchMedium() {
  const res = await fetch(`${BASE_URL}/medium_questions`);

  if (!res.ok) {
    throw new Error("Network response was not ok fetcMedium");
  }

  return res.json();
}
