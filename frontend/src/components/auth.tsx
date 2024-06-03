import { SyntheticEvent, useState } from "react";

// const API_URL = 'https://localhost:8080/api/';

function getCookie(name: string) {
    let cookieValue = "";
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function LoginForm() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  function handleSubmit(event: SyntheticEvent) {
    event.preventDefault();
    var csrftoken = getCookie('csrftoken');
    fetch("http://localhost:8000/api/v0/auth/login/",
        {
            mode: "cors",
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "http://localhost:5731",
                "X-CSRFToken": csrftoken,
            },
            credentials: "include",
            body: JSON.stringify({username, password }),
        }
    )
    .then((response) => response.json())
    .then((data) => console.log(data));
  }
  return (
    <form className="login" onSubmit={handleSubmit}>
      <label htmlFor="username">Username:</label>
      <input id="username" type="text" value={username} onChange={({ target }) => setUsername(target.value)} />
      <label htmlFor="password">Password:</label>
      <input id="password" type="password" value={password} onChange={({ target }) => setPassword(target.value)} />
      <button type="submit">Login</button>
    </form>
  )
}

export default LoginForm
