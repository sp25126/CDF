import React from 'react';
import { FileText } from 'lucide-react';
import { theme } from '../../design/theme';

export interface Material {
  type: 'pdf' | 'image' | 'text';
  source: string; // URL for PDF/image, or raw text content
  title: string;
}

interface MaterialsViewProps {
  material: Material;
}

/**
 * MaterialsView: Displays source-linked material (PDF, image, or text).
 */
export const MaterialsView: React.FC<MaterialsViewProps> = ({ material }) => {
  if (!material) return null;

  const { type, source, title } = material;

  return (
    <div className="w-full h-full flex flex-col rounded-lg overflow-hidden bg-slate-100 border" style={{borderColor: theme.colors.canvas.border}}>
      <div className="p-4 bg-white border-b" style={{borderColor: theme.colors.canvas.border}}>
        <h3 className="font-bold text-xl" style={{color: theme.colors.canvas.ink}}>{title}</h3>
      </div>
      <div className="flex-1 relative">
        {type === 'pdf' && <iframe src={source} className="w-full h-full border-0" title={title} />}
        {type === 'image' && <img src={source} alt={title} className="w-full h-full object-contain" />}
        {type === 'text' && <div className="p-6 text-lg whitespace-pre-wrap">{source}</div>}
      </div>
    </div>
  );
};

export default MaterialsView;
