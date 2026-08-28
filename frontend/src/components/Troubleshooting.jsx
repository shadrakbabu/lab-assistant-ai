import React from 'react';
import { HelpCircle, AlertCircle, CheckCircle2 } from 'lucide-react';

export function Troubleshooting({ troubleshooting = '', observations = '', result = '' }) {
  return (
    <div className="space-y-4 text-xs">
      <div className="p-4 bg-slate-950/60 border border-slate-800 rounded-xl flex items-start gap-3">
        <HelpCircle className="w-5 h-5 text-blue-400 shrink-0 mt-0.5" />
        <div>
          <h4 className="font-bold text-slate-200 text-sm">Experimental Troubleshooting & Analysis</h4>
          <p className="text-slate-400 mt-1 leading-relaxed">
            Troubleshooting guidance grounded in manual guidelines and standard laboratory procedures.
          </p>
        </div>
      </div>

      {troubleshooting ? (
        <div className="p-4 bg-slate-800/40 border border-slate-700/80 rounded-xl space-y-2 text-slate-200">
          <h5 className="font-semibold text-blue-300">Manual Troubleshooting Guidance:</h5>
          <p className="whitespace-pre-line leading-relaxed">{troubleshooting}</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div className="p-4 bg-slate-800/40 border border-slate-700/80 rounded-xl space-y-2">
            <div className="flex items-center gap-2 font-bold text-amber-300">
              <AlertCircle className="w-4 h-4 text-amber-400" />
              <span>Common Error Causes</span>
            </div>
            <ul className="list-disc list-inside space-y-1 text-slate-300">
              <li>Zero error or parallax error in apparatus readings.</li>
              <li>Incorrect chemical proportions or uncalibrated sensors.</li>
              <li>Environmental fluctuations during measurement.</li>
            </ul>
          </div>

          <div className="p-4 bg-slate-800/40 border border-slate-700/80 rounded-xl space-y-2">
            <div className="flex items-center gap-2 font-bold text-emerald-300">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Verification Checklist</span>
            </div>
            <ul className="list-disc list-inside space-y-1 text-slate-300">
              <li>Re-check zero alignment of scale / instrument.</li>
              <li>Repeat trial runs and calculate average reading.</li>
              <li>Compare results with standard expected values.</li>
            </ul>
          </div>
        </div>
      )}

      {observations && (
        <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl">
          <h5 className="font-bold text-slate-300 mb-1">Observation & Calculation Notes:</h5>
          <p className="text-slate-400 leading-relaxed">{observations}</p>
        </div>
      )}
    </div>
  );
}
