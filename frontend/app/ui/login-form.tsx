'use client';

import { useState, FormEvent } from "react";
import { useRouter } from 'next/navigation'
import { fetchApi } from "@/app/lib/api-client";

function LoginForm() {
  const [error, setError] = useState<string | null>(null);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const router = useRouter();

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    try {
      const response = await fetchApi("/auth/login", { username, password });
      const data = await response.json();
      console.log(data);
      if (response.ok) {
        router.refresh();
      }
      else {
        if ("username" in data.errors) {
          setError(data.errors.username);
        }
        else if ("password" in data.errors) {
          setError(data.errors.password);
        }
        else {
          setError("An unexpected error occurred");
        }
      }
    }
    catch (err) {
      setError("An unexpected error occurred");
    }
  }

  return (
    <div className="w-full max-w-xs">
      <form
        className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4"
        onSubmit={handleSubmit}
      >
        {error && (
          <p className="text-red-500 text-xs font-bold mb-4">{error}</p>
        )}
        <div className="mb-4">
          <label
            className="block text-gray-700 text-sm font-bold mb-2"
            htmlFor="username"
          >
            Username
          </label>
          <input
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            id="username"
            type="text"
            autoComplete="username"
            autoCapitalize="none"
            value={username}
            onChange={({ target }) => setUsername(target.value)}
          />
        </div>
        <div className="mb-6">
          <label
            className="block text-gray-700 text-sm font-bold mb-2"
            htmlFor="password"
          >
            Password
          </label>
          <input
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline"
            id="password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={({ target }) => setPassword(target.value)}
          />
        </div>
        <div className="flex items-center justify-between">
          <button
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
            type="submit"
          >
            Login
          </button>
        </div>
      </form>
    </div>
  )
}

export default LoginForm
