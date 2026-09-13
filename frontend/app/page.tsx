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
interface ChatMessage {
  id: string;
  conversation_id: string;
  role: string;
  content: string;
  created_at: string;
}

interface DocumentResponse {
  id: string;
  filename: string;
  content_type: string;
  file_path: string;
  num_chunks: number;
  created_at: string;
}

interface Conversation {
  id: string;
  user_id: string;
  document_id: string;
  title: string;
  created_at: string;
}

interface QuizQuestion {
  id: number;
  question: string;
  options: string[];
  correct_answer: string;
  explanation: string;
}

interface QuizResponse {
  document_id: string;
  questions: QuizQuestion[];
}


export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [summary, setSummary] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");

  const [question, setQuestion] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [history, setHistory] = useState<ChatMessage[]>([]);
  const [conversations, setConversations] = useState<Conversation[]>([]);

  const [quiz, setQuiz] = useState<QuizResponse | null>(null);
  const [quizLoading, setQuizLoading] = useState(false);
  const [quizError, setQuizError] = useState("");
  const [numQuestions, setNumQuestions] = useState(5);
  const [difficulty, setDifficulty] = useState("medium");

  useEffect(() => {
    const token = localStorage.getItem("access_token");

    if (!token) {
      window.location.href = "/login";
      return;
    }

    setAccessToken(token);
    loadConversations();
  }, []);

  useEffect(() => {
    if (conversationId) {
      loadConversationMessages(conversationId);
    }
  }, [conversationId]);


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
    if (!accessToken) {
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

      const document_response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/documents/upload`, {
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
        `${process.env.NEXT_PUBLIC_API_URL}/conversations/`, {
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

      if (!conversation_response.ok) {
        throw new Error(
          conversationDate.detail || "Failed to create conversation."
        );
      }
      //check summary already in db
      if (conversationDate.summary) {
        setSummary(conversationDate.summary);
        setConversationId(conversationDate.id);
        await loadConversations();
        return;
      }

      const formData = new FormData();
      formData.append("file", file);
      formData.append("document_id",documentId!)

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

  const checkSummary = async (conversationId: string) => {
    const token = localStorage.getItem("access_token");

    if (!token) {
      window.location.href = "/login";
      return;
    }

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/conversations/${conversationId}/summary`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "Failed to check summary."
        );
      }

      if (data.has_summary) {
        setSummary(data.summary);
        console.log("Summary already exists.");
        return true;
      }

      setSummary("");
      console.log("No summary exists.");
      return false;

    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Something went wrong.");
      }

      return false;
    }
  };

  const getConversation = async (documentId: string) => {
    const token = localStorage.getItem("access_token");

    if (!token) {
      window.location.href = "/login";
      return;
    }

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/conversations/`,
        {
          method: "GET",
          headers: {
            "Authorization": `Bearer ${token}`,
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to get conversations."
        );
      }

      const conversations: Conversation[] = data;
      const conversation = conversations.find((c) => c.document_id === documentId);
      return conversation;
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Something went wrong.");
      }
    }
  };

  const loadConversationMessages = async (conversationId: string) => {
    const token = localStorage.getItem("access_token");

    if (!token) {
      window.location.href = "/login";
      return;
    }

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/conversations/${conversationId}/messages`,
        {
          method: "GET",
          headers: {
            "Authorization": `Bearer ${token}`,
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to load conversation."
        );
      }

      setMessages(data);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Something went wrong.");
      }
    }
  };


  const handleChat = async () => {
    const accessToken = localStorage.getItem("access_token");

    if (!accessToken) {
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

      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          conversation_id: conversationId!,
          role: "user",
          content: question,
          created_at: new Date().toISOString(),
        },
        {
          id: crypto.randomUUID(),
          conversation_id: conversationId!,
          role: "assistant",
          content: data.answer,
          created_at: new Date().toISOString(),
        },
      ]);

      setQuestion("");

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

  const loadConversations = async () => {
    const token = localStorage.getItem("access_token");

    if (!token) {
      window.location.href = "/login";
      return;
    }

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/conversations/`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        console.error("Summary API error:", data);

        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : JSON.stringify(data.detail, null, 2)
        );
      }

      setConversations(data);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Something went wrong.");
      }
    }
  };

  const handleGenerateQuiz = async () => {
    const token = localStorage.getItem("access_token");

    if (!token) {
      window.location.href = "/login";
      return;
    }

    if (!documentId) {
      setQuizError("Please select a document first.");
      return;
    }

    setQuizLoading(true);
    setQuizError("");
    setQuiz(null);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/quiz/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            document_id: documentId,
            num_questions: numQuestions,
            difficulty: difficulty,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "Failed to generate quiz."
        );
      }

      setQuiz(data);
    } catch (err) {
      if (err instanceof Error) {
        setQuizError(err.message);
      } else {
        setQuizError("Something went wrong.");
      }
    } finally {
      setQuizLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 px-6 py-12">
      <div className="mx-auto flex max-w-6xl gap-6">
        {/* Conversations Sidebar */}
        <aside className="w-64 shrink-0 rounded-2xl bg-white p-5 shadow-lg">
          <h2 className="mb-4 text-lg font-semibold text-gray-900">
            Conversations
          </h2>

          <button
            onClick={() => {
              setFile(null);
              setSummary("");
              setQuestion("");
              setMessages([]);
              setDocumentId(null);
              setConversationId(null);
              setError("");
            }}
            className="mb-4 w-full rounded-lg bg-black px-4 py-2 text-sm font-semibold text-white transition hover:bg-gray-800"
          >
            + New Chat
          </button>

          <div className="space-y-2">
            {conversations.length === 0 ? (
              <p className="text-sm text-gray-500">
                No conversations yet.
              </p>
            ) : (
              conversations.map((conversation) => (
                <button
                  key={conversation.id}
                  onClick={() => {
                    setConversationId(conversation.id);
                    setDocumentId(conversation.document_id);
                    checkSummary(conversation.id);
                  }}
                  className={`w-full rounded-lg p-3 text-left text-sm transition ${conversation.id === conversationId
                      ? "bg-gray-900 text-white"
                      : "bg-gray-50 text-gray-700 hover:bg-gray-100"
                    }`}
                >
                  <p className="truncate font-medium">
                    {conversation.title}
                  </p>

                  <p
                    className={`mt-1 text-xs ${conversation.id === conversationId
                        ? "text-gray-300"
                        : "text-gray-400"
                      }`}
                  >
                    {new Date(
                      conversation.created_at
                    ).toLocaleDateString()}
                  </p>
                </button>
              ))
            )}
          </div>
        </aside>

        <div className="min-w-0 flex-1">
          {/* Header */}
          <div className="mb-10">
            <div className="flex items-center justify-between">
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
            </div>

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


          <div className="mt-8 rounded-xl border bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-xl font-semibold text-gray-900">
              Generate Quiz
            </h2>

            <div className="mb-4 flex gap-4">
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">
                  Questions
                </label>

                <select
                  value={numQuestions}
                  onChange={(e) => setNumQuestions(Number(e.target.value))}
                  className="rounded-lg border px-3 py-2"
                >
                  <option value={5}>5</option>
                  <option value={10}>10</option>
                  <option value={15}>15</option>
                  <option value={20}>20</option>
                </select>
              </div>

              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">
                  Difficulty
                </label>

                <select
                  value={difficulty}
                  onChange={(e) => setDifficulty(e.target.value)}
                  className="rounded-lg border px-3 py-2"
                >
                  <option value="easy">Easy</option>
                  <option value="medium">Medium</option>
                  <option value="hard">Hard</option>
                </select>
              </div>
            </div>

            <button
              onClick={handleGenerateQuiz}
              disabled={quizLoading || !documentId}
              className="rounded-lg bg-gray-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-gray-800 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {quizLoading ? "Generating Quiz..." : "Generate Quiz"}
            </button>

            {quizError && (
              <p className="mt-3 text-sm text-red-600">
                {quizError}
              </p>
            )}
          </div>


          {quiz && (
            <div className="mt-6 space-y-6">
              {quiz.questions.map((question, index) => (
                <div
                  key={question.id}
                  className="rounded-xl border bg-white p-6 shadow-sm"
                >
                  <h3 className="mb-4 font-semibold text-gray-900">
                    {index + 1}. {question.question}
                  </h3>

                  <div className="space-y-2">
                    {question.options.map((option, optionIndex) => (
                      <div
                        key={optionIndex}
                        className="rounded-lg border px-4 py-3 text-gray-700"
                      >
                        {String.fromCharCode(65 + optionIndex)}. {option}
                      </div>
                    ))}
                  </div>

                  <div className="mt-4 rounded-lg bg-gray-50 p-4">
                    <p className="text-sm font-medium text-gray-900">
                      Answer: {question.correct_answer}
                    </p>

                    {question.explanation && (
                      <p className="mt-1 text-sm text-gray-600">
                        {question.explanation}
                      </p>
                    )}
                  </div>
                </div>
              ))}
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

              {/* Answer */}
              {messages.length > 0 && (
                <div className="mt-6 space-y-4">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`rounded-xl p-5 ${message.role === "user"
                          ? "bg-gray-900 text-white"
                          : "bg-gray-50 text-gray-800"
                        }`}
                    >
                      <p className="mb-2 text-sm font-semibold">
                        {message.role === "user" ? "You" : "StudyGen AI"}
                      </p>

                      <ReactMarkdown
                        remarkPlugins={[remarkMath]}
                        rehypePlugins={[rehypeKatex]}
                      >
                        {message.content}
                      </ReactMarkdown>
                    </div>
                  ))}
                </div>
              )}

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

            </div>
          )}
        </div>
      </div>
    </main>
  );
}