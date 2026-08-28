import React from 'react';
import { ShieldAlert, AlertOctagon, UserCheck } from 'lucide-react';

export function SafetyAlerts({ safety = [] }) {
  return (
    <div className="space-y-4">
      {/* Permanent Supervision Notice */}
      <div className="p-4 bg-amber-950/40 border border-amber-800/80 rounded-xl text-amber-200 text-xs flex items-start gap-3">
        <UserCheck className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
        <div>
          <h4 className="font-bold text-amber-300 text-sm">Laboratory Supervision Mandate</h4>
          <p className="mt-1 leading-relaxed text-amber-200/90">
            All experiments must be performed under the direct supervision of a qualified laboratory instructor or teaching assistant. Always wear appropriate personal protective equipment (PPE).
          </p>
        </div>
      </div>

      {/* Safety Instructions extracted from manual */}
      {safety.length > 0 ? (
        <div className="space-y-2.5">
          <h4 className="text-xs font-semibold text-slate-300 flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-rose-400" />
            <span>Extracted Precautions & Safety Warnings ({safety.length})</span>
          </h4>

          {safety.map((item, idx) => (
            <div key={idx} className="p-3 bg-rose-950/20 border border-rose-900/40 rounded-xl flex items-start gap-3 text-xs text-rose-200">
              <AlertOctagon className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
              <span>{item}</span>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-4 bg-slate-800/40 border border-slate-700/80 rounded-xl text-slate-400 text-xs">
          Standard general safety rules apply. Review lab safety protocols before starting.
        </div>
      )}
    </div>
  );
}
