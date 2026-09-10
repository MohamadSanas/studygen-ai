"use client";

import { ChangeEvent, useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";

interface SummaryResponse {
  file_name: string;
  summary: string;
}

interface DocumentResponse {
  id: string;
  filename: string;
  content_type: string;
  file_path: string;
  num_chunks: number;
  created_at: string;
}


export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [summary, setSummary] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");
  
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      window.location.href = "/login";
      return;
    }
    setAccessToken(token);
  }, []);


  const handleLogout = () => {
    localStorage.removeItem("access_token");
    window.location.href = "/login";
  };

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];

    if (!selectedFile) {
      return;
    }

    if (selectedFile.type !== "application/pdf") {
      setError("Please select a PDF file.");
      setFile(null);
      return;
    }

    setFile(selectedFile);
    setSummary("");
    setError("");
  };

  const handleSummarize = async () => {
    const accessToken = localStorage.getItem("access_token");
    if(!accessToken){
      setError("Please login to continue.");
      return;
    }

    if (!file) {
      setError("Please select a PDF file first.");
      return;
    }

    setLoading(true);
    setError("");
    setSummary("");

    try {
      const documentFormData = new FormData();
      documentFormData.append("file", file);

      const document_response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/documents/upload`,{
        method: "POST",
        body: documentFormData,
        headers: {
          "Authorization": `Bearer ${accessToken}`,
        },
      })
      if (!document_response.ok) {
        throw new Error(
          "Failed to upload document."
        );
      }

      const document_details = await document_response.json()
      const documentId = document_details.id;
      console.log("Document ID:", documentId);
      setDocumentId(documentId);

      const conversation_response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/conversations/`,{
        method: "POST",
        body: JSON.stringify({
          document_id: documentId,
          title: file.name,
        }),
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${accessToken}`,
        },
      })

      const conversationDate = await conversation_response.json();
      console.log("Conversation Data:", conversationDate);

      if(!conversation_response.ok){
        throw new Error(
          conversationDate.detail || "Failed to create conversation."
        );
      }

      const conversationId = conversationDate.id;
      console.log("Conversation ID:", conversationId);
      setConversationId(conversationId);

      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/summary/`,
        {
          method: "POST",
          body: formData,
          headers: {
            "Authorization": `Bearer ${accessToken}`,
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to generate summary."
        );
      }

      const result: SummaryResponse = data;

      setSummary(result.summary);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Something went wrong.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleChat = async () => {
    const accessToken = localStorage.getItem("access_token");

    if(!accessToken){
      setError("Please login to continue.");
      return;
    }
      if (!documentId) {
        setError("Please upload a document first.");
        return;
      }

      if (!question.trim()) {
        setError("Please enter a question.");
        return;
      }


      setChatLoading(true);
      setAnswer("");
      setError("");

      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/chat/`,
          {
            method: "POST",
            body: JSON.stringify({
              document_id: documentId,
              conversation_id: conversationId,
              question: question,
            }),
            headers: {
              "Content-Type": "application/json",
              "Authorization": `Bearer ${accessToken}`,
            },
          }
        );

        const data = await response.json();

        if (!response.ok) {
          throw new Error(
            data.detail || "Failed to generate answer."
          );
        }

        setAnswer(data.answer);

      } catch (err) {
        if (err instanceof Error) {
          setError(err.message);
        } else {
          setError("Something went wrong.");
        }
      } finally {
        setChatLoading(false);
      }
  };

  return (
    <main className="min-h-screen bg-gray-50 px-6 py-12">
      <div className="mx-auto max-w-4xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-10">
          <h1 className="text-4xl font-bold text-gray-900">
            StudyGen AI
          </h1>

          {accessToken ? (
            <button
              onClick={handleLogout}
              className="rounded-lg bg-red-500 px-6 py-3 text-white transition hover:bg-red-600"
            >
              Logout
            </button>
          ) : (
            <a
              href="/login"
              className="rounded-lg bg-blue-500 px-6 py-3 text-white transition hover:bg-blue-600"
            >
              Login
            </a>
          )}

          <p className="mt-3 text-lg text-gray-600">
            Upload your lecture notes and generate an AI-powered summary.
          </p>
        </div>



        {/* Upload Card */}
        <div className="rounded-2xl bg-white p-8 shadow-lg">
          <h2 className="text-2xl font-semibold text-gray-900">
            PDF Summarizer
          </h2>

          <p className="mt-2 text-gray-500">
            Upload a PDF lecture note to get a clear study summary.
          </p>

          {/* File Input */}
          <div className="mt-6">
            <label
              htmlFor="pdf-upload"
              className="flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-gray-300 p-10 text-center transition hover:border-gray-500"
            >
              <div className="text-4xl">📄</div>

              <p className="mt-4 font-medium text-gray-700">
                Choose a PDF file
              </p>

              <p className="mt-1 text-sm text-gray-500">
                Only PDF files are supported
              </p>

              <input
                id="pdf-upload"
                type="file"
                accept="application/pdf"
                onChange={handleFileChange}
                className="hidden"
              />
            </label>
          </div>

          {/* Selected File */}
          {file && (
            <div className="mt-4 rounded-lg bg-gray-100 p-4">
              <p className="text-sm font-medium text-gray-700">
                Selected file:
              </p>

              <p className="mt-1 truncate text-sm text-gray-600">
                {file.name}
              </p>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="mt-4 rounded-lg bg-red-50 p-4 text-sm text-red-700">
              {error}
            </div>
          )}

          {/* Button */}
          <button
            onClick={handleSummarize}
            disabled={!file || loading}
            className="mt-6 w-full rounded-xl bg-black px-6 py-3 font-semibold text-white transition hover:bg-gray-800 disabled:cursor-not-allowed disabled:bg-gray-300"
          >
            {loading ? "Generating Summary..." : "Generate Summary"}
          </button>
        </div>

        {/* Summary */}
        {summary && (
          <div className="mt-8 rounded-2xl bg-white p-8 shadow-lg">
            <h2 className="text-2xl font-semibold text-gray-900">
              Summary
            </h2>

            <div className="mt-6 max-w-none text-gray-800">
              <ReactMarkdown
                remarkPlugins={[remarkMath]}
                rehypePlugins={[rehypeKatex]}
                components={{
                  h1: ({ children }) => (
                    <h1 className="mb-4 mt-8 text-3xl font-bold text-gray-900">
                      {children}
                    </h1>
                  ),

                  h2: ({ children }) => (
                    <h2 className="mb-3 mt-7 text-2xl font-bold text-gray-900">
                      {children}
                    </h2>
                  ),

                  h3: ({ children }) => (
                    <h3 className="mb-2 mt-5 text-xl font-semibold text-gray-900">
                      {children}
                    </h3>
                  ),

                  p: ({ children }) => (
                    <p className="mb-4 leading-7 text-gray-700">
                      {children}
                    </p>
                  ),

                  ul: ({ children }) => (
                    <ul className="mb-4 ml-6 list-disc space-y-2 text-gray-700">
                      {children}
                    </ul>
                  ),

                  ol: ({ children }) => (
                    <ol className="mb-4 ml-6 list-decimal space-y-2 text-gray-700">
                      {children}
                    </ol>
                  ),

                  li: ({ children }) => (
                    <li className="leading-7">
                      {children}
                    </li>
                  ),

                  strong: ({ children }) => (
                    <strong className="font-bold text-gray-900">
                      {children}
                    </strong>
                  ),
                }}
              >
                {summary}
              </ReactMarkdown>
            </div>
          </div>
        )}


        {/* Chat with PDF */}
        {documentId && (
          <div className="mt-8 rounded-2xl bg-white p-8 shadow-lg">
            <h2 className="text-2xl font-semibold text-gray-900">
              Chat with your PDF
            </h2>

            <p className="mt-2 text-gray-500">
              Ask questions about the uploaded document.
            </p>

            {/* Question Input */}
            <div className="mt-6">
              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask something about your PDF..."
                rows={4}
                className="w-full rounded-xl border border-gray-300 p-4 text-gray-800 outline-none focus:border-gray-500"
              />
            </div>

            {/* Ask Button */}
            <button
              onClick={handleChat}
              disabled={!question.trim() || chatLoading}
              className="mt-4 w-full rounded-xl bg-black px-6 py-3 font-semibold text-white transition hover:bg-gray-800 disabled:cursor-not-allowed disabled:bg-gray-300"
            >
              {chatLoading ? "Thinking..." : "Ask Question"}
            </button>

            {/* Answer */}
            {answer && (
              <div className="mt-6 rounded-xl bg-gray-50 p-6">
                <h3 className="text-lg font-semibold text-gray-900">
                  Answer
                </h3>

                <div className="mt-4 leading-7 text-gray-700">
                  <ReactMarkdown
                    remarkPlugins={[remarkMath]}
                    rehypePlugins={[rehypeKatex]}
                  >
                    {answer}
                  </ReactMarkdown>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}