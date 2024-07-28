'use client';

import { useState, useContext, FormEvent } from "react";
import { useRouter } from 'next/navigation'
import { JwtContext } from '@/app/lib/jwt-provider';
import { fetchApiSingle, jwtObtainPairEndpoint } from "@/app/lib/api";

import Button from '@/app/ui/button';

function LoginForm() {
  const [jwt, setAndStoreJwt] = useContext(JwtContext);

  const [error, setError] = useState<string | null>(null);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    try {
      const response = await fetchApiSingle(jwtObtainPairEndpoint, "POST", { username, password });
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
        className="bg-zinc-900 shadow-md rounded px-8 py-8 flex flex-col space-y-4"
        onSubmit={handleSubmit}
      >
        {error && (
          <p className="text-red-500 text-xs font-bold mb-4">{error}</p>
        )}
        <div>
          <label
            className="block text-zinc-100 text-sm font-bold mb-2"
            htmlFor="username"
          >
            Username
          </label>
          <input
            className="shadow appearance-none border border-zinc-800 rounded w-full py-2 px-3 text-zinc-100 bg-black leading-tight focus:outline-none focus:shadow-outline"
            id="username"
            type="text"
            autoComplete="username"
            autoCapitalize="none"
            value={username}
            onChange={({ target }) => setUsername(target.value)}
          />
        </div>
        <div>
          <label
            className="block text-zinc-100 text-sm font-bold mb-2"
            htmlFor="password"
          >
            Password
          </label>
          <input
            className="shadow appearance-none border border-zinc-800 rounded w-full py-2 px-3 text-zinc-100 bg-black leading-tight focus:outline-none focus:shadow-outline"
            id="password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={({ target }) => setPassword(target.value)}
          />
        </div>
          <Button kind="primary" type="submit">
            Login
          </Button>
      </form>
    </div>
  )
}

export default LoginForm
