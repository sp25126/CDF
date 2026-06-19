import React from 'react';

const SkeletonBase = ({ className }: { className: string }) => (
  <div className={`bg-slate-200 rounded animate-pulse ${className}`} />
);

const ExplainCardSkeleton = () => (
  <div className="space-y-8">
    <SkeletonBase className="h-12 w-3/4" />
    <div className="space-y-4">
      <SkeletonBase className="h-8 w-full" />
      <SkeletonBase className="h-8 w-5/6" />
      <SkeletonBase className="h-8 w-full" />
      <SkeletonBase className="h-8 w-4/6" />
    </div>
    <SkeletonBase className="h-24 w-full" />
    <div className="flex gap-4">
        <SkeletonBase className="h-12 w-24" />
        <SkeletonBase className="h-12 w-24" />
        <SkeletonBase className="h-12 w-24" />
    </div>
  </div>
);

export const Skeletons = {
    ExplainCard: ExplainCardSkeleton,
}
