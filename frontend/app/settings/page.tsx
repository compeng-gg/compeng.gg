import LoginRequired from '@/app/lib/login-required';
import DiscordButton from '@/app/ui/discord-button';

function SettingsPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="mb-4 font-black text-5xl">Settings</h1>
      <DiscordButton action="connect" />
    </main>
  );

}

export default function Page() {
  return (
    <LoginRequired>
      <SettingsPage />
    </LoginRequired>
  );
}
