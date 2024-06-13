export default function Page({username}: {username: string}) {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="mb-4 font-black text-5xl">@{username} Settings</h1>
    </main>
  );
}
