"use client";

import React, { useRef, useState } from 'react';
import { ReactSketchCanvas, ReactSketchCanvasRef } from 'react-sketch-canvas';
import { Document, Page, pdfjs } from 'react-pdf';
import { Upload, Eraser, PenTool, Trash2, Undo, Redo, ChevronLeft, ChevronRight, Image as ImageIcon, X, ZoomIn, ZoomOut } from 'lucide-react';
import { theme } from '../design/theme';
import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';
import { AssistantPayload } from '../lib/apiClient';

// Initialize PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.js`;

interface SmartWhiteboardProps {
  initialTitle?: string;
  payload?: AssistantPayload | null;
  onClose?: () => void;
}

export const SmartWhiteboard: React.FC<SmartWhiteboardProps> = ({ initialTitle, payload, onClose }) => {
  const canvasRef = useRef<ReactSketchCanvasRef>(null);
  
  // Tools state
  const [eraseMode, setEraseMode] = useState(false);
  const [strokeColor, setStrokeColor] = useState(theme.colors.primary);
  const [strokeWidth, setStrokeWidth] = useState(4);
  
  // Background document state
  const [bgFile, setBgFile] = useState<File | null>(null);
  const [bgType, setBgType] = useState<'pdf' | 'image' | null>(null);
  const [bgUrl, setBgUrl] = useState<string | null>(null);
  
  // PDF state
  const [numPages, setNumPages] = useState<number | null>(null);
  const [pageNumber, setPageNumber] = useState<number>(1);
  const [pdfScale, setPdfScale] = useState<number>(1.2);

  const visuals = payload?.visuals || [];

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (bgUrl && !visuals.some(v => v.url === bgUrl)) {
        URL.revokeObjectURL(bgUrl);
    }

    setBgFile(file);
    const objectUrl = URL.createObjectURL(file);
    setBgUrl(objectUrl);
    
    if (file.type === 'application/pdf') {
      setBgType('pdf');
      setPageNumber(1);
    } else if (file.type.startsWith('image/')) {
      setBgType('image');
    } else {
      alert("Unsupported file type. Please upload a PDF or Image.");
      setBgFile(null);
      setBgUrl(null);
      setBgType(null);
    }
    
    canvasRef.current?.clearCanvas();
  };

  const handleSelectVisual = (url: string) => {
    setBgType('image');
    setBgUrl(url);
    setBgFile(null);
    canvasRef.current?.clearCanvas();
  };

  const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages);
  };

  const toggleEraser = () => {
    setEraseMode(!eraseMode);
    canvasRef.current?.eraseMode(!eraseMode);
  };

  const handleClear = () => {
    canvasRef.current?.clearCanvas();
  };

  const handleUndo = () => {
    canvasRef.current?.undo();
  };

  const handleRedo = () => {
    canvasRef.current?.redo();
  };

  return (
    <div className="w-full h-full flex flex-col bg-white rounded-2xl overflow-hidden shadow-lg border" style={{ borderColor: theme.colors.canvas.border }}>
      
      {/* Toolbar */}
      <div className="min-h-[64px] border-b flex flex-col md:flex-row items-center justify-between px-4 md:px-6 py-3 md:py-0 gap-3 md:gap-0 bg-slate-50 shrink-0" style={{ borderColor: theme.colors.canvas.border }}>
        <div className="flex items-center gap-2 md:gap-4 flex-wrap justify-center">
            {onClose && (
              <button onClick={onClose} className="p-2 rounded-lg hover:bg-slate-200 text-slate-500 hover:text-red-500 transition-colors" title="Close Whiteboard">
                  <X size={24} />
              </button>
            )}
            <h2 className="text-lg font-semibold" style={{ color: theme.colors.canvas.ink }}>
              Whiteboard {initialTitle ? `- ${initialTitle}` : ''}
            </h2>
            <div className="w-px h-6 bg-slate-300 mx-2" />
            
            <button 
                onClick={() => { setEraseMode(false); canvasRef.current?.eraseMode(false); }}
                className={`p-2 rounded-lg transition-colors ${!eraseMode ? 'bg-blue-100 text-blue-600' : 'hover:bg-slate-200'}`}
                title="Pen"
            >
                <PenTool size={20} />
            </button>
            <button 
                onClick={toggleEraser}
                className={`p-2 rounded-lg transition-colors ${eraseMode ? 'bg-blue-100 text-blue-600' : 'hover:bg-slate-200'}`}
                title="Eraser"
            >
                <Eraser size={20} />
            </button>
            
            <input 
                type="color" 
                value={strokeColor}
                onChange={(e) => setStrokeColor(e.target.value)}
                className="w-8 h-8 rounded cursor-pointer border-0 p-0"
                disabled={eraseMode}
                title="Color"
            />
            
            <div className="w-px h-6 bg-slate-300 mx-2" />
            
            <button onClick={handleUndo} className="p-2 rounded-lg hover:bg-slate-200" title="Undo">
                <Undo size={20} />
            </button>
            <button onClick={handleRedo} className="p-2 rounded-lg hover:bg-slate-200" title="Redo">
                <Redo size={20} />
            </button>
            <button onClick={handleClear} className="p-2 rounded-lg hover:bg-slate-200 text-red-500" title="Clear Canvas">
                <Trash2 size={20} />
            </button>
        </div>

        <div className="flex items-center gap-2 md:gap-4 flex-wrap justify-center">
            {bgType === 'pdf' && numPages && (
                <div className="flex items-center gap-2 mr-4 bg-white px-3 py-1 rounded-full border">
                    <button onClick={() => setPdfScale(s => Math.max(0.5, s - 0.2))} className="p-1 hover:bg-slate-100 rounded" title="Zoom Out">
                        <ZoomOut size={16} />
                    </button>
                    <span className="text-sm font-medium w-12 text-center">{Math.round(pdfScale * 100)}%</span>
                    <button onClick={() => setPdfScale(s => Math.min(3, s + 0.2))} className="p-1 hover:bg-slate-100 rounded" title="Zoom In">
                        <ZoomIn size={16} />
                    </button>
                    
                    <div className="w-px h-4 bg-slate-300 mx-1" />
                    
                    <button 
                        disabled={pageNumber <= 1} 
                        onClick={() => {
                            setPageNumber(prev => Math.max(prev - 1, 1));
                            canvasRef.current?.clearCanvas();
                        }}
                        className="p-1 disabled:opacity-50 hover:bg-slate-100 rounded"
                    >
                        <ChevronLeft size={16} />
                    </button>
                    <span className="text-sm font-medium">Page {pageNumber} of {numPages}</span>
                    <button 
                        disabled={pageNumber >= numPages} 
                        onClick={() => {
                            setPageNumber(prev => Math.min(prev + 1, numPages));
                            canvasRef.current?.clearCanvas();
                        }}
                        className="p-1 disabled:opacity-50 hover:bg-slate-100 rounded"
                    >
                        <ChevronRight size={16} />
                    </button>
                </div>
            )}
            
            <label className="flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-600 rounded-lg cursor-pointer hover:bg-blue-100 transition-colors font-medium text-sm">
                <Upload size={18} />
                Import Document
                <input 
                    type="file" 
                    accept=".pdf,image/*" 
                    onChange={handleFileUpload} 
                    className="hidden" 
                />
            </label>
        </div>
      </div>

      <div className="flex-1 flex flex-col md:flex-row overflow-hidden">
        {/* Media Sidebar */}
        {visuals.length > 0 && (
          <div className="w-full md:w-48 border-b md:border-b-0 md:border-r bg-slate-50 overflow-x-auto md:overflow-y-auto p-4 flex flex-row md:flex-col gap-4 shrink-0" style={{ borderColor: theme.colors.canvas.border }}>
            <h3 className="text-sm font-semibold text-slate-500 md:mb-2 uppercase tracking-wider hidden md:block">Topic Media</h3>
            {visuals.map((vis, i) => (
              <button 
                key={i} 
                className={`w-32 md:w-full shrink-0 overflow-hidden rounded-lg border-2 transition-all hover:opacity-80 ${bgUrl === vis.url ? 'border-blue-500 shadow-md' : 'border-transparent shadow-sm'}`}
                onClick={() => handleSelectVisual(vis.url)}
                title={vis.title}
              >
                <img src={vis.url} alt={vis.title} className="w-full object-cover" style={{ aspectRatio: '16/9' }} />
              </button>
            ))}
          </div>
        )}

        {/* Canvas Area */}
        <div className="flex-1 relative bg-slate-200 overflow-auto flex p-2 md:p-6 min-w-0 min-h-0">
          <div className={`relative shadow-xl bg-white w-full min-h-[600px] flex-1 mx-auto ${bgType === 'pdf' ? 'h-max' : 'h-full'}`} style={{ maxWidth: bgType === 'pdf' ? 'none' : '100%' }}>
              {/* Background Layer */}
              <div className="relative pointer-events-none flex items-center justify-center w-full min-h-full">
                  {!bgUrl && (
                      <div className="text-slate-400 flex flex-col items-center text-center px-8">
                          <ImageIcon size={48} className="mb-2 opacity-50" />
                          <p>Import a PDF or Image, or select topic media from the sidebar to annotate</p>
                      </div>
                  )}
                  {bgType === 'image' && bgUrl && (
                      <img src={bgUrl} alt="Whiteboard Background" className="absolute inset-0 w-full h-full object-contain" />
                  )}
                  {bgType === 'pdf' && bgUrl && (
                      <div className="w-full flex justify-center items-start pt-4 pb-4">
                        <Document 
                            file={bgUrl} 
                            onLoadSuccess={onDocumentLoadSuccess}
                            className="flex flex-col items-center"
                        >
                            <Page pageNumber={pageNumber} scale={pdfScale} renderTextLayer={false} renderAnnotationLayer={false} className="shadow-sm" />
                        </Document>
                      </div>
                  )}
              </div>

              {/* Drawing Layer */}
              <ReactSketchCanvas
                  ref={canvasRef}
                  strokeWidth={strokeWidth}
                  strokeColor={strokeColor}
                  canvasColor="transparent"
                  className="absolute inset-0 z-10"
                  style={{ border: 'none' }}
                  preserveBackgroundImageAspectRatio="none"
              />
          </div>
        </div>
      </div>
    </div>
  );
};

export default SmartWhiteboard;
