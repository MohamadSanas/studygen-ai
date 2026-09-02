"use client";

import { ChangeEvent, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";

interface SummaryResponse {
  file_name: string;
  summary: string;
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [summary, setSummary] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");

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
    if (!file) {
      setError("Please select a PDF file first.");
      return;
    }

    setLoading(true);
    setError("");
    setSummary("");

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/summary/`,
        {
          method: "POST",
          body: formData,
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

  return (
    <main className="min-h-screen bg-gray-50 px-6 py-12">
      <div className="mx-auto max-w-4xl">
        {/* Header */}
        <div className="mb-10 text-center">
          <h1 className="text-4xl font-bold text-gray-900">
            StudyGen AI
          </h1>

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
      </div>
    </main>
  );
}