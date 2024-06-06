'use client';

import { SyntheticEvent, useState } from "react";
import { useRouter } from 'next/navigation'

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

function fetchApi(input: string, data: any) {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v0';
  var csrftoken = getCookie('csrftoken');
  return fetch(apiUrl + input,
        {
            mode: "cors",
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "http://localhost:3000",
                "X-CSRFToken": csrftoken,
            },
            credentials: "include",
            body: JSON.stringify(data),
        }
  )
}

function LoginForm() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const router = useRouter();

  function handleSubmit(event: SyntheticEvent) {

    event.preventDefault();
    var csrftoken = getCookie('csrftoken');

    fetchApi("/auth/login", { username, password })
    .then((response) => response.json())
    .then((data) => console.log(data));
  
    fetchApi("/auth/session", { })
    .then((response) => response.json())
    .then((data) => console.log(data))
    .then(() => router.push('/test'));
  }

  return (
    <div className="w-full max-w-xs">
      <form className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4" onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="username">Username:</label>
          <input className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="username" type="text" value={username} onChange={({ target }) => setUsername(target.value)} />
        </div>
        <div className="mb-6">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="password">Password:</label>
          <input className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline" id="password" type="password" value={password} onChange={({ target }) => setPassword(target.value)} />
        </div>
        <div className="flex items-center justify-between">
          <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline" type="submit">Login</button>
        </div>
      </form>
    </div>
  )
}

export default LoginForm
