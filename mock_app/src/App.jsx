import React, { useState, useCallback } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import LoginForm from './components/LoginForm';
import Dashboard from './components/Dashboard';
import Navigation from './components/Navigation';
import MutationPanel from './components/MutationPanel';
import { applyScenario, revertAll } from './mutations/mutationEngine';
import { scenarios } from './mutations/scenarios';

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [appliedMutations, setAppliedMutations] = useState([]);

  const handleLogin = useCallback(() => {
    setIsAuthenticated(true);
  }, []);

  const handleLogout = useCallback(() => {
    setIsAuthenticated(false);
  }, []);

  const handleApplyScenario = useCallback((scenarioId) => {
    const scenario = scenarios.find((s) => s.id === scenarioId);
    if (!scenario) return;
    applyScenario(scenario);
    setAppliedMutations((prev) => {
      if (prev.includes(scenarioId)) return prev;
      return [...prev, scenarioId];
    });
  }, []);

  const handleRevertAll = useCallback(() => {
    revertAll();
    setAppliedMutations([]);
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      {isAuthenticated && (
        <Navigation onLogout={handleLogout} />
      )}

      <main className="flex-1">
        <Routes>
          <Route
            path="/"
            element={
              isAuthenticated ? (
                <Navigate to="/dashboard" replace />
              ) : (
                <LoginForm onLogin={handleLogin} />
              )
            }
          />
          <Route
            path="/dashboard"
            element={
              isAuthenticated ? (
                <Dashboard />
              ) : (
                <Navigate to="/" replace />
              )
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>

      {/* Floating Mutation Control Panel */}
      <MutationPanel
        scenarios={scenarios}
        appliedMutations={appliedMutations}
        onApplyScenario={handleApplyScenario}
        onRevertAll={handleRevertAll}
      />
    </div>
  );
}
