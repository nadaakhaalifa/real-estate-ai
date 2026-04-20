import { useState } from "react";
import UploadBox from "./components/UploadBox";
import api from "./api/client";

function App() {
  const [summaryData, setSummaryData] = useState(null);
  const [loadingSummary, setLoadingSummary] = useState(false);
  const [summaryError, setSummaryError] = useState("");

  const handleGetSummary = async () => {
    try {
      setLoadingSummary(true);
      setSummaryError("");

      const response = await api.get("/summary");
      setSummaryData(response.data);
    } catch (error) {
      console.error(error);
      setSummaryError("Failed to load summary.");
    } finally {
      setLoadingSummary(false);
    }
  };

  const formatCategory = (value) => {
    if (value === null || value === undefined || value === "") return "-";
    return `${value} bedroom${Number(value) > 1 ? "s" : ""}`;
  };

  const formatArea = (value) => {
    if (value === null || value === undefined || value === "") return "-";
    return `${Number(value).toLocaleString()} m²`;
  };

  const formatPrice = (value) => {
    if (value === null || value === undefined || value === "") return "-";
    return `${Number(value).toLocaleString()} EGP`;
  };

  return (
    <div className="min-h-screen bg-slate-950 px-4 py-10 text-white">
      <div className="mx-auto flex max-w-6xl flex-col items-center">
        <h1 className="mb-3 text-center text-4xl font-bold">
          Starting Price Report
        </h1>

        <p className="mb-10 text-center text-slate-300">
          Upload Excel files, generate the summary, and review starting price and starting area.
        </p>

        <UploadBox />

        <div className="mt-8 w-full max-w-6xl rounded-3xl border border-white/10 bg-white/5 p-6 shadow-xl backdrop-blur">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="text-xl font-semibold text-white">
                Summary Report
              </h2>
              <p className="mt-1 text-sm text-slate-300">
                Review the lowest starting price and starting area by project and category.
              </p>
            </div>

            <button
              onClick={handleGetSummary}
              disabled={loadingSummary}
              className="rounded-2xl bg-cyan-500 px-5 py-3 font-semibold text-white transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loadingSummary ? "Loading..." : "Generate Summary"}
            </button>
          </div>

          {summaryError && (
            <p className="mt-4 text-sm text-red-400">{summaryError}</p>
          )}

          {summaryData && (
            <div className="mt-6 rounded-2xl bg-slate-900/70 p-4">
              <div className="mb-6 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <p className="text-sm text-slate-300">
                  Total Units:{" "}
                  <span className="font-semibold text-white">
                    {summaryData.total_units}
                  </span>
                </p>

                <div className="rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1 text-xs font-medium text-cyan-300">
                  {summaryData.summary_rows.length} summary rows
                </div>
              </div>

              <div className="max-h-[600px] overflow-auto rounded-2xl border border-white/5">
                <table className="w-full border-collapse text-sm">
                  <thead className="sticky top-0 z-10 bg-slate-950/95 backdrop-blur">
                    <tr className="border-b border-slate-700 text-left text-slate-300">
                      <th className="p-4 font-semibold">Project</th>
                      <th className="p-4 font-semibold">Category</th>
                      <th className="p-4 font-semibold">Starting Price</th>
                      <th className="p-4 font-semibold">Starting Area</th>
                    </tr>
                  </thead>

                  <tbody>
                    {summaryData.summary_rows.map((row, index) => (
                      <tr
                        key={index}
                        className="border-b border-slate-800 transition hover:bg-slate-800/50"
                      >
                        <td className="p-4 font-semibold text-white">
                          {row.project_name || "-"}
                        </td>

                        <td className="p-4">
                          <span className="rounded-full bg-slate-800 px-3 py-1 text-xs font-medium text-slate-200">
                            {formatCategory(row.category_value)}
                          </span>
                        </td>

                        <td className="p-4 font-semibold text-cyan-300">
                          {formatPrice(row.starting_price)}
                        </td>

                        <td className="p-4 text-slate-300">
                          {formatArea(row.starting_area_m2)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;