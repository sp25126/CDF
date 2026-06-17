"use client";

import { useState, useRef, useEffect } from "react";
import { Mic, RotateCcw, Trash2, Send, Upload, Trash, BookOpen, FileText } from "lucide-react";

export default function Home() {
  const [inputText, setInputText] = useState("");
  const [transcript, setTranscript] = useState<string[]>([]);
  const [response, setResponse] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);

  // Source Mode states
  const [sourceMode, setSourceMode] = useState(false);
  const [activeTab, setActiveTab] = useState<"transcript" | "materials">("transcript");
  const [sourcesList, setSourcesList] = useState<any[]>([]);
  const [urlInput, setUrlInput] = useState("");
  const [pastedTitle, setPastedTitle] = useState("");
  const [pastedText, setPastedText] = useState("");
  const [handoffActive, setHandoffActive] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const recognitionRef = useRef<any>(null);
  const speechTextHintRef = useRef<string>("");
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    if (activeTab === "materials") {
      fetchSources();
    }
  }, [activeTab]);

  const fetchSources = async () => {
    try {
      const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiBaseUrl}/sources`);
      const result = await res.json();
      if (result.status === "success") {
        setSourcesList(result.data);
      }
    } catch (err) {
      console.error("Error fetching sources:", err);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    
    const formData = new FormData();
    formData.append("file", file);
    
    setIsUploading(true);
    try {
      const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiBaseUrl}/sources/upload`, {
        method: "POST",
        body: formData,
      });
      const result = await res.json();
      if (result.status === "success") {
        fetchSources();
      } else {
        alert(result.error?.message || "Ingestion failed");
      }
    } catch (err) {
      console.error("Error uploading file:", err);
    } finally {
      setIsUploading(false);
      // Clear input
      e.target.value = "";
    }
  };

  const handleAddUrl = async () => {
    if (!urlInput.trim()) return;
    setIsUploading(true);
    try {
      const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiBaseUrl}/sources/add-url`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: urlInput }),
      });
      const result = await res.json();
      if (result.status === "success") {
        setUrlInput("");
        fetchSources();
      } else {
        alert(result.error?.message || "Ingestion failed");
      }
    } catch (err) {
      console.error("Error adding URL:", err);
    } finally {
      setIsUploading(false);
    }
  };

  const handleAddText = async () => {
    if (!pastedText.trim() || !pastedTitle.trim()) return;
    setIsUploading(true);
    try {
      const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiBaseUrl}/sources/add-text`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: pastedTitle, text: pastedText }),
      });
      const result = await res.json();
      if (result.status === "success") {
        setPastedTitle("");
        setPastedText("");
        fetchSources();
      } else {
        alert(result.error?.message || "Ingestion failed");
      }
    } catch (err) {
      console.error("Error adding text:", err);
    } finally {
      setIsUploading(false);
    }
  };

  const handleDeleteSource = async (id: string) => {
    try {
      const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiBaseUrl}/sources/${id}`, {
        method: "DELETE",
      });
      const result = await res.json();
      if (result.status === "success") {
        fetchSources();
      }
    } catch (err) {
      console.error("Error deleting source:", err);
    }
  };

  const handleNotebookLMHandoff = () => {
    if (!response) return;
    
    const topic = response.title || "Classroom Topic";
    const promptText = `Create a study guide and an audio podcast outline for the topic: '${topic}' at Grade Level 'Grade 6' using the uploaded classroom source documents. Include Haryana-local analogies to explain key terms.`;
    
    navigator.clipboard.writeText(promptText).then(() => {
      setHandoffActive(true);
      setTimeout(() => {
        setHandoffActive(false);
        window.open("https://notebooklm.google/", "_blank");
      }, 1500);
    }).catch(err => {
      console.error("Clipboard copy failed:", err);
      window.open("https://notebooklm.google/", "_blank");
    });
  };

  const submitCommand = async (commandText: string) => {
    if (!commandText.trim()) return;

    if (audioRef.current) {
      audioRef.current.pause();
    }
    if (typeof window !== "undefined" && window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }

    setIsLoading(true);
    try {
      const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiBaseUrl}/command/text`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: commandText,
          session_id: "demo-session-123",
          context: { grade_level: 7, subject: "Science" },
          source_mode: sourceMode
        }),
      });

      const result = await res.json();
      if (result.status === "success") {
        setResponse(result.data);
        setTranscript((prev) => [...prev, commandText]);
        setInputText("");

        // Play the base64 audio response if present
        if (result.data.audio_base64) {
          const audio = new Audio(result.data.audio_base64);
          audioRef.current = audio;
          audio.play();
        }
      }
    } catch (error) {
      console.error("Error sending command:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const startRecording = async () => {
    audioChunksRef.current = [];
    speechTextHintRef.current = "";
    setInputText("");

    if (audioRef.current) {
      audioRef.current.pause();
    }
    if (typeof window !== "undefined" && window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });
        setIsLoading(true);

        try {
          const formData = new FormData();
          formData.append("session_id", "demo-session-123");
          formData.append("audio", audioBlob, "audio.wav");
          formData.append("source_mode", String(sourceMode));
          if (speechTextHintRef.current) {
            formData.append("text_hint", speechTextHintRef.current);
          }

          const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
          const res = await fetch(`${apiBaseUrl}/command/audio`, {
            method: "POST",
            body: formData,
          });

          const result = await res.json();
          if (result.status === "success") {
            setResponse(result.data);
            setTranscript((prev) => [...prev, result.data.transcript || speechTextHintRef.current || "Voice Input"]);
            if (result.data.audio_base64) {
              const audio = new Audio(result.data.audio_base64);
              audioRef.current = audio;
              audio.play();
            }
          }
        } catch (error) {
          console.error("Error sending audio command:", error);
        } finally {
          setIsLoading(false);
        }
      };

      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        const rec = new SpeechRecognition();
        rec.continuous = true;
        rec.interimResults = true;
        rec.lang = "hi-IN";
        rec.onresult = (event: any) => {
          let finalTranscript = "";
          let interimTranscript = "";
          for (let i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
              finalTranscript += event.results[i][0].transcript;
            } else {
              interimTranscript += event.results[i][0].transcript;
            }
          }
          const currentText = finalTranscript || interimTranscript;
          if (currentText.trim()) {
            setInputText(currentText);
            speechTextHintRef.current = currentText;
          }
        };
        rec.onerror = (e: any) => {
          console.error("Speech recognition error:", e.error);
        };
        recognitionRef.current = rec;
        rec.start();
      }

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error("Microphone access denied or error starting recording:", err);
      alert("Microphone access is required for voice commands. Using text fallback.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach((track) => track.stop());
    }
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    setIsRecording(false);
  };

  const handleSendCommand = () => {
    submitCommand(inputText);
  };

  const handleRepeat = () => {
    if (!response) return;

    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }

    if (response.audio_base64) {
      const audio = new Audio(response.audio_base64);
      audioRef.current = audio;
      audio.play();
    } else if (response.response_text && typeof window !== "undefined" && window.speechSynthesis) {
      const utterance = new SpeechSynthesisUtterance(response.response_text);
      utterance.lang = "hi-IN";
      window.speechSynthesis.cancel();
      window.speechSynthesis.speak(utterance);
    }
  };

  const clearSession = () => {
    if (audioRef.current) {
      audioRef.current.pause();
    }
    if (typeof window !== "undefined" && window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
    setTranscript([]);
    setResponse(null);
    setInputText("");
  };

  return (
    <main className="flex min-h-screen flex-col bg-slate-50 text-slate-900 font-sans relative">
      {/* NotebookLM Portal Animation Overlay */}
      {handoffActive && (
        <div className="absolute inset-0 bg-indigo-950 z-50 flex flex-col items-center justify-center animate-in fade-in duration-500">
          <div className="w-24 h-24 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mb-6"></div>
          <h2 className="text-4xl font-extrabold text-white animate-pulse">Launching NotebookLM Study Guide...</h2>
          <p className="text-xl text-purple-200 mt-2">Topic prompt copied to clipboard!</p>
        </div>
      )}

      {/* Header */}
      <header className="bg-blue-700 text-white p-6 shadow-md">
        <h1 className="text-4xl font-bold text-center">Shiksha Sahayak: AI Teaching Assistant</h1>
      </header>

      <div className="flex-1 flex flex-col md:flex-row p-6 gap-6 overflow-hidden">
        {/* Left Panel: Tabs for Transcript / Materials */}
        <div className="w-full md:w-1/3 flex flex-col bg-white rounded-xl shadow-lg border border-slate-200 p-4">
          <div className="flex border-b border-slate-200 mb-4">
            <button
              onClick={() => setActiveTab("transcript")}
              className={`flex-1 pb-2 text-xl font-bold text-center border-b-2 transition-all ${
                activeTab === "transcript"
                  ? "border-blue-700 text-blue-700"
                  : "border-transparent text-slate-400 hover:text-slate-600"
              }`}
            >
              Transcript
            </button>
            <button
              onClick={() => {
                setActiveTab("materials");
                fetchSources();
              }}
              className={`flex-1 pb-2 text-xl font-bold text-center border-b-2 transition-all ${
                activeTab === "materials"
                  ? "border-blue-700 text-blue-700"
                  : "border-transparent text-slate-400 hover:text-slate-600"
              }`}
            >
              Classroom Materials
            </button>
          </div>

          {activeTab === "transcript" ? (
            <div className="flex-1 flex flex-col overflow-hidden">
              <div className="flex-1 overflow-y-auto space-y-3">
                {transcript.length === 0 && (
                  <p className="text-slate-400 italic">No commands yet...</p>
                )}
                {transcript.map((t, i) => (
                  <div key={i} className="p-3 bg-slate-100 rounded-lg text-lg">
                    {t}
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="flex-1 flex flex-col overflow-hidden space-y-4">
              {/* Document upload / URL form / Pasted text form */}
              <div className="space-y-3 p-3 bg-slate-50 border border-slate-200 rounded-xl">
                <h3 className="text-lg font-bold text-slate-700 mb-1">Add Document</h3>
                
                {/* File Upload */}
                <div className="flex flex-col gap-1">
                  <label className="text-sm font-semibold text-slate-600">Upload PDF / TXT</label>
                  <input
                    type="file"
                    accept=".pdf,.txt"
                    onChange={handleFileUpload}
                    disabled={isUploading}
                    className="w-full text-md text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-md file:font-semibold file:bg-blue-50 file:text-blue-700 file:cursor-pointer hover:file:bg-blue-100"
                  />
                </div>

                <div className="border-t my-2 border-slate-200"></div>

                {/* URL Add */}
                <div className="flex flex-col gap-1">
                  <label className="text-sm font-semibold text-slate-600">Add Webpage URL</label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      placeholder="https://example.com/topic"
                      value={urlInput}
                      onChange={(e) => setUrlInput(e.target.value)}
                      className="flex-1 px-3 py-1.5 border border-slate-300 rounded-lg text-md"
                    />
                    <button
                      onClick={handleAddUrl}
                      disabled={isUploading || !urlInput.trim()}
                      className="px-3 py-1.5 bg-blue-700 hover:bg-blue-600 disabled:bg-slate-300 text-white rounded-lg text-md font-bold"
                    >
                      Add
                    </button>
                  </div>
                </div>

                <div className="border-t my-2 border-slate-200"></div>

                {/* Paste Text */}
                <div className="flex flex-col gap-2">
                  <label className="text-sm font-semibold text-slate-600">Paste Text Content</label>
                  <input
                    type="text"
                    placeholder="Document Title"
                    value={pastedTitle}
                    onChange={(e) => setPastedTitle(e.target.value)}
                    className="w-full px-3 py-1.5 border border-slate-300 rounded-lg text-md"
                  />
                  <textarea
                    placeholder="Paste your paragraphs here..."
                    rows={3}
                    value={pastedText}
                    onChange={(e) => setPastedText(e.target.value)}
                    className="w-full px-3 py-1.5 border border-slate-300 rounded-lg text-md"
                  ></textarea>
                  <button
                    onClick={handleAddText}
                    disabled={isUploading || !pastedText.trim() || !pastedTitle.trim()}
                    className="w-full py-2 bg-blue-700 hover:bg-blue-600 disabled:bg-slate-300 text-white rounded-lg text-md font-bold"
                  >
                    Add Pasted Text
                  </button>
                </div>
              </div>

              {/* Ingestion progress spinner */}
              {isUploading && (
                <div className="text-center py-2 text-blue-700 font-bold animate-pulse">
                  Ingesting materials...
                </div>
              )}

              {/* Active Sources List */}
              <div className="flex-1 overflow-y-auto space-y-2">
                <h3 className="text-lg font-bold text-slate-700">Uploaded Materials ({sourcesList.length})</h3>
                {sourcesList.length === 0 ? (
                  <p className="text-slate-400 italic">No custom materials uploaded yet.</p>
                ) : (
                  sourcesList.map((src) => (
                    <div key={src.id} className="flex items-center justify-between p-3 bg-slate-100 border border-slate-200 rounded-xl">
                      <div className="flex-1 min-w-0 pr-2">
                        <p className="text-md font-bold text-slate-800 truncate">{src.title}</p>
                        <p className="text-xs text-slate-500 uppercase">
                          {src.type} • {src.language} {src.page_count ? `• ${src.page_count} pages` : ""}
                        </p>
                      </div>
                      <button
                        onClick={() => handleDeleteSource(src.id)}
                        className="p-1.5 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      >
                        <Trash2 size={20} />
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* Right Panel: Main Response */}
        <div className="w-full md:w-2/3 flex flex-col bg-white rounded-xl shadow-lg border border-slate-200 p-6">
          <h2 className="text-2xl font-semibold mb-4 border-b pb-2 text-blue-800">AI Response</h2>
          <div className="flex-1 overflow-y-auto">
            {!response && !isLoading && (
              <div className="h-full flex items-center justify-center text-slate-400 text-xl">
                Awaiting teacher command...
              </div>
            )}

            {isLoading && (
              <div className="h-full flex items-center justify-center text-blue-600 text-xl font-medium animate-pulse">
                Processing command...
              </div>
            )}

            {response && (
              <div className="space-y-6 animate-in fade-in duration-500 relative pt-2">
                {/* Language Badge in top right */}
                {response.language_mode && (
                  <div className="absolute top-0 right-0 px-4 py-2 bg-blue-50 border border-blue-200 rounded-full text-lg font-bold text-blue-800 shadow-sm flex items-center gap-2">
                    {response.language_mode === "english" && "🇬🇧 English"}
                    {response.language_mode === "hindi" && "🕉 Hindi"}
                    {response.language_mode === "hinglish" && "🇮🇳 Hinglish"}
                  </div>
                )}

                {/* Explain View */}
                {(response.mode === "explain" || response.intent === "explain") && (
                  <div className="space-y-4">
                    <h3 className="text-3xl font-bold text-blue-900 pr-36">{response.title}</h3>
                    <p className="text-2xl leading-relaxed text-slate-700 font-medium italic bg-blue-50 p-4 rounded-lg border-l-4 border-blue-500">
                      "{response.response_text}"
                    </p>
                    {response.bullets && response.bullets.length > 0 && (
                      <div className="space-y-3">
                        <h4 className="text-xl font-semibold text-slate-800">Key Points:</h4>
                        <ul className="list-disc list-inside space-y-2 text-xl text-slate-700">
                          {response.bullets.map((b: string, i: number) => (
                            <li key={i}>{b}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {response.example && (
                      <div className="mt-6 p-5 bg-amber-50 rounded-xl border border-amber-200 shadow-sm">
                        <h4 className="text-xl font-bold text-amber-900 mb-2">Local Analogy:</h4>
                        <p className="text-2xl text-amber-950 font-medium">{response.example}</p>
                      </div>
                    )}
                  </div>
                )}

                {/* Quiz View */}
                {(response.mode === "quiz" || response.intent === "quiz") && (
                  <div className="space-y-4">
                    <h3 className="text-3xl font-bold text-green-900 pr-36">{response.title}</h3>
                    <p className="text-2xl leading-relaxed text-slate-700 font-medium italic mb-4">
                      "{response.response_text}"
                    </p>
                    <div className="space-y-6">
                      {response.questions.map((q: any) => (
                        <div key={q.id} className="p-5 bg-slate-50 rounded-xl border border-slate-200 shadow-sm">
                          <p className="text-2xl font-bold text-slate-900 mb-4">{q.id}. {q.question}</p>
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            {q.options.map((opt: string, idx: number) => (
                              <div key={idx} className="p-3 bg-white border-2 border-slate-300 rounded-lg text-xl font-semibold text-center hover:border-blue-500 cursor-default transition-colors">
                                {opt}
                              </div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Clarify View */}
                {(response.mode === "clarify" || response.intent === "clarify") && (
                  <div className="flex flex-col items-center justify-center h-full text-center space-y-6">
                    <p className="text-3xl font-medium text-slate-800 pr-36">
                      {response.message}
                    </p>
                    <div className="flex flex-wrap gap-4 justify-center">
                      {response.suggestions.map((s: string, i: number) => (
                        <button
                          key={i}
                          onClick={() => {
                            submitCommand(s);
                          }}
                          className="px-6 py-3 bg-blue-100 text-blue-800 rounded-full text-xl font-bold hover:bg-blue-200 transition-colors border-2 border-blue-300"
                        >
                          {s}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Citations Renderer & NotebookLM Learning Handoff */}
                {response.citations && response.citations.length > 0 && (
                  <div className="mt-6 p-5 bg-slate-50 border border-slate-200 rounded-xl shadow-inner animate-in slide-in-from-bottom duration-300">
                    <h4 className="text-xl font-bold text-slate-800 mb-3 flex items-center gap-2">
                      <span>📄 Grounded Sources & Citations</span>
                    </h4>
                    <div className="space-y-3">
                      {response.citations.map((c: any, i: number) => (
                        <div key={i} className="text-lg text-slate-700 border-l-4 border-indigo-400 pl-3">
                          <p className="font-bold text-indigo-950">
                            {c.source_title} 
                            {c.page_number && <span className="text-slate-500 font-semibold"> (Page {c.page_number})</span>}
                            {c.section_label && <span className="text-slate-500 font-semibold"> - {c.section_label}</span>}
                          </p>
                          <p className="italic text-slate-600 mt-1">"{c.snippet}"</p>
                        </div>
                      ))}
                    </div>

                    <button
                      onClick={handleNotebookLMHandoff}
                      className="mt-5 w-full flex items-center justify-center gap-3 px-6 py-4 bg-gradient-to-r from-purple-700 to-indigo-700 hover:from-purple-600 hover:to-indigo-600 text-white rounded-xl text-xl font-extrabold shadow-lg transition-transform active:scale-95 duration-200"
                    >
                      <span>Launch NotebookLM Study Guide</span>
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Control Bar */}
      <footer className="bg-slate-900 text-white p-6 shadow-inner">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center gap-6">
          {/* Dev Text Input */}
          <div className="flex-1 w-full flex gap-3">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSendCommand()}
              placeholder="Enter teacher command (e.g., 'Explain Gravity')"
              className="flex-1 px-5 py-4 bg-slate-800 border-2 border-slate-700 rounded-xl text-xl focus:outline-none focus:border-blue-500 transition-all text-white placeholder:text-slate-500"
            />
            <button
              onClick={handleSendCommand}
              disabled={isLoading || !inputText.trim()}
              className="p-4 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 rounded-xl transition-colors shadow-lg"
            >
              <Send size={32} />
            </button>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-4 items-center">
            {/* Source Mode Toggle Switch */}
            <div className="flex items-center gap-3 bg-slate-800 px-5 py-3 rounded-xl border border-slate-700">
              <span className="text-lg font-bold text-slate-300">Source Mode</span>
              <button
                onClick={() => {
                  const nextVal = !sourceMode;
                  setSourceMode(nextVal);
                  if (nextVal) {
                    setActiveTab("materials");
                    fetchSources();
                  }
                }}
                className={`w-14 h-8 flex items-center rounded-full p-1 transition-colors duration-300 focus:outline-none ${
                  sourceMode ? "bg-green-500" : "bg-slate-600"
                }`}
              >
                <div
                  className={`bg-white w-6 h-6 rounded-full shadow-md transform transition-transform duration-300 ${
                    sourceMode ? "translate-x-6" : "translate-x-0"
                  }`}
                ></div>
              </button>
            </div>

            <button
              onClick={isRecording ? stopRecording : startRecording}
              className={`flex items-center gap-3 px-8 py-4 rounded-xl text-2xl font-bold shadow-lg transition-transform active:scale-95 ${
                isRecording ? "bg-amber-600 hover:bg-amber-500 animate-pulse" : "bg-red-600 hover:bg-red-500"
              }`}
            >
              <Mic size={32} />
              <span>{isRecording ? "Stop" : "Listen"}</span>
            </button>
            <button
              onClick={handleRepeat}
              disabled={!response || !response.response_text}
              className="flex items-center gap-3 px-8 py-4 bg-slate-700 hover:bg-slate-600 disabled:bg-slate-800 disabled:opacity-50 rounded-xl text-2xl font-bold shadow-lg transition-transform active:scale-95"
            >
              <RotateCcw size={32} />
              <span>Repeat</span>
            </button>
            <button
              onClick={clearSession}
              className="flex items-center gap-3 px-8 py-4 bg-slate-800 hover:bg-slate-700 rounded-xl text-2xl font-bold border border-slate-600 shadow-lg transition-transform active:scale-95"
            >
              <Trash2 size={32} />
              <span>Clear</span>
            </button>
          </div>
        </div>
      </footer>
    </main>
  );
}
