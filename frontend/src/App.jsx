import { useMemo, useState } from "react";
import { ArrowUpDown, Search, SlidersHorizontal } from "lucide-react";
import UploadBox from "./components/UploadBox";
import api from "./api/client";

const API_URL = import.meta.env.VITE_API_URL;

function App() {
  const [summaryData, setSummaryData] = useState(null);
  const [loadingSummary, setLoadingSummary] = useState(false);
  const [summaryError, setSummaryError] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [sortConfig, setSortConfig] = useState({
    key: "project_name",
    direction: "asc",
  });

  const handleGetSummary = async (
    nextSearch = searchTerm,
    nextCategory = categoryFilter,
    nextSort = sortConfig
  ) => {
    try {
      setLoadingSummary(true);
      setSummaryError("");

      const response = await api.get("/summary", {
        params: {
          search: nextSearch,
          category: nextCategory,
          sort_key: nextSort.key,
          sort_direction: nextSort.direction,
        },
      });

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

  const categoryOptions = useMemo(() => {
    const rows = summaryData?.summary_rows || [];
    const values = rows
      .map((row) => row.category_value)
      .filter((value) => value !== null && value !== undefined && value !== "");

    return ["all", ...new Set(values.map(String))];
  }, [summaryData]);

  const exportQuery = new URLSearchParams({
    search: searchTerm,
    category: categoryFilter,
    sort_key: sortConfig.key,
    sort_direction: sortConfig.direction,
  }).toString();

  const handleSearchChange = async (e) => {
    const newValue = e.target.value;
    setSearchTerm(newValue);

    if (summaryData) {
      await handleGetSummary(newValue, categoryFilter, sortConfig);
    }
  };

  const handleCategoryChange = async (e) => {
    const newValue = e.target.value;
    setCategoryFilter(newValue);

    if (summaryData) {
      await handleGetSummary(searchTerm, newValue, sortConfig);
    }
  };

  const handleSort = async (key) => {
    const nextSort = {
      key,
      direction:
        sortConfig.key === key && sortConfig.direction === "asc" ? "desc" : "asc",
    };

    setSortConfig(nextSort);

    if (summaryData) {
      await handleGetSummary(searchTerm, categoryFilter, nextSort);
    }
  };

  const SortButton = ({ label, sortKey }) => (
    <button
      type="button"
      onClick={() => handleSort(sortKey)}
      className="group inline-flex items-center gap-2 font-semibold text-slate-300 transition hover:text-cyan-300"
    >
      <span>{label}</span>
      <ArrowUpDown className="h-4 w-4 transition group-hover:scale-110" />
    </button>
  );

  const SummarySkeleton = () => (
    <div className="mt-6 rounded-2xl bg-slate-900/70 p-4">
      <div className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="h-5 w-40 animate-pulse rounded bg-slate-800" />
        <div className="h-10 w-72 animate-pulse rounded-2xl bg-slate-800" />
      </div>

      <div className="mb-6 grid gap-3 sm:grid-cols-2">
        <div className="h-12 animate-pulse rounded-2xl bg-slate-800" />
        <div className="h-12 animate-pulse rounded-2xl bg-slate-800" />
      </div>

      <div className="overflow-hidden rounded-2xl border border-white/5">
        <div className="grid grid-cols-4 gap-4 border-b border-slate-800 bg-slate-950/95 p-4">
          <div className="h-4 animate-pulse rounded bg-slate-800" />
          <div className="h-4 animate-pulse rounded bg-slate-800" />
          <div className="h-4 animate-pulse rounded bg-slate-800" />
          <div className="h-4 animate-pulse rounded bg-slate-800" />
        </div>

        {Array.from({ length: 6 }).map((_, index) => (
          <div
            key={index}
            className="grid grid-cols-4 gap-4 border-b border-slate-800 p-4"
          >
            <div className="h-4 animate-pulse rounded bg-slate-800" />
            <div className="h-4 animate-pulse rounded bg-slate-800" />
            <div className="h-4 animate-pulse rounded bg-slate-800" />
            <div className="h-4 animate-pulse rounded bg-slate-800" />
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-slate-950 px-4 py-10 text-white">
      <div className="mx-auto flex max-w-6xl flex-col items-center">
        <h1 className="mb-3 text-center text-4xl font-bold">
          Real Estate Analysis Platform
        </h1>

        <p className="mb-10 text-center text-slate-300">
          Upload Excel files, generate the summary, and review starting price
          and starting area.
        </p>

        <UploadBox />

        <div className="mt-8 w-full max-w-6xl rounded-3xl border border-white/10 bg-white/5 p-6 shadow-xl backdrop-blur">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="text-xl font-semibold text-white">
                Summary Report
              </h2>
              <p className="mt-1 text-sm text-slate-300">
                Review the lowest starting price and starting area by project
                and category.
              </p>
            </div>

            <button
              onClick={() => handleGetSummary()}
              disabled={loadingSummary}
              className="rounded-2xl bg-cyan-500 px-5 py-3 font-semibold text-white transition duration-300 hover:scale-105 hover:bg-cyan-400 hover:shadow-lg hover:shadow-cyan-500/30 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loadingSummary ? "Loading..." : "Generate Summary"}
            </button>
          </div>

          {summaryError && (
            <p className="mt-4 text-sm text-red-400">{summaryError}</p>
          )}

          {loadingSummary && <SummarySkeleton />}

          {!loadingSummary && summaryData && (
            <div className="mt-6 rounded-2xl bg-slate-900/70 p-4">
              <div className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:gap-4">
                  <p className="text-sm text-slate-300">
                    Total Units:{" "}
                    <span className="font-semibold text-white">
                      {summaryData.total_units}
                    </span>
                  </p>

                  <div className="w-fit rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1 text-xs font-medium text-cyan-300">
                    {summaryData.summary_rows.length} visible rows
                  </div>
                </div>

                <div className="flex flex-col gap-3 sm:flex-row">
                  <a
                    href={`${API_URL}/summary/pdf?${exportQuery}`}
                    target="_blank"
                    rel="noreferrer"
                    className="group relative overflow-hidden rounded-2xl border border-white/10 bg-white/5 px-5 py-3 text-center font-semibold text-white transition-all duration-300 hover:scale-105"
                  >
                    <span className="relative z-10">Export PDF</span>
                    <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/0 via-cyan-500/40 to-cyan-500/0 opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
                    <div className="absolute inset-0 rounded-2xl border border-cyan-400/0 transition-all duration-300 group-hover:border-cyan-400/60" />
                  </a>

                  <a
                    href={`${API_URL}/summary/excel?${exportQuery}`}
                    className="group relative overflow-hidden rounded-2xl bg-gradient-to-r from-cyan-500 to-blue-500 px-5 py-3 text-center font-semibold text-white shadow-lg transition-all duration-300 hover:scale-105 hover:shadow-cyan-500/40"
                  >
                    <span className="relative z-10">Export Excel</span>
                    <div className="absolute left-[-100%] top-0 h-full w-full bg-white/20 transition-all duration-500 group-hover:left-[100%]" />
                  </a>
                </div>
              </div>

              <div className="mb-6 grid gap-3 md:grid-cols-2">
                <div className="relative">
                  <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                  <input
                    type="text"
                    placeholder="Search by project name..."
                    value={searchTerm}
                    onChange={handleSearchChange}
                    className="w-full rounded-2xl border border-white/10 bg-slate-950/80 py-3 pl-11 pr-4 text-sm text-white outline-none transition focus:border-cyan-400"
                  />
                </div>

                <div className="relative">
                  <SlidersHorizontal className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                  <select
                    value={categoryFilter}
                    onChange={handleCategoryChange}
                    className="w-full appearance-none rounded-2xl border border-white/10 bg-slate-950/80 py-3 pl-11 pr-4 text-sm text-white outline-none transition focus:border-cyan-400"
                  >
                    {categoryOptions.map((option) => (
                      <option key={option} value={option}>
                        {option === "all"
                          ? "All Categories"
                          : formatCategory(option)}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="max-h-[600px] overflow-auto rounded-2xl border border-white/5">
                <table className="w-full border-collapse text-sm">
                  <thead className="sticky top-0 z-10 bg-slate-950/95 backdrop-blur">
                    <tr className="border-b border-slate-700 text-left text-slate-300">
                      <th className="p-4">
                        <SortButton label="Project" sortKey="project_name" />
                      </th>
                      <th className="p-4">
                        <SortButton label="Category" sortKey="category_value" />
                      </th>
                      <th className="p-4">
                        <SortButton
                          label="Starting Price"
                          sortKey="starting_price"
                        />
                      </th>
                      <th className="p-4">
                        <SortButton
                          label="Starting Area"
                          sortKey="starting_area_m2"
                        />
                      </th>
                    </tr>
                  </thead>

                  <tbody>
                    {summaryData.summary_rows.length > 0 ? (
                      summaryData.summary_rows.map((row, index) => (
                        <tr
                          key={index}
                          className="border-b border-slate-800 transition duration-300 hover:bg-slate-800/60"
                        >
                          <td className="p-4 font-semibold text-white">
                            {row.project_name || "-"}
                          </td>

                          <td className="p-4">
                            <span className="rounded-full bg-slate-800 px-3 py-1 text-xs font-medium text-slate-200 transition hover:bg-cyan-500/20 hover:text-cyan-300">
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
                      ))
                    ) : (
                      <tr>
                        <td
                          colSpan="4"
                          className="p-8 text-center text-sm text-slate-400"
                        >
                          No matching rows found.
                        </td>
                      </tr>
                    )}
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