import { useState } from "react";
import Navbar from "../components/Navbar";
import FileUpload from "../components/FileUpload";
import ChatBox from "../components/ChatBox";

export default function Dashboard({ user, onLogout, onNavigate }) {
    const [uploadedFilename, setUploadedFilename] = useState(null);

    return (
        <div className="flex flex-col h-screen">
            <Navbar
                username={user.username}
                role={user.role}
                currentPage="dashboard"
                onNavigate={onNavigate}
                onLogout={onLogout}
            />

            <main className="flex flex-1 gap-5 overflow-hidden p-5">
                {/* Left panel — Upload */}
                <div className="w-80 shrink-0 flex flex-col gap-5">
                    <FileUpload onUploadSuccess={(filename) => setUploadedFilename(filename)} />

                    {/* Tip card */}
                    <div className="surface p-5 text-sm text-slate-400 leading-relaxed">
                        <p className="mb-2 font-semibold text-slate-300">How it works</p>
                        <ol className="list-decimal list-inside space-y-1.5">
                            <li>Upload a document (PDF, DOCX, image)</li>
                            <li>Wait a moment for processing</li>
                            <li>Ask questions in the chat →</li>
                        </ol>
                        <p className="mt-3 text-xs text-slate-500">
                            Answers are generated from the content of your uploaded documents only.
                        </p>
                    </div>
                </div>

                {/* Right panel — Chat */}
                <div className="flex-1 min-w-0">
                    <ChatBox uploadedFilename={uploadedFilename} />
                </div>
            </main>
        </div>
    );
}
