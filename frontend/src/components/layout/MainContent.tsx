import React from 'react';

interface MainContentProps {
  canvas: React.ReactNode;
  sidebar: React.ReactNode;
  isFullWidth?: boolean;
}

/**
 * MainContent: The middle section of the app shell.
 * Splits the screen between the student-facing canvas and the JULI-E/Media sidebar.
 */
export const MainContent: React.FC<MainContentProps> = ({ canvas, sidebar, isFullWidth }) => {
  return (
    <div className={`main-content-zone ${isFullWidth ? 'full-width' : ''}`}>
      <div className="teaching-canvas-zone custom-scrollbar">
        {canvas}
      </div>
      {!isFullWidth && (
        <aside className="sidebar-zone custom-scrollbar">
          {sidebar}
        </aside>
      )}
    </div>
  );
};

export default MainContent;
