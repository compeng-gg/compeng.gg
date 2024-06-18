'use client';

import { useState, useContext, FormEvent } from "react";
import { useRouter } from 'next/navigation'
import { JwtContext } from '@/app/lib/jwt-provider';
import { fetchApiSingle, jwtObtainPairEndpoint } from "@/app/lib/api";

function LoginForm() {
  const [jwt, setAndStoreJwt] = useContext(JwtContext);

  const [error, setError] = useState<string | null>(null);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    try {
      const response = await fetchApiSingle(jwtObtainPairEndpoint, { username, password });
      const data = await response.json();
      if (response.ok) {
        setAndStoreJwt(data);
      }
      else {
        setError(data.detail);
      }
    }
    catch (err) {
      setError("An unexpected error occurred");
    }
  }

  return (
    <div className="w-full max-w-xs">
      <form
        className="bg-gray-900 shadow-md rounded px-8 pt-6 pb-6 mb-4"
        onSubmit={handleSubmit}
      >
        {error && (
          <p className="text-red-500 text-xs font-bold mb-4">{error}</p>
        )}
        <div className="mb-4">
          <label
            className="block text-gray-100 text-sm font-bold mb-2"
            htmlFor="username"
          >
            Username
          </label>
          <input
            className="shadow appearance-none border border-gray-800 rounded w-full py-2 px-3 text-gray-100 bg-black leading-tight focus:outline-none focus:shadow-outline"
            id="username"
            type="text"
            autoComplete="username"
            autoCapitalize="none"
            value={username}
            onChange={({ target }) => setUsername(target.value)}
          />
        </div>
        <div className="mb-4">
          <label
            className="block text-gray-100 text-sm font-bold mb-2"
            htmlFor="password"
          >
            Password
          </label>
          <input
            className="shadow appearance-none border border-gray-800 rounded w-full py-2 px-3 text-gray-100 bg-black mb-3 leading-tight focus:outline-none focus:shadow-outline"
            id="password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={({ target }) => setPassword(target.value)}
          />
        </div>
        <div className="flex items-center justify-center">
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
