import React, { useState } from 'react';

const severityColors = {
  low: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
  medium: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
  high: 'text-orange-400 bg-orange-500/10 border-orange-500/20',
  critical: 'text-red-400 bg-red-500/10 border-red-500/20',
};

const categoryIcons = {
  Attribute: '🏷️',
  Structure: '🏗️',
  Content: '📝',
  Compound: '⚡',
};

export default function MutationPanel({ scenarios, appliedMutations, onApplyScenario, onRevertAll }) {
  const [isOpen, setIsOpen] = useState(false);
  const [lastApplied, setLastApplied] = useState(null);

  const handleApply = (scenarioId) => {
    onApplyScenario(scenarioId);
    setLastApplied(scenarioId);
    setTimeout(() => setLastApplied(null), 2000);
  };

  return (
    <>
      {/* Toggle Button — always visible */}
      <button
        onClick={() => setIsOpen((prev) => !prev)}
        className={`fixed bottom-6 right-6 z-50 w-14 h-14 rounded-2xl flex items-center justify-center shadow-lg transition-all duration-300 ${
          isOpen
            ? 'bg-red-500/80 hover:bg-red-500 shadow-red-500/30 rotate-45'
            : 'bg-gradient-to-br from-aura-500 to-aura-700 hover:from-aura-400 hover:to-aura-600 shadow-aura-500/30 animate-pulse-glow'
        }`}
        title={isOpen ? 'Close Mutation Panel' : 'Open Mutation Panel'}
      >
        {isOpen ? (
          <svg className="w-6 h-6 text-white -rotate-45" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        ) : (
          <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" />
          </svg>
        )}
      </button>

      {/* Applied Mutations Count Badge */}
      {appliedMutations.length > 0 && !isOpen && (
        <div className="fixed bottom-[5.25rem] right-6 z-50 px-2.5 py-1 rounded-full bg-amber-500/90 text-xs font-bold text-black shadow-lg animate-slide-up">
          {appliedMutations.length} active
        </div>
      )}

      {/* Panel */}
      <div
        className={`fixed bottom-24 right-6 z-50 w-[420px] max-h-[70vh] transition-all duration-300 ease-out ${
          isOpen
            ? 'opacity-100 translate-y-0 pointer-events-auto'
            : 'opacity-0 translate-y-4 pointer-events-none'
        }`}
      >
        <div className="glass-card gradient-border overflow-hidden flex flex-col max-h-[70vh]">
          {/* Panel Header */}
          <div className="p-5 border-b border-white/[0.06] shrink-0">
            <div className="flex items-center gap-3 mb-1">
              <div className="p-1.5 rounded-lg bg-aura-500/15 text-aura-400">
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" />
                </svg>
              </div>
              <div>
                <h3 className="text-base font-semibold text-white">Mutation Control Panel</h3>
                <p className="text-xs text-white/40">Simulate DOM drift scenarios</p>
              </div>
            </div>

            {/* Status Bar */}
            <div className="mt-3 flex items-center justify-between">
              <span className="text-xs text-white/40">
                {appliedMutations.length} of {scenarios.length} active
              </span>
              {appliedMutations.length > 0 && (
                <button
                  onClick={onRevertAll}
                  className="px-3 py-1.5 rounded-lg text-xs font-medium bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500/20 transition-all duration-200"
                >
                  ↩ Revert All
                </button>
              )}
            </div>
          </div>

          {/* Scenario List */}
          <div className="overflow-y-auto p-3 space-y-2 flex-1">
            {scenarios.map((scenario) => {
              const isApplied = appliedMutations.includes(scenario.id);
              const justApplied = lastApplied === scenario.id;

              return (
                <div
                  key={scenario.id}
                  className={`p-4 rounded-xl transition-all duration-300 ${
                    isApplied
                      ? 'bg-aura-500/10 border border-aura-500/20'
                      : 'bg-white/[0.02] border border-white/[0.04] hover:bg-white/[0.05] hover:border-white/[0.08]'
                  } ${justApplied ? 'ring-2 ring-amber-400/50' : ''}`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1.5">
                        <span className="text-sm">{categoryIcons[scenario.category] || '🔬'}</span>
                        <span className="text-sm font-semibold text-white">
                          #{scenario.id} {scenario.name}
                        </span>
                        <span
                          className={`inline-flex px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wider border ${
                            severityColors[scenario.severity]
                          }`}
                        >
                          {scenario.severity}
                        </span>
                      </div>
                      <p className="text-xs text-white/40 font-mono">{scenario.description}</p>
                    </div>
                    <button
                      onClick={() => handleApply(scenario.id)}
                      disabled={isApplied}
                      className={`shrink-0 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 ${
                        isApplied
                          ? 'bg-aura-500/20 text-aura-300 cursor-not-allowed opacity-60'
                          : 'bg-aura-500/10 text-aura-400 border border-aura-500/20 hover:bg-aura-500/30 hover:text-aura-300'
                      }`}
                    >
                      {isApplied ? '✓ Applied' : 'Apply'}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Panel Footer */}
          <div className="p-4 border-t border-white/[0.06] shrink-0">
            <p className="text-[11px] text-white/25 text-center">
              Mutations are applied to the live DOM. Open DevTools console to see detailed logs.
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
