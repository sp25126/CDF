import React, { useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { motionTokens } from '../design/motion';
import { useReducedMotion } from '../hooks/useReducedMotion';
import { useSpeechStore } from '../state/speechStore';

import ExplainCard, { Explanation } from './cards/ExplainCard';
import QuizCard, { Quiz } from './cards/QuizCard';
import MaterialsView, { Material } from './cards/MaterialsView';
import ErrorState from './ErrorState';
import LoadingState from './LoadingState';
import EmptyState from './EmptyState';

import JuliEPanel from './JuliEPanel';

type CanvasState = 'idle' | 'explain' | 'quiz' | 'materials' | 'loading' | 'error';

interface ResponseRendererProps {
  state: CanvasState;
  payload?: {
    explanation?: Explanation;
    quiz?: Quiz;
    material?: Material;
    next_actions?: string[];
  };
  error?: { message: string };
  onActionClick: (action: string) => void;
  onRetry: () => void;
}

/**
 * ResponseRenderer: The primary student-facing learning area.
 * Switches between different card views based on app state.
 */
export const ResponseRenderer: React.FC<ResponseRendererProps> = ({ 
  state = 'idle',
  payload,
  error,
  onActionClick,
  onRetry
}) => {
  const prefersReducedMotion = useReducedMotion();
  const variants = prefersReducedMotion ? {} : motionTokens.variants.page;
  const constraintsRef = useRef<HTMLDivElement>(null);
  
  const { currentWordIndex, isPlaying, spokenText } = useSpeechStore();
  const words = spokenText ? spokenText.split(/\s+/).filter(w => w.length > 0) : [];

  const renderContent = () => {
    switch (state) {
      case 'loading':
        return <LoadingState />;
      case 'explain':
        return payload?.explanation ? (
          <ExplainCard 
            explanation={payload.explanation} 
            actions={payload.next_actions || []}
            onActionClick={onActionClick}
          />
        ) : <EmptyState message="The explanation could not be loaded." onRetry={onRetry} />;
      case 'quiz':
        return payload?.quiz ? <QuizCard quiz={payload.quiz} /> : <EmptyState message="The quiz could not be loaded." onRetry={onRetry} />;
      case 'materials':
        return payload?.material ? <MaterialsView material={payload.material} /> : <EmptyState message="The materials could not be found." onRetry={onRetry} />;
      case 'error':
        return <ErrorState message={error?.message || "An unknown error occurred."} onRetry={onRetry} />;
      case 'idle':
      default:
        return (
          <div className="flex flex-col items-center justify-center text-center mt-12">
            <h2 className="text-3xl font-bold text-slate-700">Awaiting teacher command...</h2>
            <p className="text-xl mt-2 text-slate-500">
              Try: "Explain photosynthesis" or "Quiz me on the solar system".
            </p>
          </div>
        );
    }
  };

  const isCentered = state === 'idle' || state === 'loading' || state === 'error';

  return (
    <div ref={constraintsRef} className="teaching-canvas-zone custom-scrollbar flex h-full p-8 relative overflow-hidden">
      {/* JuliE container */}
      <motion.div
        layout
        className={
           isCentered
             ? "absolute inset-0 flex flex-col items-center justify-center pointer-events-none mb-32 z-40"
             : "flex-none w-48 mr-8 z-40"
        }
      >
        <motion.div
          drag
          dragConstraints={constraintsRef}
          dragElastic={0.1}
          dragMomentum={false}
          className="pointer-events-auto cursor-grab active:cursor-grabbing relative flex flex-col items-center"
        >
          <JuliEPanel className="border-none p-0" />
          
          {/* Floating Speech Bubble with Real-time Word Highlighting */}
          {isPlaying && words.length > 0 && (
            <div className="absolute top-full mt-4 w-72 bg-white border border-slate-200 rounded-2xl p-4 shadow-xl text-sm text-slate-800 z-50 transition-all duration-200">
              <div className="absolute bottom-full left-1/2 -translate-x-1/2 w-0 h-0 border-8 border-transparent" style={{ borderBottomColor: '#ffffff' }} />
              
              <div className="leading-relaxed text-center">
                {words.map((word, idx) => {
                  const isActive = idx === currentWordIndex;
                  return (
                    <span
                      key={idx}
                      className={`inline-block mr-1 transition-all duration-150 ${
                        isActive
                          ? 'text-indigo-600 font-extrabold scale-110 bg-indigo-50 px-1 rounded shadow-sm'
                          : 'text-slate-700 font-medium'
                      }`}
                    >
                      {word}
                    </span>
                  );
                })}
              </div>
            </div>
          )}
        </motion.div>
      </motion.div>
      
      {/* Cards container */}
      <motion.div layout className={`flex-1 ${isCentered ? 'mt-96' : ''}`}>
        <AnimatePresence mode="wait">
          <motion.div 
            key={state} 
            variants={variants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={motionTokens.transition.default as any}
          >
            {renderContent()}
          </motion.div>
        </AnimatePresence>
      </motion.div>
    </div>
  );
};

export default ResponseRenderer;
