import React from 'react';
import UserTable from './UserTable';

const stats = [
  {
    id: 'metric-card-1',
    label: 'Total Tests',
    value: '12,847',
    change: '+14.2%',
    changeType: 'positive',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15a2.25 2.25 0 012.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25z" />
      </svg>
    ),
  },
  {
    id: 'metric-card-2',
    label: 'Self-Healed',
    value: '1,203',
    change: '+28.7%',
    changeType: 'positive',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
      </svg>
    ),
  },
  {
    id: 'metric-card-3',
    label: 'Pass Rate',
    value: '98.3%',
    change: '+2.1%',
    changeType: 'positive',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 18L9 11.25l4.306 4.307a11.95 11.95 0 015.814-5.519l2.74-1.22m0 0l-5.94-2.28m5.94 2.28l-2.28 5.941" />
      </svg>
    ),
  },
  {
    id: 'metric-card-4',
    label: 'Drift Events',
    value: '47',
    change: '-8.3%',
    changeType: 'negative',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
      </svg>
    ),
  },
];

const recentHeals = [
  { selector: '#checkout-btn', from: 'id', to: 'data-action="checkout"', confidence: 97, time: '3 min ago' },
  { selector: '.product-card', from: 'class', to: 'div[role="article"]', confidence: 94, time: '12 min ago' },
  { selector: '[data-testid="nav"]', from: 'testid', to: '#main-navigation', confidence: 91, time: '28 min ago' },
  { selector: '.submit-btn', from: 'class', to: 'button[type="submit"]', confidence: 89, time: '1 hr ago' },
  { selector: '#search-input', from: 'id', to: 'input[name="search"]', confidence: 96, time: '2 hrs ago' },
];

function MiniChart() {
  // Pure CSS mini chart visualization
  const bars = [40, 65, 45, 80, 55, 70, 90, 60, 75, 85, 50, 95];
  return (
    <div className="flex items-end gap-[3px] h-16">
      {bars.map((height, i) => (
        <div
          key={i}
          className="flex-1 rounded-t-sm bg-gradient-to-t from-aura-600/60 to-aura-400/60 transition-all duration-300 hover:from-aura-500 hover:to-aura-300"
          style={{ height: `${height}%` }}
        />
      ))}
    </div>
  );
}

function ActivityRing({ percent, color }) {
  const radius = 40;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (percent / 100) * circumference;

  return (
    <svg className="w-28 h-28 -rotate-90" viewBox="0 0 100 100">
      <circle cx="50" cy="50" r={radius} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="8" />
      <circle
        cx="50"
        cy="50"
        r={radius}
        fill="none"
        stroke={color}
        strokeWidth="8"
        strokeLinecap="round"
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        className="transition-all duration-1000 ease-out"
      />
    </svg>
  );
}

export default function Dashboard() {
  return (
    <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
      {/* Page Header */}
      <div className="animate-fade-in">
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <p className="text-white/40 text-sm mt-1">Overview of your test automation health</p>
      </div>

      {/* Stats Grid */}
      <div className="dashboard-stats grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {stats.map((stat, index) => (
          <div
            key={stat.id}
            id={stat.id}
            className="glass-card-hover p-6 animate-slide-up"
            style={{ animationDelay: `${index * 0.1}s`, animationFillMode: 'backwards' }}
          >
            <div className="flex items-start justify-between mb-4">
              <div className="p-2.5 rounded-xl bg-aura-500/10 text-aura-400">
                {stat.icon}
              </div>
              <span
                className={`text-xs font-semibold px-2 py-1 rounded-full ${
                  stat.changeType === 'positive'
                    ? 'text-emerald-400 bg-emerald-500/10'
                    : 'text-red-400 bg-red-500/10'
                }`}
              >
                {stat.change}
              </span>
            </div>
            <p className="text-2xl font-bold text-white mb-1">{stat.value}</p>
            <p className="text-sm text-white/40">{stat.label}</p>
          </div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Test Execution Trend */}
        <div className="lg:col-span-2 glass-card p-6 animate-slide-up" style={{ animationDelay: '0.2s', animationFillMode: 'backwards' }}>
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-semibold text-white">Test Execution Trend</h3>
              <p className="text-sm text-white/40 mt-0.5">Last 12 hours</p>
            </div>
            <div className="flex items-center gap-4 text-xs">
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-aura-400" />
                <span className="text-white/50">Passed</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-red-400" />
                <span className="text-white/50">Failed</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-400" />
                <span className="text-white/50">Healed</span>
              </div>
            </div>
          </div>
          <MiniChart />
          {/* X-axis labels */}
          <div className="flex justify-between mt-2 text-xs text-white/20">
            {['00:00', '02:00', '04:00', '06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00'].map((t) => (
              <span key={t}>{t}</span>
            ))}
          </div>
        </div>

        {/* Healing Success Ring */}
        <div className="glass-card p-6 flex flex-col items-center justify-center animate-slide-up" style={{ animationDelay: '0.25s', animationFillMode: 'backwards' }}>
          <h3 className="text-lg font-semibold text-white mb-1">Healing Rate</h3>
          <p className="text-sm text-white/40 mb-6">Self-healing success</p>
          <div className="relative">
            <ActivityRing percent={96.2} color="url(#auraGradient)" />
            <svg className="absolute inset-0" width="0" height="0">
              <defs>
                <linearGradient id="auraGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#a78bfa" />
                  <stop offset="100%" stopColor="#7c3aed" />
                </linearGradient>
              </defs>
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-2xl font-bold text-white">96.2%</span>
              <span className="text-xs text-white/40">Success</span>
            </div>
          </div>
          <div className="mt-6 grid grid-cols-2 gap-4 w-full text-center">
            <div>
              <p className="text-lg font-semibold text-white">1,203</p>
              <p className="text-xs text-white/40">Healed</p>
            </div>
            <div>
              <p className="text-lg font-semibold text-white">47</p>
              <p className="text-xs text-white/40">Failed</p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Self-Heals */}
      <div className="glass-card p-6 animate-slide-up" style={{ animationDelay: '0.3s', animationFillMode: 'backwards' }}>
        <div className="flex items-center justify-between mb-5">
          <div>
            <h3 className="text-lg font-semibold text-white">Recent Self-Heals</h3>
            <p className="text-sm text-white/40 mt-0.5">Automatically resolved selector drifts</p>
          </div>
          <button className="text-sm text-aura-400 hover:text-aura-300 transition-colors">View all →</button>
        </div>
        <div className="space-y-3">
          {recentHeals.map((heal, i) => (
            <div
              key={i}
              className="flex items-center gap-4 p-3 rounded-xl bg-white/[0.02] hover:bg-white/[0.04] transition-colors duration-150"
            >
              {/* Icon */}
              <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 shrink-0">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                </svg>
              </div>
              {/* Details */}
              <div className="flex-1 min-w-0">
                <p className="text-sm text-white/80 font-mono truncate">{heal.selector}</p>
                <p className="text-xs text-white/40">
                  {heal.from} → {heal.to}
                </p>
              </div>
              {/* Confidence */}
              <div className="text-right shrink-0">
                <p className="text-sm font-semibold text-emerald-400">{heal.confidence}%</p>
                <p className="text-xs text-white/30">{heal.time}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* User Table */}
      <UserTable />
    </div>
  );
}
