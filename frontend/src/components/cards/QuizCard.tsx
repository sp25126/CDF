import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { theme } from '../../design/theme';

export interface Quiz {
  questions: {
    question: string;
    options: string[];
    correct_index: number;
    explanation: string;
  }[];
}

interface QuizCardProps {
  quiz: Quiz;
}

/**
 * QuizCard: A stateful component to manage a multi-question quiz.
 */
export const QuizCard: React.FC<QuizCardProps> = ({ quiz }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [showAnswer, setShowAnswer] = useState(false);
  const [score, setScore] = useState(0);
  const [isFinished, setIsFinished] = useState(false);

  if (!quiz || !quiz.questions || quiz.questions.length === 0) {
    return <div>Quiz data is missing or invalid.</div>;
  }

  const currentQuestion = quiz.questions[currentIndex];
  const totalQuestions = quiz.questions.length;

  const handleSelectAnswer = (index: number) => {
    if (showAnswer) return;
    setSelectedAnswer(index);
  };

  const handleShowAnswer = () => {
    setShowAnswer(true);
    if (selectedAnswer === currentQuestion.correct_index) {
      setScore(prev => prev + 1);
    }
  };

  const handleNextQuestion = () => {
    if (currentIndex === totalQuestions - 1) {
      setIsFinished(true);
    } else {
      setShowAnswer(false);
      setSelectedAnswer(null);
      setCurrentIndex(prev => prev + 1);
    }
  };
  
  const getOptionStyle = (index: number) => {
    if (!showAnswer) {
      return selectedAnswer === index ? 'border-indigo-600 bg-indigo-50' : 'border-slate-200 bg-white';
    }
    if (index === currentQuestion.correct_index) {
      return 'border-green-600 bg-green-50';
    }
    if (index === selectedAnswer) {
      return 'border-red-600 bg-red-50';
    }
    return 'border-slate-200 bg-white';
  };

  if (isFinished) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-4xl mx-auto text-center p-12 bg-white rounded-2xl shadow-xl border-2 border-slate-100"
      >
        <h2 style={{ fontSize: theme.typography.fontSize['4xl'], color: theme.colors.primary }} className="font-bold mb-6">
          Quiz Complete!
        </h2>
        <p className="text-2xl text-slate-600 mb-8">
          You scored <span className="font-bold text-slate-800">{score}</span> out of <span className="font-bold text-slate-800">{totalQuestions}</span>
        </p>
        <button
          onClick={() => {
            setIsFinished(false);
            setCurrentIndex(0);
            setScore(0);
            setShowAnswer(false);
            setSelectedAnswer(null);
          }}
          className="px-8 py-4 rounded-lg font-bold text-white transition-transform hover:scale-105"
          style={{ backgroundColor: theme.colors.primary }}
        >
          Retake Quiz
        </button>
      </motion.div>
    );
  }

  return (
    <motion.div
      key={currentIndex}
      initial={{ opacity: 0, x: 50 }}
      animate={{ opacity: 1, x: 0 }}
      className="w-full max-w-4xl mx-auto"
    >
      {/* Progress Bar */}
      <div className="mb-6">
        <p className="font-semibold mb-2" style={{ color: theme.colors.canvas.muted }}>
          Question {currentIndex + 1}/{totalQuestions}
        </p>
        <div className="w-full bg-slate-200 rounded-full h-2.5">
          <div
            className="h-2.5 rounded-full transition-all duration-500"
            style={{ width: `${((currentIndex + 1) / totalQuestions) * 100}%`, backgroundColor: theme.colors.primary }}
          ></div>
        </div>
      </div>

      <h2 style={{ fontSize: theme.typography.fontSize['2xl']}} className="font-bold text-center mb-10">
        {currentQuestion.question}
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {currentQuestion.options.map((option, index) => (
          <button
            key={index}
            onClick={() => handleSelectAnswer(index)}
            disabled={showAnswer}
            className={`p-6 text-left rounded-lg shadow-md border-2 transition-all ${getOptionStyle(index)}`}
            style={{ fontSize: theme.typography.fontSize.lg }}
          >
            <span className="font-bold mr-3">{String.fromCharCode(65 + index)}.</span>
            {option}
          </button>
        ))}
      </div>
      
      {showAnswer && (
        <motion.div initial={{opacity:0}} animate={{opacity:1}} className="mt-6 p-4 bg-slate-50 rounded-lg border-slate-200">
            <h4 className="font-bold text-slate-800">Explanation</h4>
            <p className="text-slate-600">{currentQuestion.explanation}</p>
        </motion.div>
      )}

      <div className="text-center mt-12">
        {!showAnswer ? (
          <button
            onClick={handleShowAnswer}
            disabled={selectedAnswer === null}
            className="px-8 py-4 rounded-lg font-bold text-white disabled:opacity-50"
            style={{ backgroundColor: theme.colors.primary }}
          >
            Show Answer
          </button>
        ) : (
          <button
            onClick={handleNextQuestion}
            className="px-8 py-4 rounded-lg font-bold text-white"
            style={{ backgroundColor: theme.colors.success }}
          >
            {currentIndex === totalQuestions - 1 ? "Finish Quiz" : "Next Question"}
          </button>
        )}
      </div>
    </motion.div>
  );
};

export default QuizCard;
