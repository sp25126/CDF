import React from 'react';

interface MainContentProps {
  canvas: React.ReactNode;
  sidebar: React.ReactNode;
}

/**
 * MainContent: The middle section of the app shell.
 * Splits the screen between the student-facing canvas and the JULI-E/Media sidebar.
 */
export const MainContent: React.FC<MainContentProps> = ({ canvas, sidebar }) => {
  return (
    <div className="main-content-zone">
      <div className="teaching-canvas-zone custom-scrollbar">
        {canvas}
      </div>
      <aside className="sidebar-zone custom-scrollbar">
        {sidebar}
      </aside>
    </div>
  );
};

export default MainContent;
