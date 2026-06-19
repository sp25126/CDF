import React from 'react';
import '../styles/layout.css';

interface AppShellProps {
  topBar: React.ReactNode;
  mainContent: React.ReactNode;
  teacherConsole: React.ReactNode;
}

/**
 * AppShell: The root layout container.
 * Implements the 3-zone grid architecture: TopBar, MainContent, TeacherConsole.
 */
export const AppShell: React.FC<AppShellProps> = ({ topBar, mainContent, teacherConsole }) => {
  return (
    <div className="app-grid">
      <div className="top-bar-zone">
        {topBar}
      </div>
      
      {mainContent}
      
      <div className="teacher-console-zone">
        {teacherConsole}
      </div>
    </div>
  );
};

export default AppShell;
