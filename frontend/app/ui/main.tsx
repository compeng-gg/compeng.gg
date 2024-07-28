function Main({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <main className="container mx-auto p-4 space-y-4">
      {children}
    </main>
  );
}

export default Main;
