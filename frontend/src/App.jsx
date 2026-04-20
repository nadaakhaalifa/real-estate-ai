import { useState } from "react";
import api from "./api/client";

function App() {
  const [message, setMessage] = useState("");

  async function testBackend() {
    try {
      const response = await api.get("/health");
      setMessage(response.data.status);
    } catch (error) {
      setMessage("backend connection failed");
    }
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 bg-slate-950 text-white">
      <h1 className="text-3xl font-bold">Frontend Connected 🚀</h1>

      <button
        onClick={testBackend}
        className="rounded-xl bg-cyan-400 px-6 py-3 font-semibold text-black"
      >
        Test Backend
      </button>

      <p className="text-lg">{message}</p>
    </div>
  );
}

export default App;