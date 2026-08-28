import React from 'react';
import { Wrench, Info } from 'lucide-react';

export function EquipmentAssistant({ equipment = [] }) {
  if (!equipment || equipment.length === 0) {
    return (
      <div className="p-6 text-center text-slate-400 text-xs bg-slate-800/40 rounded-xl border border-slate-700/80">
        No explicit apparatus/equipment listed for this experiment.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-2 text-xs font-semibold text-slate-300">
        <Wrench className="w-4 h-4 text-emerald-400" />
        <span>Identified Equipment & Apparatus ({equipment.length} items)</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {equipment.map((item, idx) => (
          <div key={idx} className="p-3.5 bg-slate-800/40 border border-slate-700/80 rounded-xl flex items-start gap-3">
            <div className="w-7 h-7 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center shrink-0 text-xs font-bold border border-emerald-500/20">
              {idx + 1}
            </div>
            <div>
              <h5 className="text-xs font-bold text-slate-100">{item}</h5>
              <p className="text-[11px] text-slate-400 mt-1 flex items-center gap-1">
                <Info className="w-3 h-3 text-slate-500" />
                <span>Required for measurement & procedure execution</span>
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
