import React from 'react';

const SUBJECT_STYLES = {
  Physics: 'bg-indigo-950 text-indigo-300 border-indigo-700',
  Chemistry: 'bg-emerald-950 text-emerald-300 border-emerald-700',
  Biology: 'bg-rose-950 text-rose-300 border-rose-700',
  'Computer Science': 'bg-cyan-950 text-cyan-300 border-cyan-700',
  'General Science': 'bg-slate-800 text-slate-300 border-slate-600'
};

export function SubjectBadge({ subject = 'General Science', className = '' }) {
  const style = SUBJECT_STYLES[subject] || SUBJECT_STYLES['General Science'];
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${style} ${className}`}>
      {subject}
    </span>
  );
}
