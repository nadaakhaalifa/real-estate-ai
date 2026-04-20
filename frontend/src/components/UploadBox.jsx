import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { UploadCloud, FileText, X } from "lucide-react";
import axios from "axios";

const API_URL = "http://127.0.0.1:8000";

function UploadBox() {
  const [files, setFiles] = useState([]);
  const [status, setStatus] = useState("");
  const [uploaded, setUploaded] = useState(false);

  const onDrop = useCallback((acceptedFiles) => {
    setFiles((prevFiles) => {
      const combinedFiles = [...prevFiles, ...acceptedFiles];

      const uniqueFiles = combinedFiles.filter(
        (file, index, self) =>
          index === self.findIndex((f) => f.name === file.name)
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
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
      "application/vnd.ms-excel": [".xls"],
    },
  });

  const handleUpload = async () => {
    if (files.length === 0) {
      setStatus("Please select at least one Excel file.");
      return;
    }

    const formData = new FormData();

    files.forEach((file) => {
      formData.append("files", file);
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
      console.error(error);
      setUploaded(false);
      setStatus("Upload failed ❌");
    }
  };

  return (
    <div className="w-full max-w-3xl rounded-3xl border border-white/10 bg-white/5 p-6 shadow-xl backdrop-blur">
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

          <div className="max-h-56 space-y-2 overflow-y-auto">
            {files.map((file, index) => (
              <div
                key={`${file.name}-${index}`}
                className="flex items-center justify-between rounded-xl bg-slate-800 p-3"
              >
                <div className="flex items-center gap-3 overflow-hidden">
                  <FileText className="shrink-0 text-cyan-400" />
                  <span className="truncate text-sm text-white">
                    {file.name}
                  </span>
                </div>

                <div className="ml-3 flex items-center gap-3">
                  <span
                    className={`shrink-0 text-xs ${
                      uploaded ? "text-emerald-400" : "text-green-400"
                    }`}
                  >
                    {uploaded ? "Uploaded" : "Ready"}
                  </span>

                  <button
                    type="button"
                    onClick={() =>
                      setFiles((prevFiles) =>
                        prevFiles.filter((_, fileIndex) => fileIndex !== index)
                      )
                    }
                    className="rounded-full p-1 text-slate-400 transition hover:bg-slate-700 hover:text-white"
                  >
                    <X className="h-4 w-4" />
                  </button>
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

          {status && (
            <p className="mt-3 text-sm text-slate-300">{status}</p>
          )}
        </div>
      )}
    </div>
  );
}

export default UploadBox;