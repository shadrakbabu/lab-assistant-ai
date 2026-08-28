import React from 'react';
import { FlaskConical, Upload, BookOpen, Activity } from 'lucide-react';
import { SubjectBadge } from './SubjectBadge';

export function Header({ activeManual, onUploadClick, manuals, onSelectManual, isHealthy }) {
  return (
    <header className="sticky top-0 z-40 bg-slate-900/90 backdrop-blur border-b border-slate-800 px-6 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <FlaskConical className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-bold text-lg text-white tracking-tight">Lab AI Assistant</h1>
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                PRO RAG
              </span>
            </div>
            <p className="text-xs text-slate-400">Grounded Educational Lab Companion</p>
          </div>
        </div>

        {/* Manual selector & Controls */}
        <div className="flex items-center gap-4">
          
          {/* Connection Status */}
          <div className="hidden sm:flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700 text-xs text-slate-300">
            <Activity className={`w-3.5 h-3.5 ${isHealthy ? 'text-emerald-400 animate-pulse' : 'text-amber-400'}`} />
            <span>{isHealthy ? 'Backend Connected' : 'Offline Mode'}</span>
          </div>

          {/* Active Manual Dropdown */}
          {manuals && manuals.length > 0 && (
            <div className="flex items-center gap-2 bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200">
              <BookOpen className="w-4 h-4 text-blue-400" />
              <select
                value={activeManual?.id || ''}
                onChange={(e) => {
                  const m = manuals.find(item => item.id === e.target.value);
                  if (m) onSelectManual(m);
                }}
                className="bg-transparent text-slate-200 font-medium focus:outline-none cursor-pointer"
              >
                {manuals.map((m) => (
                  <option key={m.id} value={m.id} className="bg-slate-900 text-slate-200">
                    {m.filename} ({m.num_experiments} Exps)
                  </option>
                ))}
              </select>
              {activeManual && <SubjectBadge subject={activeManual.subject} />}
            </div>
          )}

          {/* Upload Button */}
          <button
            onClick={onUploadClick}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold px-4 py-2 rounded-lg transition shadow-md shadow-blue-600/20 active:scale-95"
          >
            <Upload className="w-4 h-4" />
            <span>Upload Manual</span>
          </button>
        </div>

      </div>
    </header>
  );
}
