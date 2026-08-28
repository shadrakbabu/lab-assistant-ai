import React, { useState } from 'react';
import { BookOpen, Sparkles, Target } from 'lucide-react';

export function TheorySection({ theory = '', aim = '' }) {
  const [isSimpleMode, setIsSimpleMode] = useState(false);

  return (
    <div className="space-y-4">
      {/* Aim Box */}
      <div className="p-4 bg-slate-950/60 border border-slate-800 rounded-xl flex items-start gap-3">
        <Target className="w-5 h-5 text-blue-400 shrink-0 mt-0.5" />
        <div>
          <h4 className="text-xs uppercase font-bold text-blue-400 tracking-wider">Experiment Aim & Objective</h4>
          <p className="text-sm text-slate-200 mt-1 font-medium leading-relaxed">{aim}</p>
        </div>
      </div>

      {/* Theory Card */}
      <div className="bg-slate-800/40 border border-slate-700/80 rounded-xl p-5">
        <div className="flex items-center justify-between mb-4 border-b border-slate-700/60 pb-3">
          <div className="flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-blue-400" />
            <h4 className="text-sm font-semibold text-slate-200">Scientific Theory & Principles</h4>
          </div>

          <button
            onClick={() => setIsSimpleMode(!isSimpleMode)}
            className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold transition border ${
              isSimpleMode
                ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white border-blue-400 shadow-md shadow-blue-500/20'
                : 'bg-slate-800 text-slate-300 border-slate-700 hover:border-slate-600'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>{isSimpleMode ? 'Simple Explanation Mode Active' : 'Enable Simple Explanation'}</span>
          </button>
        </div>

        {isSimpleMode ? (
          <div className="p-4 bg-blue-950/30 border border-blue-800/50 rounded-xl text-blue-100 text-xs leading-relaxed space-y-3">
            <p className="font-semibold text-blue-300">💡 Student Summary:</p>
            <p>{theory || 'This experiment verifies key physical/chemical properties through controlled measurements.'}</p>
            <div className="pt-2 border-t border-blue-800/40 text-[11px] text-blue-300">
              📌 Practical Connection: The steps you perform directly measure parameters explained in the equations above.
            </div>
          </div>
        ) : (
          <div className="text-xs text-slate-300 leading-relaxed whitespace-pre-line font-mono bg-slate-950/40 p-4 rounded-xl border border-slate-800/80">
            {theory || 'No detailed theory text extracted for this experiment section.'}
          </div>
        )}
      </div>
    </div>
  );
}
