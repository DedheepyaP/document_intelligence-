import { useState, useRef } from "react";
import { uploadFile } from "../services/api";

export default function FileUpload({ onUploadSuccess }) {
    const [dragging, setDragging] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [status, setStatus] = useState(null); // { type, message }
    const inputRef = useRef();

    const handleFile = async (file) => {
        if (!file) return;
        setUploading(true);
        setStatus(null);
        try {
            const res = await uploadFile(file);
            setStatus({ type: "success", message: `"${res.data.filename}" queued for processing.` });
            onUploadSuccess?.(res.data.filename);
        } catch (err) {
            setStatus({
                type: "error",
                message: err.response?.data?.detail || "Upload failed.",
            });
        } finally {
            setUploading(false);
        }
    };

    const onDrop = (e) => {
        e.preventDefault();
        setDragging(false);
        handleFile(e.dataTransfer.files[0]);
    };

    return (
        <div className="surface p-6 flex flex-col gap-4">
            <h2 className="text-xs font-semibold uppercase tracking-widest text-slate-400">
                Upload Document
            </h2>

            <div
                onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
                onDragLeave={() => setDragging(false)}
                onDrop={onDrop}
                onClick={() => inputRef.current?.click()}
                className={`flex cursor-pointer flex-col items-center justify-center gap-3
                    rounded-xl border-2 border-dashed py-10 transition
                    ${dragging
                        ? "border-indigo-400 bg-indigo-500/10"
                        : "border-white/10 hover:border-indigo-500/40 hover:bg-white/5"}`}
            >
                <span className="select-none text-3xl">📂</span>
                <p className="text-sm font-medium text-slate-300">
                    {dragging ? "Drop it here…" : "Drag & drop or click to browse"}
                </p>
                <p className="text-xs text-slate-500">PDF, DOCX, images</p>
                <input
                    ref={inputRef}
                    type="file"
                    className="hidden"
                    accept=".pdf,.docx,.doc,.png,.jpg,.jpeg,.tiff"
                    onChange={(e) => handleFile(e.target.files[0])}
                />
            </div>

            {uploading && (
                <div className="flex items-center gap-2 text-sm text-slate-400">
                    <span className="spinner" /> Uploading…
                </div>
            )}
            {status && (
                <p className={status.type === "success" ? "alert-success" : "alert-error"}>
                    {status.message}
                </p>
            )}
        </div>
    );
}
