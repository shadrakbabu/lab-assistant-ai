import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { ManualUploader } from './components/ManualUploader';
import { ExperimentCard } from './components/ExperimentCard';
import { ExperimentDetail } from './components/ExperimentDetail';
import { ChatAssistant } from './components/ChatAssistant';
import { api } from './services/api';
import { Search, SlidersHorizontal, BookOpen, Sparkles, MessageSquare, Layers } from 'lucide-react';

export default function App() {
  const [manuals, setManuals] = useState([]);
  const [activeManual, setActiveManual] = useState(null);
  const [experiments, setExperiments] = useState([]);
  const [selectedExperiment, setSelectedExperiment] = useState(null);
  const [subjectFilter, setSubjectFilter] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [isHealthy, setIsHealthy] = useState(false);
  const [showChat, setShowChat] = useState(true);

  // Check health & load manuals on mount
  useEffect(() => {
    const init = async () => {
      try {
        await api.checkHealth();
        setIsHealthy(true);
        const data = await api.getManuals();
        setManuals(data);
        if (data.length > 0) {
          loadManual(data[0]);
        }
      } catch (err) {
        setIsHealthy(false);
      }
    };
    init();
  }, []);

  const loadManual = async (manual) => {
    setActiveManual(manual);
    try {
      const exps = await api.getExperiments(manual.id);
      setExperiments(exps);
      setSelectedExperiment(exps[0] || null);
    } catch (err) {
      console.error('Failed to load experiments', err);
    }
  };

  const handleUploadSuccess = async (file) => {
    const newManual = await api.uploadManual(file);
    const updatedList = await api.getManuals();
    setManuals(updatedList);
    loadManual(newManual);
  };

  const subjects = ['All', 'Physics', 'Chemistry', 'Biology', 'Computer Science', 'General Science'];

  const filteredExperiments = experiments.filter((exp) => {
    const matchesSubject = subjectFilter === 'All' || exp.subject === subjectFilter;
    const matchesQuery = searchQuery === '' || 
      exp.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
      exp.aim.toLowerCase().includes(searchQuery.toLowerCase()) ||
      `exp ${exp.experiment_number}`.includes(searchQuery.toLowerCase());
    return matchesSubject && matchesQuery;
  });

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      
      {/* Header */}
      <Header
        activeManual={activeManual}
        manuals={manuals}
        onSelectManual={loadManual}
        onUploadClick={() => setShowUploadModal(true)}
        isHealthy={isHealthy}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 flex flex-col gap-6">
        
        {/* If no manual uploaded yet -> Hero Banner */}
        {(!manuals || manuals.length === 0) && (
          <div className="bg-gradient-to-r from-blue-900/40 via-indigo-900/30 to-slate-900 border border-blue-800/40 rounded-3xl p-10 text-center max-w-3xl mx-auto my-auto shadow-2xl space-y-6">
            <div className="w-16 h-16 rounded-2xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 mx-auto shadow-lg shadow-blue-500/20">
              <Sparkles className="w-8 h-8" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white tracking-tight">Grounded Laboratory AI Assistant</h2>
              <p className="text-sm text-slate-300 mt-2 max-w-xl mx-auto leading-relaxed">
                Upload your laboratory manual PDF to automatically detect experiments, explore step-by-step procedures, understand theory, inspect safety guidelines, and chat with a grounded RAG AI.
              </p>
            </div>
            <button
              onClick={() => setShowUploadModal(true)}
              className="bg-blue-600 hover:bg-blue-500 text-white font-bold px-6 py-3 rounded-xl transition shadow-lg shadow-blue-600/30 inline-flex items-center gap-2 text-sm"
            >
              <BookOpen className="w-4 h-4" />
              <span>Upload Laboratory Manual PDF</span>
            </button>
          </div>
        )}

        {/* Workspace layout when manuals exist */}
        {activeManual && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1 items-start">
            
            {/* Left Sidebar: Search & Experiment List */}
            <div className="lg:col-span-4 space-y-4">
              
              {/* Manual Info Card */}
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 font-bold text-xs">
                    PDF
                  </div>
                  <div>
                    <h3 className="text-xs font-bold text-slate-100 truncate max-w-[180px]">{activeManual.filename}</h3>
                    <p className="text-[11px] text-slate-400">{activeManual.num_experiments} Experiments Detected</p>
                  </div>
                </div>
                <button
                  onClick={() => setShowChat(!showChat)}
                  className={`p-2 rounded-xl border transition ${showChat ? 'bg-blue-600 text-white border-blue-500' : 'bg-slate-800 text-slate-400 border-slate-700'}`}
                  title="Toggle AI Chat Panel"
                >
                  <MessageSquareText className="w-4 h-4" />
                </button>
              </div>

              {/* Search input */}
              <div className="relative">
                <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search experiments by name or number..."
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
                />
              </div>

              {/* Subject filters */}
              <div className="flex items-center gap-1.5 overflow-x-auto no-scrollbar pb-1">
                {subjects.map((subj) => (
                  <button
                    key={subj}
                    onClick={() => setSubjectFilter(subj)}
                    className={`px-3 py-1 rounded-lg text-[11px] font-semibold transition border whitespace-nowrap ${
                      subjectFilter === subj
                        ? 'bg-blue-600 text-white border-blue-500'
                        : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-slate-200'
                    }`}
                  >
                    {subj}
                  </button>
                ))}
              </div>

              {/* Experiment Cards list */}
              <div className="space-y-3 max-h-[600px] overflow-y-auto pr-1">
                {filteredExperiments.length > 0 ? (
                  filteredExperiments.map((exp) => (
                    <ExperimentCard
                      key={exp.id}
                      experiment={exp}
                      isSelected={selectedExperiment?.id === exp.id}
                      onSelect={() => setSelectedExperiment(exp)}
                    />
                  ))
                ) : (
                  <div className="p-8 text-center text-slate-500 text-xs bg-slate-900/60 rounded-xl border border-slate-800">
                    No experiments found matching filters.
                  </div>
                )}
              </div>

            </div>

            {/* Middle & Right Workspace */}
            <div className={`grid grid-cols-1 ${showChat ? 'lg:col-span-8 lg:grid-cols-2' : 'lg:col-span-8'} gap-6 h-[720px]`}>
              
              {/* Experiment Detail Workspace */}
              <div className="h-full overflow-hidden">
                <ExperimentDetail experiment={selectedExperiment} />
              </div>

              {/* Grounded RAG AI Chat Assistant */}
              {showChat && (
                <div className="h-full overflow-hidden">
                  <ChatAssistant
                    manualId={activeManual.id}
                    activeExperiment={selectedExperiment}
                  />
                </div>
              )}

            </div>

          </div>
        )}

      </main>

      {/* Upload Modal */}
      {showUploadModal && (
        <ManualUploader
          onUploadSuccess={handleUploadSuccess}
          onClose={() => setShowUploadModal(false)}
        />
      )}

    </div>
  );
}
