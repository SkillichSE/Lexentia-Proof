const providerRows = [
  { name: "openai-compatible", byok: "yes", runtime: "client" },
  { name: "groq", byok: "yes", runtime: "client" },
  { name: "openrouter", byok: "yes", runtime: "client" }
];

export default function ProvidersPage() {
  return (
    <div className="klyxe-container py-10">
      <h1 className="mb-6 text-2xl font-bold">providers</h1>
      <div className="overflow-hidden rounded-xl border border-zinc-800">
        <table className="w-full text-left text-sm">
          <thead className="bg-zinc-900 text-zinc-300">
            <tr>
              <th className="px-3 py-2">provider</th>
              <th className="px-3 py-2">byok</th>
              <th className="px-3 py-2">runtime</th>
            </tr>
          </thead>
          <tbody>
            {providerRows.map((row) => (
              <tr key={row.name} className="border-t border-zinc-800">
                <td className="px-3 py-2">{row.name}</td>
                <td className="px-3 py-2">{row.byok}</td>
                <td className="px-3 py-2">{row.runtime}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
