import { useState, useRef, useEffect, useCallback } from "react";

interface UseHandsFreeProps {
  onCommand: (text: string) => void;
  onStateChange?: (state: "idle" | "listening" | "speaking" | "thinking") => void;
}

export function useHandsFree({ onCommand, onStateChange }: UseHandsFreeProps) {
  const [isActive, setIsActive] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef<any>(null);
  const pauseTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    setIsListening(false);
    if (onStateChange) onStateChange("idle");
  }, [onStateChange]);

  const startListening = useCallback(() => {
    if (!isActive) return;
    
    try {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (!SpeechRecognition) {
        console.warn("Speech recognition not supported");
        return;
      }

      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }

      const rec = new SpeechRecognition();
      rec.continuous = true;
      rec.interimResults = true;
      rec.lang = "hi-IN"; // Good default for Hinglish/Hindi

      rec.onstart = () => {
        setIsListening(true);
        if (onStateChange) onStateChange("listening");
      };

      rec.onresult = (event: any) => {
        let finalTranscript = "";
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
          }
        }

        if (finalTranscript.trim()) {
          // User spoke a final phrase
          if (pauseTimeoutRef.current) {
            clearTimeout(pauseTimeoutRef.current);
          }
          
          // Wait 1.5 seconds of silence before submitting
          pauseTimeoutRef.current = setTimeout(() => {
            stopListening();
            if (onStateChange) onStateChange("thinking");
            onCommand(finalTranscript.trim());
          }, 1500);
        }
      };

      rec.onerror = (e: any) => {
        console.error("Hands-free recognition error:", e.error);
        if (e.error === "no-speech" || e.error === "network") {
            // Keep trying if it's active
            setTimeout(() => {
                if (isActive) startListening();
            }, 1000);
        } else {
            setIsListening(false);
            if (onStateChange) onStateChange("idle");
        }
      };

      rec.onend = () => {
        setIsListening(false);
        // Automatically restart if still active
        if (isActive) {
          startListening();
        }
      };

      recognitionRef.current = rec;
      rec.start();
    } catch (err) {
      console.error("Error starting hands-free listening", err);
    }
  }, [isActive, onCommand, onStateChange, stopListening]);

  useEffect(() => {
    if (isActive) {
      startListening();
    } else {
      stopListening();
    }
    
    return () => {
      if (pauseTimeoutRef.current) clearTimeout(pauseTimeoutRef.current);
      stopListening();
    };
  }, [isActive, startListening, stopListening]);

  return {
    isActive,
    setIsActive,
    isListening,
    startListening,
    stopListening
  };
}
