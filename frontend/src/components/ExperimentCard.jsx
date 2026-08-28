import React from 'react';
import { ListChecks, Wrench, ShieldAlert, ChevronRight } from 'lucide-react';
import { SubjectBadge } from './SubjectBadge';

export function ExperimentCard({ experiment, isSelected, onSelect }) {
  const stepsCount = experiment.procedure?.length || 0;
  const equipmentCount = experiment.equipment?.length || 0;
  const safetyCount = experiment.safety?.length || 0;

  return (
    <div
      onClick={onSelect}
      className={`p-4 rounded-xl border transition-all cursor-pointer relative overflow-hidden group ${
        isSelected
          ? 'bg-blue-950/40 border-blue-500 shadow-lg shadow-blue-500/10'
          : 'bg-slate-800/60 border-slate-700/80 hover:bg-slate-800 hover:border-slate-600'
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="text-xs font-bold px-2 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30">
              Exp {experiment.experiment_number}
            </span>
            <SubjectBadge subject={experiment.subject} />
          </div>
          <h3 className="font-semibold text-slate-100 text-sm group-hover:text-blue-300 transition line-clamp-2">
            {experiment.title}
          </h3>
        </div>
        <ChevronRight className={`w-5 h-5 transition-transform ${isSelected ? 'text-blue-400 translate-x-1' : 'text-slate-500 group-hover:text-slate-300'}`} />
      </div>

      <p className="text-xs text-slate-400 mt-2 line-clamp-2 italic">
        "{experiment.aim}"
      </p>

      <div className="mt-4 pt-3 border-t border-slate-700/60 flex items-center gap-4 text-[11px] text-slate-400">
        <div className="flex items-center gap-1">
          <ListChecks className="w-3.5 h-3.5 text-blue-400" />
          <span>{stepsCount} Steps</span>
        </div>
        <div className="flex items-center gap-1">
          <Wrench className="w-3.5 h-3.5 text-emerald-400" />
          <span>{equipmentCount} Apparatus</span>
        </div>
        {safetyCount > 0 && (
          <div className="flex items-center gap-1 text-amber-400">
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>{safetyCount} Safety Rules</span>
          </div>
        )}
      </div>
    </div>
  );
}
