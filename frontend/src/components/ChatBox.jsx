import { useState, useRef, useEffect, useCallback } from "react";
import { queryDoc, getUserFiles } from "../services/api";

export default function ChatBox({ uploadedFilename }) {
    const [messages, setMessages] = useState([
        { role: "assistant", text: "Hi! Upload a document and ask me anything about it." },
    ]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const [files, setFiles] = useState([]);           // [{ id, filename, uploaded_at }]
    const [filesLoading, setFilesLoading] = useState(false);
    const [filesError, setFilesError] = useState("");
    const [selectedFilename, setSelectedFilename] = useState("");
    const bottomRef = useRef();

    // Fetch the user's file list from the backend
    const fetchFiles = useCallback(async () => {
        setFilesLoading(true);
        setFilesError("");
        try {
            const res = await getUserFiles();
            setFiles(res.data);
        } catch (err) {
            const msg = err.response?.data?.detail || err.message || "Failed to load files";
            setFilesError(msg);
            console.error("[getUserFiles]", err.response?.status, msg);
        } finally {
            setFilesLoading(false);
        }
    }, []);

    // Load file list on mount
    useEffect(() => { fetchFiles(); }, [fetchFiles]);

    // Refresh list + auto-select the new file when an upload completes
    useEffect(() => {
        if (uploadedFilename) {
            fetchFiles();
            setSelectedFilename(uploadedFilename);
        }
    }, [uploadedFilename, fetchFiles]);

    // Auto-scroll to latest message
    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, loading]);

    const sendMessage = async () => {
        const question = input.trim();
        if (!question || loading) return;

        setMessages((prev) => [...prev, { role: "user", text: question }]);
        setInput("");
        setLoading(true);
        try {
            const res = await queryDoc(question, selectedFilename || null);
            setMessages((prev) => [...prev, { role: "assistant", text: res.data.answer }]);
        } catch (err) {
            if (err.response?.status === 429) {
            setMessages((prev) => [
                ...prev,
                { role: "assistant", text: "⚠️ Rate limit exceeded. Please try again later." },
            ]);
            }
            else {
                setMessages((prev) => [
                ...prev,
                {
                    role: "assistant",
                    text: "⚠️ " + (err.response?.data?.detail || "Something went wrong."),
                },
            ]);
            }
        } finally {
            setLoading(false);
        }
    };

    const handleKey = (e) => {
        if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
    };

    return (
        <div className="surface flex flex-col h-full min-h-0">
            {/* Header with file dropdown */}
            <div className="flex items-center justify-between border-b border-white/10 px-5 py-3 shrink-0">
                <h2 className="text-xs font-semibold uppercase tracking-widest text-slate-400">Chat</h2>

                <div className="flex flex-col items-end gap-1">
                    <div className="flex items-center gap-2">
                        {filesLoading && <span className="spinner" />}
                        <select
                            value={selectedFilename}
                            onChange={(e) => setSelectedFilename(e.target.value)}
                            className="w-56 rounded-lg border border-white/10 bg-[#0d0f14] px-3 py-1
                                       text-xs text-slate-300 outline-none focus:border-indigo-500
                                       transition cursor-pointer disabled:opacity-50"
                            disabled={filesLoading}
                        >
                            <option value="">All documents</option>
                            {files.map((f) => (
                                <option key={f.id} value={f.filename}>
                                    {f.filename}
                                </option>
                            ))}
                            {files.length === 0 && !filesLoading && !filesError && (
                                <option disabled>No files uploaded yet</option>
                            )}
                        </select>
                        <button
                            onClick={fetchFiles}
                            title="Refresh file list"
                            className="text-slate-500 hover:text-slate-200 transition text-sm select-none"
                        >
                            ↻
                        </button>
                    </div>
                    {/* Show error below dropdown if fetch failed */}
                    {filesError && (
                        <span className="text-[10px] text-rose-400">{filesError}</span>
                    )}
                </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-5 py-4 space-y-3 min-h-0">
                {messages.map((msg, i) =>
                    msg.role === "user" ? (
                        <div key={i} className="flex justify-end">
                            <p className="bubble-user">{msg.text}</p>
                        </div>
                    ) : (
                        <div key={i} className="flex justify-start">
                            <p className="bubble-ai whitespace-pre-wrap">{msg.text}</p>
                        </div>
                    )
                )}
                {loading && (
                    <div className="flex justify-start">
                        <p className="bubble-ai flex items-center gap-2">
                            <span className="spinner" /> Thinking…
                        </p>
                    </div>
                )}
                <div ref={bottomRef} />
            </div>

            {/* Input bar */}
            <div className="border-t border-white/10 px-4 py-3 flex gap-2 shrink-0">
                <textarea
                    rows={1}
                    className="flex-1 resize-none rounded-xl border border-white/10 bg-white/5
                     px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 outline-none
                     focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/25 transition"
                    placeholder="Ask a question about your document… (Enter to send)"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKey}
                />
                <button
                    onClick={sendMessage}
                    disabled={!input.trim() || loading}
                    className="btn-primary self-end px-4"
                >
                    Send
                </button>
            </div>
        </div>
    );
}
