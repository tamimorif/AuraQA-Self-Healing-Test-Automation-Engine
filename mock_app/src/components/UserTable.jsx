import React from 'react';

const users = [
  { id: 1, name: 'Sarah Chen', email: 'sarah.chen@auraq.io', role: 'Lead Engineer', status: 'active', tests: 1247, lastActive: '2 min ago' },
  { id: 2, name: 'Marcus Johnson', email: 'marcus.j@auraq.io', role: 'QA Manager', status: 'active', tests: 892, lastActive: '15 min ago' },
  { id: 3, name: 'Priya Patel', email: 'priya.p@auraq.io', role: 'SDET', status: 'active', tests: 2103, lastActive: '1 hr ago' },
  { id: 4, name: 'Alex Rivera', email: 'alex.r@auraq.io', role: 'DevOps Lead', status: 'warning', tests: 456, lastActive: '3 hrs ago' },
  { id: 5, name: 'Emily Watson', email: 'emily.w@auraq.io', role: 'Test Architect', status: 'active', tests: 1834, lastActive: '30 min ago' },
  { id: 6, name: 'James Kim', email: 'james.k@auraq.io', role: 'Automation Dev', status: 'error', tests: 321, lastActive: '1 day ago' },
  { id: 7, name: 'Olivia Brooks', email: 'olivia.b@auraq.io', role: 'QA Analyst', status: 'active', tests: 678, lastActive: '45 min ago' },
];

function StatusBadge({ status }) {
  const classes = {
    active: 'status-active',
    warning: 'status-warning',
    error: 'status-error',
  };
  const labels = {
    active: 'Active',
    warning: 'Idle',
    error: 'Offline',
  };
  const dots = {
    active: 'bg-emerald-400',
    warning: 'bg-amber-400',
    error: 'bg-red-400',
  };

  return (
    <span className={classes[status]}>
      <span className={`w-1.5 h-1.5 rounded-full ${dots[status]}`} />
      {labels[status]}
    </span>
  );
}

export default function UserTable() {
  return (
    <div className="glass-card overflow-hidden animate-slide-up" style={{ animationDelay: '0.3s', animationFillMode: 'backwards' }}>
      {/* Header */}
      <div className="px-6 py-5 border-b border-white/[0.06] flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-white">Team Members</h3>
          <p className="text-sm text-white/40 mt-0.5">{users.length} active contributors</p>
        </div>
        <button className="px-4 py-2 rounded-lg bg-aura-500/10 text-aura-400 text-sm font-medium border border-aura-500/20 hover:bg-aura-500/20 transition-all duration-200">
          + Invite
        </button>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table id="user-table" className="w-full">
          <thead>
            <tr className="border-b border-white/[0.06]">
              <th className="text-left px-6 py-3 text-xs font-semibold text-white/40 uppercase tracking-wider">User</th>
              <th className="text-left px-6 py-3 text-xs font-semibold text-white/40 uppercase tracking-wider">Role</th>
              <th className="text-left px-6 py-3 text-xs font-semibold text-white/40 uppercase tracking-wider">Status</th>
              <th className="text-left px-6 py-3 text-xs font-semibold text-white/40 uppercase tracking-wider">Tests Run</th>
              <th className="text-left px-6 py-3 text-xs font-semibold text-white/40 uppercase tracking-wider">Last Active</th>
              <th className="text-right px-6 py-3 text-xs font-semibold text-white/40 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.04]">
            {users.map((user) => (
              <tr
                key={user.id}
                className="table-row group hover:bg-white/[0.02] transition-colors duration-150"
                data-testid="user-row"
              >
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-full bg-gradient-to-br from-aura-400/60 to-blue-500/60 flex items-center justify-center text-xs font-bold text-white shrink-0">
                      {user.name.split(' ').map((n) => n[0]).join('')}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-white/90">{user.name}</p>
                      <p className="text-xs text-white/40">{user.email}</p>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span className="text-sm text-white/60">{user.role}</span>
                </td>
                <td className="px-6 py-4">
                  <StatusBadge status={user.status} />
                </td>
                <td className="px-6 py-4">
                  <span className="text-sm text-white/60 font-mono">{user.tests.toLocaleString()}</span>
                </td>
                <td className="px-6 py-4">
                  <span className="text-sm text-white/40">{user.lastActive}</span>
                </td>
                <td className="px-6 py-4 text-right">
                  <button className="opacity-0 group-hover:opacity-100 p-1.5 rounded-lg text-white/40 hover:text-white/70 hover:bg-white/[0.06] transition-all duration-200">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M6.75 12a.75.75 0 11-1.5 0 .75.75 0 011.5 0zM12.75 12a.75.75 0 11-1.5 0 .75.75 0 011.5 0zM18.75 12a.75.75 0 11-1.5 0 .75.75 0 011.5 0z" />
                    </svg>
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Footer */}
      <div className="px-6 py-4 border-t border-white/[0.06] flex items-center justify-between">
        <span className="text-sm text-white/30">Showing 1-{users.length} of {users.length}</span>
        <div className="flex items-center gap-2">
          <button className="px-3 py-1.5 rounded-lg text-sm text-white/30 bg-white/[0.03] border border-white/[0.06] cursor-not-allowed">
            Previous
          </button>
          <button className="px-3 py-1.5 rounded-lg text-sm text-white/30 bg-white/[0.03] border border-white/[0.06] cursor-not-allowed">
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
