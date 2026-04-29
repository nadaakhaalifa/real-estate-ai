import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { UploadCloud, FileText, X } from "lucide-react";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL;

function UploadBox() {
  const [files, setFiles] = useState([]);
  const [status, setStatus] = useState("");
  const [uploaded, setUploaded] = useState(false);

  const onDrop = useCallback((acceptedFiles) => {
    setFiles((prevFiles) => {
      const newFiles = acceptedFiles.map((file) => ({
        file,
        displayName: file.name.replace(/\.(xlsx|xls)$/i, ""),
        isRenaming: false,
      }));

      const combinedFiles = [...prevFiles, ...newFiles];

      const uniqueFiles = combinedFiles.filter(
        (item, index, self) =>
          index === self.findIndex((f) => f.file.name === item.file.name)
      );

      return uniqueFiles.slice(0, 50);
    });

    setStatus("");
    setUploaded(false);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: true,
    maxFiles: 50,
    accept: {
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [
        ".xlsx",
      ],
      "application/vnd.ms-excel": [".xls"],
    },
  });

  const handleRename = (index, value) => {
    setFiles((prevFiles) =>
      prevFiles.map((item, fileIndex) =>
        fileIndex === index ? { ...item, displayName: value } : item
      )
    );

    setUploaded(false);
  };

  const toggleRename = (index) => {
    setFiles((prevFiles) =>
      prevFiles.map((item, fileIndex) =>
        fileIndex === index
          ? { ...item, isRenaming: !item.isRenaming }
          : item
      )
    );
  };

  const handleRemove = (index) => {
    setFiles((prevFiles) =>
      prevFiles.filter((_, fileIndex) => fileIndex !== index)
    );
    setUploaded(false);
    setStatus("");
  };

  const handleUpload = async () => {
    if (files.length === 0) {
      setStatus("Please select at least one Excel file.");
      return;
    }

    const hasEmptyName = files.some((item) => item.displayName.trim() === "");

    if (hasEmptyName) {
      setStatus("Please give every file a name before uploading.");
      return;
    }

    const formData = new FormData();

    files.forEach((item) => {
      formData.append("files", item.file);
      formData.append("display_names", item.displayName.trim());
    });

    try {
      setStatus("Uploading...");

      await axios.post(`${API_URL}/upload`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setUploaded(true);
      setStatus("Upload successful ✅");
    } catch (error) {
      console.error("Upload error:", error);
      console.error("Response data:", error.response?.data);
      console.error("Status:", error.response?.status);

      setUploaded(false);
      setStatus(
        error.response?.data?.detail
          ? `Upload failed ❌ ${error.response.data.detail}`
          : `Upload failed ❌ ${error.message}`
      );
    }
  };

  return (
    <div className="w-full max-w-4xl rounded-3xl border border-white/10 bg-white/5 p-6 shadow-xl backdrop-blur">
      <div
        {...getRootProps()}
        className={`cursor-pointer rounded-2xl border-2 border-dashed p-10 text-center transition ${
          isDragActive
            ? "border-cyan-400 bg-cyan-400/10"
            : "border-slate-600 hover:border-cyan-400 hover:bg-white/5"
        }`}
      >
        <input {...getInputProps()} />

        <div className="flex flex-col items-center gap-4">
          <UploadCloud className="h-12 w-12 text-cyan-300" />

          <div>
            <h2 className="text-xl font-semibold text-white">
              Upload Excel Files
            </h2>

            <p className="mt-2 text-sm text-slate-300">
              Drag and drop your files here, or click to browse
            </p>

            <p className="mt-1 text-xs text-slate-400">
              Supported formats: .xlsx, .xls — up to 50 files
            </p>
          </div>
        </div>
      </div>

      {files.length > 0 && (
        <div className="mt-6 rounded-2xl bg-slate-900/70 p-4">
          <div className="mb-3 flex items-center justify-between">
            <h3 className="text-sm font-semibold text-white">
              Selected Files
            </h3>

            <span className="text-xs text-cyan-300">
              {files.length} file{files.length > 1 ? "s" : ""}
            </span>
          </div>

          <div className="max-h-72 space-y-3 overflow-y-auto">
            {files.map((item, index) => (
              <div
                key={`${item.file.name}-${index}`}
                className="rounded-xl bg-slate-800 p-4"
              >
                <div className="flex items-center justify-between gap-3">
                  <div className="flex min-w-0 items-center gap-3">
                    <FileText className="shrink-0 text-cyan-400" />

                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium text-white">
                        {item.file.name}
                      </p>
                      <p className="text-xs text-slate-400">
                        Original file name
                      </p>
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={() => handleRemove(index)}
                    className="rounded-full p-1 text-slate-400 transition hover:bg-slate-700 hover:text-white"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>

                <div className="mt-3 flex items-center justify-between gap-3 rounded-xl border border-slate-700 bg-slate-900/70 px-3 py-2">
                  <div className="min-w-0">
                    <p className="text-xs text-slate-400">Output name</p>
                    <p className="truncate text-sm font-semibold text-cyan-300">
                      {item.displayName}
                    </p>
                  </div>

                  <button
                    type="button"
                    onClick={() => toggleRename(index)}
                    className="rounded-xl border border-cyan-400/30 px-3 py-2 text-xs font-semibold text-cyan-300 transition hover:bg-cyan-400/10"
                  >
                    {item.isRenaming ? "Done" : "Rename"}
                  </button>
                </div>

                {item.isRenaming && (
                  <div className="mt-3">
                    <input
                      type="text"
                      value={item.displayName}
                      onChange={(event) =>
                        handleRename(index, event.target.value)
                      }
                      placeholder="Example: Mountain View October Prices"
                      className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-400"
                    />
                  </div>
                )}

                <div className="mt-2 flex justify-end">
                  <span
                    className={`text-xs ${
                      uploaded ? "text-emerald-400" : "text-green-400"
                    }`}
                  >
                    {uploaded ? "Uploaded" : "Ready"}
                  </span>
                </div>
              </div>
            ))}
          </div>

          <button
            onClick={handleUpload}
            className="mt-4 w-full rounded-2xl bg-cyan-500 px-4 py-3 font-semibold text-white transition hover:bg-cyan-400"
          >
            Upload Files
          </button>

          {status && <p className="mt-3 text-sm text-slate-300">{status}</p>}
        </div>
      )}
    </div>
  );
}

export default UploadBox;