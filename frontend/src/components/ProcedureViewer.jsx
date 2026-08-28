import React, { useState } from 'react';
import { CheckCircle2, Circle, AlertTriangle, ListChecks, RotateCcw } from 'lucide-react';

export function ProcedureViewer({ procedure = [], safety = [] }) {
  const [completedSteps, setCompletedSteps] = useState(new Set());

  const toggleStep = (index) => {
    const next = new Set(completedSteps);
    if (next.has(index)) {
      next.delete(index);
    } else {
      next.add(index);
    }
    setCompletedSteps(next);
  };

  const resetProgress = () => {
    setCompletedSteps(new Set());
  };

  const progressPercent = procedure.length > 0 ? Math.round((completedSteps.size / procedure.length) * 100) : 0;

  return (
    <div className="space-y-4">
      {/* Header & Progress Bar */}
      <div className="flex items-center justify-between bg-slate-950/60 p-4 rounded-xl border border-slate-800">
        <div className="flex items-center gap-3">
          <ListChecks className="w-5 h-5 text-blue-400" />
          <div>
            <h4 className="text-sm font-semibold text-slate-200">Step-by-Step Practical Procedure</h4>
            <p className="text-xs text-slate-400">
              {completedSteps.size} of {procedure.length} steps completed ({progressPercent}%)
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="w-32 bg-slate-800 rounded-full h-2 overflow-hidden border border-slate-700">
            <div
              className="bg-blue-500 h-full transition-all duration-300"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
          {completedSteps.size > 0 && (
            <button
              onClick={resetProgress}
              title="Reset progress"
              className="p-1.5 rounded-lg bg-slate-800 text-slate-400 hover:text-white transition"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Safety Banner */}
      {safety.length > 0 && (
        <div className="p-3 bg-amber-950/40 border border-amber-800/60 rounded-xl text-amber-300 text-xs flex items-start gap-2.5">
          <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
          <div>
            <span className="font-bold">Important Safety Reminder:</span> Review safety precautions before commencing step 1.
          </div>
        </div>
      )}

      {/* Steps List */}
      <div className="space-y-3">
        {procedure.map((step, idx) => {
          const isDone = completedSteps.has(idx);
          return (
            <div
              key={idx}
              onClick={() => toggleStep(idx)}
              className={`p-4 rounded-xl border transition cursor-pointer flex items-start gap-3 ${
                isDone
                  ? 'bg-emerald-950/20 border-emerald-800/50 text-slate-300'
                  : 'bg-slate-800/40 border-slate-700/70 hover:bg-slate-800/70 text-slate-200'
              }`}
            >
              <button className="mt-0.5 shrink-0 text-slate-400 hover:text-emerald-400 transition">
                {isDone ? (
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                ) : (
                  <Circle className="w-5 h-5 text-slate-500" />
                )}
              </button>

              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className={`text-xs font-bold px-2 py-0.5 rounded ${isDone ? 'bg-emerald-500/20 text-emerald-300' : 'bg-blue-500/10 text-blue-400 border border-blue-500/20'}`}>
                    Step {idx + 1}
                  </span>
                </div>
                <p className={`text-xs leading-relaxed ${isDone ? 'line-through text-slate-400' : 'text-slate-200'}`}>
                  {step}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
