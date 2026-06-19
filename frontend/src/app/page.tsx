"use client";

import { useState, useEffect } from "react";

// State Machine & Hooks
import { useAppState } from "../state/useAppState";
import { useCommandSubmit } from "../hooks/useCommandSubmit";
import { useAppEvents } from "../state/useAppEvents";
import { useTranscriptStore } from "../state/transcriptStore";
import { clearSession as clearPersistedSession } from '../state/persistence';
import { rotateSessionId } from '../state/sessionStore';
import { resetSession } from '../lib/apiClient';
import { SettingsProvider, useSettings } from '../state/settingsStore';

// Layout Components
import AppShell from "../components/AppShell";
import MainContent from "../components/layout/MainContent";
import TopContextBar from "../components/TopContextBar";
import TeacherConsole from "../components/TeacherConsole";
import ResponseRenderer from "../components/ResponseRenderer";
import dynamic from 'next/dynamic';
const SmartWhiteboard = dynamic(() => import("../components/SmartWhiteboard"), { ssr: false });
import JuliEPanel from "../components/JuliEPanel";
import MediaRail from "../components/MediaRail";
import SettingsModal from "../components/settings/SettingsModal";

// Other components
import { useVoiceSession } from "../voice/voiceRouter";

export default function Home() {
  return (
    <SettingsProvider>
      <HomeInner />
    </SettingsProvider>
  );
}

function HomeInner() {
  const { apiKey, provider, model, isSaved, openSettings } = useSettings();
  const { state, transitionTo, setPayload } = useAppState();
  const [command, setCommand] = useState("");
  const { history, clearHistory } = useTranscriptStore();
  const { dispatch } = useAppEvents();

  // The new command submission hook
  const { submit: submitCommand, isLoading, error } = useCommandSubmit();

  const handleCommandSubmit = (text: string) => {
    if (!text.trim()) return;
    // Pass user key if set
    submitCommand(text, isSaved && apiKey ? { userApiKey: apiKey, userProvider: provider, userModel: model } : undefined);
    setCommand("");
  };

  // Hands-free voice session hook
  const {
    enable: enableVoice,
    disable: disableVoice,
    isListening: isVoiceListening,
  } = useVoiceSession({
    onCommand: (text) => handleCommandSubmit(text),
  });

  // Sync state.topBar.handsFree with useVoiceSession
  useEffect(() => {
    if (state.topBar.handsFree) {
      enableVoice();
    } else {
      disableVoice();
    }
  }, [state.topBar.handsFree, enableVoice, disableVoice]);
  
  const handleHandsFreeToggle = () => {
    const isEnabling = !state.topBar.handsFree;
    transitionTo(isEnabling ? 'hands_free_active' : 'idle', {
      topBar: { ...state.topBar, handsFree: isEnabling }
    });
  };

  const handleSourceModeToggle = () => {
    const isEnabling = !state.topBar.sourceMode;
    transitionTo(state.name, {
        topBar: { ...state.topBar, sourceMode: isEnabling }
    });
    if (isEnabling) {
      dispatch({ type: 'SOURCE_MODE_ACTIVATED' });
    }
  }

  const handleWhiteboardToggle = () => {
    const isEnabling = !state.topBar.isWhiteboardActive;
    transitionTo(state.name, {
        topBar: { ...state.topBar, isWhiteboardActive: isEnabling }
    });
  };

  // No duplicate RESPONSE_RECEIVED dispatch needed here —
  // useCommandSubmit dispatches it immediately after the API returns.

  // Derived state for props
  const canvasState = state.name === 'processing' ? 'loading' : state.canvasMode;

  return (
    <>
      <AppShell
        topBar={
            <TopContextBar
              currentTopic={state.payload?.title}
              languageMode={state.topBar.language}
              isHandsFree={state.topBar.handsFree}
              isSourceMode={state.topBar.sourceMode}
              onSettingsOpen={openSettings}
            />
          }
      mainContent={
        <MainContent
          isFullWidth={state.topBar.isWhiteboardActive}
          canvas={
            state.topBar.isWhiteboardActive ? (
              <SmartWhiteboard initialTitle={state.payload?.title} payload={state.payload} onClose={handleWhiteboardToggle} />
            ) : (
              <ResponseRenderer
                state={canvasState}
                payload={state.payload}
                error={state.error}
                onActionClick={(action) => handleCommandSubmit(action)}
                onRetry={() => handleCommandSubmit(history[0]?.command || "")}
              />
            )
          }
          sidebar={
            <MediaRail payload={state.payload} />
          }
        />
      }
      teacherConsole={
        state.topBar.isWhiteboardActive ? null : (
        <TeacherConsole
          isLoading={isLoading}
          isWhiteboardActive={state.topBar.isWhiteboardActive}
          isListening={state.name === 'listening' || isVoiceListening}
          isHandsFree={state.topBar.handsFree}
          isSourceMode={state.topBar.sourceMode}
          command={command}
          lastCommands={history.map((h) => h.command)}
          onCommandChange={setCommand}
          onCommandSubmit={() => handleCommandSubmit(command)}
          onListenClick={() => {
            transitionTo('listening');
            dispatch({ type: 'MIC_OPEN' });
          }}
          onHandsFreeToggle={handleHandsFreeToggle}
          onSourceModeToggle={handleSourceModeToggle}
          onWhiteboardToggle={handleWhiteboardToggle}
          onRepeatClick={() => { 
            dispatch({ type: 'TTS_START' });
            if (state.payload?.audio_base64) {
              import('../hooks/useCommandSubmit').then(({ playAudio }) => {
                playAudio(state.payload!.audio_base64!, () => dispatch({ type: 'TTS_END' }));
              });
            } else {
              setTimeout(() => dispatch({ type: 'TTS_END' }), 3000);
            }
          }}
          onClearClick={async () => {
            clearPersistedSession();
            clearHistory();
            setPayload(null);
            transitionTo('idle');
            dispatch({ type: 'CLEAR_SESSION' });
            // Rotate session ID so the next request starts a fresh session
            const oldSessionId = rotateSessionId();
            // Tell the backend to clear the session memory (fire-and-forget)
            resetSession(oldSessionId).catch(() => {});
          }}
          onMacroPillClick={(pill) => handleCommandSubmit(`${pill} ${state.payload?.title || ''}`)}
        />
        )
      }
    />
    <SettingsModal />
    </>
  );
}
