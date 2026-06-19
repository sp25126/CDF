import React from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { useReducedMotion } from '../hooks/useReducedMotion';
import { motionTokens } from '../design/motion';

import SummaryCard from './cards/SummaryCard';
import VisualDiagramCard from './cards/VisualDiagramCard';
import BestVideoCard from './cards/BestVideoCard';
import AlternativeVideoCard from './cards/AlternativeVideoCard';
import { SourceChips } from './SourceChips';
import SidebarEmptyState from './cards/SidebarEmptyState';
import { Visual } from './cards/VisualDiagramCard';
import { Video } from './cards/BestVideoCard';

interface SourceRef {
  title: string;
  snippet: string;
  page_number?: number;
  section_label?: string;
}

interface MediaRailProps {
  payload?: {
    summary?: string;
    visual?: Visual;
    best_video?: Video;
    alternative_videos?: Video[];
    source_refs?: SourceRef[];
  };
}

const containerVariants = {
    animate: {
        transition: {
            staggerChildren: 0.1,
        },
    },
};

/**
 * MediaRail: The right-hand column for supporting media, driven by live data.
 */
export const MediaRail: React.FC<MediaRailProps> = ({ payload }) => {
    const prefersReducedMotion = useReducedMotion();
    const itemVariants = prefersReducedMotion ? {} : motionTokens.variants.item;

    const hasMedia = payload && (
        payload.summary || 
        payload.visual || 
        payload.best_video || 
        (payload.alternative_videos && payload.alternative_videos.length > 0) ||
        (payload.source_refs && payload.source_refs.length > 0)
    );

    return (
        <div className="flex-1 overflow-y-auto custom-scrollbar">
            <motion.div 
                className="p-6 space-y-6"
                variants={containerVariants}
                initial="initial"
                animate="animate"
            >
                <AnimatePresence>
                    {!hasMedia && <SidebarEmptyState />}
                    {payload?.summary && <motion.div variants={itemVariants}><SummaryCard text={payload.summary} /></motion.div>}
                    {payload?.visual && <motion.div variants={itemVariants}><VisualDiagramCard visual={payload.visual} /></motion.div>}
                    {payload?.best_video && <motion.div variants={itemVariants}><BestVideoCard video={payload.best_video} /></motion.div>}
                    {payload?.alternative_videos && payload.alternative_videos.length > 0 && (
                        <motion.div variants={itemVariants}><AlternativeVideoCard videos={payload.alternative_videos} /></motion.div>
                    )}
                    {payload?.source_refs && payload.source_refs.length > 0 && (
                        <motion.div variants={itemVariants}><SourceChips citations={payload.source_refs} /></motion.div>
                    )}
                </AnimatePresence>
            </motion.div>
        </div>
    );
};

export default MediaRail;
