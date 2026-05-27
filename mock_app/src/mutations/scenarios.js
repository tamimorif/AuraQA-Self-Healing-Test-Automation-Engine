
/**
 * AuraQA Drift Scenarios
 * ──────────────────────
 * Each scenario describes a DOM mutation that simulates real-world UI drift.
 * The mutation engine reads these declaratively and applies them to the live DOM.
 */

export const scenarios = [
  {
    id: 1,
    name: 'ID Rename',
    description: '#login-btn → #signin-button',
    category: 'Attribute',
    severity: 'medium',
    mutations: [
      {
        type: 'renameId',
        oldId: 'login-btn',
        newId: 'signin-button',
      },
    ],
  },
  {
    id: 2,
    name: 'Class Swap',
    description: '.submit-form → .auth-form',
    category: 'Attribute',
    severity: 'medium',
    mutations: [
      {
        type: 'renameClass',
        selector: '.submit-form',
        oldClass: 'submit-form',
        newClass: 'auth-form',
      },
    ],
  },
  {
    id: 3,
    name: 'Nesting Depth Change',
    description: 'Add wrapper divs around #login-btn',
    category: 'Structure',
    severity: 'high',
    mutations: [
      {
        type: 'wrapElement',
        selector: '#login-btn, #signin-button',
        wrapperTag: 'div',
        wrapperClasses: ['mutation-wrapper-outer'],
        depth: 2, // Wrap with 2 nested divs
      },
    ],
  },
  {
    id: 4,
    name: 'Attribute Removal',
    description: 'Strip all data-testid attributes',
    category: 'Attribute',
    severity: 'high',
    mutations: [
      {
        type: 'removeAttribute',
        selector: '[data-testid]',
        attribute: 'data-testid',
      },
    ],
  },
  {
    id: 5,
    name: 'Tag Change',
    description: '<button> → <a> for login button',
    category: 'Structure',
    severity: 'critical',
    mutations: [
      {
        type: 'changeTag',
        selector: '#login-btn, #signin-button',
        newTag: 'a',
        addAttributes: { href: '#', role: 'button' },
      },
    ],
  },
  {
    id: 6,
    name: 'Text Content Change',
    description: '"Login" → "Sign In"',
    category: 'Content',
    severity: 'low',
    mutations: [
      {
        type: 'changeText',
        selector: '#login-btn, #signin-button',
        oldText: 'Login',
        newText: 'Sign In',
      },
    ],
  },
  {
    id: 7,
    name: 'Sibling Reorder',
    description: 'Reverse stat card order in dashboard',
    category: 'Structure',
    severity: 'medium',
    mutations: [
      {
        type: 'reverseSiblings',
        parentSelector: '.dashboard-stats',
      },
    ],
  },
  {
    id: 8,
    name: 'Compound Shift',
    description: 'Multi-element: rename IDs + swap classes + change text',
    category: 'Compound',
    severity: 'critical',
    mutations: [
      {
        type: 'renameId',
        oldId: 'user-table',
        newId: 'team-roster',
      },
      {
        type: 'renameClass',
        selector: '.table-row',
        oldClass: 'table-row',
        newClass: 'roster-entry',
      },
      {
        type: 'renameId',
        oldId: 'main-nav',
        newId: 'top-navigation',
      },
      {
        type: 'renameId',
        oldId: 'metric-card-1',
        newId: 'kpi-tile-1',
      },
    ],
  },
];
