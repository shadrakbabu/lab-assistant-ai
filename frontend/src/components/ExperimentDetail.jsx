import React, { useState } from 'react';
import { ListChecks, BookOpen, Wrench, ShieldAlert, HelpCircle } from 'lucide-react';
import { SubjectBadge } from './SubjectBadge';
import { ProcedureViewer } from './ProcedureViewer';
import { TheorySection } from './TheorySection';
import { EquipmentAssistant } from './EquipmentAssistant';
import { SafetyAlerts } from './SafetyAlerts';
import { Troubleshooting } from './Troubleshooting';

export function ExperimentDetail({ experiment }) {
  const [activeTab, setActiveTab] = useState('procedure');

  if (!experiment) return null;

  const tabs = [
    { id: 'procedure', label: 'Procedure', icon: ListChecks, badge: experiment.procedure?.length || 0 },
    { id: 'theory', label: 'Theory', icon: BookOpen },
    { id: 'equipment', label: 'Equipment', icon: Wrench, badge: experiment.equipment?.length || 0 },
    { id: 'safety', label: 'Safety', icon: ShieldAlert, badge: experiment.safety?.length || 0 },
    { id: 'troubleshooting', label: 'Troubleshooting', icon: HelpCircle }
  ];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col h-full">
      
      {/* Title & Metadata Banner */}
      <div className="border-b border-slate-800 pb-5 mb-5">
        <div className="flex items-center gap-3 mb-2">
          <span className="text-xs font-bold px-2.5 py-1 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30">
            Experiment {experiment.experiment_number}
          </span>
          <SubjectBadge subject={experiment.subject} />
        </div>
        <h2 className="text-xl font-bold text-white tracking-tight leading-snug">{experiment.title}</h2>
        <p className="text-xs text-slate-400 mt-1 italic">{experiment.aim}</p>
      </div>

      {/* Tabs Bar */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-3 mb-5 overflow-x-auto">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition border whitespace-nowrap ${
                isActive
                  ? 'bg-blue-600 text-white border-blue-500 shadow-md shadow-blue-600/20'
                  : 'bg-slate-800/60 text-slate-400 border-slate-700/80 hover:bg-slate-800 hover:text-slate-200'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
              {tab.badge !== undefined && (
                <span className={`px-1.5 py-0.2 rounded-full text-[10px] ${isActive ? 'bg-white/20 text-white' : 'bg-slate-700 text-slate-300'}`}>
                  {tab.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Tab Content Area */}
      <div className="flex-1 overflow-y-auto pr-1">
        {activeTab === 'procedure' && <ProcedureViewer procedure={experiment.procedure} safety={experiment.safety} />}
        {activeTab === 'theory' && <TheorySection theory={experiment.theory} aim={experiment.aim} />}
        {activeTab === 'equipment' && <EquipmentAssistant equipment={experiment.equipment} />}
        {activeTab === 'safety' && <SafetyAlerts safety={experiment.safety} />}
        {activeTab === 'troubleshooting' && <Troubleshooting troubleshooting={experiment.troubleshooting} observations={experiment.observations} />}
      </div>

    </div>
  );
}
