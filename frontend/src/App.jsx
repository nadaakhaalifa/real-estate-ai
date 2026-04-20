import UploadBox from "./components/UploadBox";

function App() {
  return (
    <div className="min-h-screen bg-slate-950 px-4 py-10 text-white">
      <div className="mx-auto flex max-w-6xl flex-col items-center">
        <h1 className="mb-3 text-center text-4xl font-bold">
          Excel Data Review Platform
        </h1>

        <p className="mb-10 text-center text-slate-300">
          Upload your sheet, review the extracted data, and export the result.
        </p>

        <UploadBox />
      </div>
    </div>
  );
}

export default App;