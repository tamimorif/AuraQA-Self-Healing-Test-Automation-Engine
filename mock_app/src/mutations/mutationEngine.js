
/**
 * AuraQA DOM Mutation Engine
 * ──────────────────────────
 * Programmatically applies drift scenarios to the live DOM.
 * Keeps a revert journal so all mutations can be cleanly undone.
 */

const revertJournal = [];

/* ─── Helpers ─── */

function flashElement(el) {
  el.classList.add('mutation-flash');
  el.addEventListener('animationend', () => el.classList.remove('mutation-flash'), { once: true });
}

function log(scenarioName, action, detail) {
  const timestamp = new Date().toISOString();
  console.log(
    `%c[AuraQA Mutation] %c${scenarioName} %c→ ${action}: ${detail}`,
    'color: #a78bfa; font-weight: bold;',
    'color: #facc15; font-weight: bold;',
    'color: #94a3b8;'
  );
  console.log(`  ⏱ ${timestamp}`);
}

/* ─── Mutation Handlers ─── */

function handleRenameId(mutation, scenarioName) {
  const el = document.getElementById(mutation.oldId);
  if (!el) {
    console.warn(`[AuraQA] Element #${mutation.oldId} not found — may already be mutated`);
    return;
  }

  const oldId = el.id;
  el.id = mutation.newId;
  flashElement(el);
  log(scenarioName, 'ID Rename', `#${oldId} → #${mutation.newId}`);

  revertJournal.push(() => {
    const target = document.getElementById(mutation.newId);
    if (target) target.id = oldId;
  });
}

function handleRenameClass(mutation, scenarioName) {
  const elements = document.querySelectorAll(mutation.selector);
  if (elements.length === 0) {
    console.warn(`[AuraQA] No elements found for ${mutation.selector}`);
    return;
  }

  elements.forEach((el) => {
    el.classList.remove(mutation.oldClass);
    el.classList.add(mutation.newClass);
    flashElement(el);
  });

  log(scenarioName, 'Class Swap', `.${mutation.oldClass} → .${mutation.newClass} (${elements.length} elements)`);

  revertJournal.push(() => {
    document.querySelectorAll(`.${mutation.newClass}`).forEach((el) => {
      el.classList.remove(mutation.newClass);
      el.classList.add(mutation.oldClass);
    });
  });
}

function handleWrapElement(mutation, scenarioName) {
  const el = document.querySelector(mutation.selector);
  if (!el) {
    console.warn(`[AuraQA] Element ${mutation.selector} not found`);
    return;
  }

  const parent = el.parentNode;
  const depth = mutation.depth || 1;

  // Build wrapper chain
  let outerWrapper = null;
  let innerWrapper = null;

  for (let i = 0; i < depth; i++) {
    const wrapper = document.createElement(mutation.wrapperTag || 'div');
    if (mutation.wrapperClasses) {
      wrapper.classList.add(...mutation.wrapperClasses);
    }
    wrapper.setAttribute('data-mutation-wrapper', 'true');

    if (!outerWrapper) {
      outerWrapper = wrapper;
      innerWrapper = wrapper;
    } else {
      innerWrapper.appendChild(wrapper);
      innerWrapper = wrapper;
    }
  }

  parent.insertBefore(outerWrapper, el);
  innerWrapper.appendChild(el);
  flashElement(outerWrapper);

  log(scenarioName, 'Nesting Depth', `Wrapped ${mutation.selector} in ${depth} div(s)`);

  revertJournal.push(() => {
    // Unwrap: move element back out and remove wrappers
    const wrappers = document.querySelectorAll('[data-mutation-wrapper]');
    if (wrappers.length > 0) {
      const topWrapper = wrappers[0];
      const wrappedEl = topWrapper.querySelector(mutation.selector) ||
                         innerWrapper.firstElementChild;
      if (wrappedEl && topWrapper.parentNode) {
        topWrapper.parentNode.insertBefore(wrappedEl, topWrapper);
        topWrapper.remove();
      }
    }
  });
}

function handleRemoveAttribute(mutation, scenarioName) {
  const elements = document.querySelectorAll(mutation.selector);
  if (elements.length === 0) {
    console.warn(`[AuraQA] No elements found for ${mutation.selector}`);
    return;
  }

  const savedAttrs = [];
  elements.forEach((el) => {
    const value = el.getAttribute(mutation.attribute);
    savedAttrs.push({ el, value });
    el.removeAttribute(mutation.attribute);
    flashElement(el);
  });

  log(scenarioName, 'Attribute Removal', `Removed ${mutation.attribute} from ${elements.length} element(s)`);

  revertJournal.push(() => {
    savedAttrs.forEach(({ el, value }) => {
      if (value !== null) {
        el.setAttribute(mutation.attribute, value);
      }
    });
  });
}

function handleChangeTag(mutation, scenarioName) {
  const el = document.querySelector(mutation.selector);
  if (!el) {
    console.warn(`[AuraQA] Element ${mutation.selector} not found`);
    return;
  }

  const oldTag = el.tagName.toLowerCase();
  const newEl = document.createElement(mutation.newTag);

  // Copy attributes
  Array.from(el.attributes).forEach((attr) => {
    newEl.setAttribute(attr.name, attr.value);
  });

  // Copy innerHTML
  newEl.innerHTML = el.innerHTML;

  // Add any extra attributes
  if (mutation.addAttributes) {
    Object.entries(mutation.addAttributes).forEach(([key, value]) => {
      newEl.setAttribute(key, value);
    });
  }

  // Copy classes
  newEl.className = el.className;

  el.parentNode.replaceChild(newEl, el);
  flashElement(newEl);

  log(scenarioName, 'Tag Change', `<${oldTag}> → <${mutation.newTag}>`);

  revertJournal.push(() => {
    const current = document.querySelector(mutation.selector);
    if (!current) return;
    const reverted = document.createElement(oldTag);
    Array.from(current.attributes).forEach((attr) => {
      if (mutation.addAttributes && attr.name in mutation.addAttributes) return;
      reverted.setAttribute(attr.name, attr.value);
    });
    reverted.innerHTML = current.innerHTML;
    reverted.className = current.className;
    current.parentNode.replaceChild(reverted, current);
  });
}

function handleChangeText(mutation, scenarioName) {
  const el = document.querySelector(mutation.selector);
  if (!el) {
    console.warn(`[AuraQA] Element ${mutation.selector} not found`);
    return;
  }

  // Find text nodes containing the old text
  const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, null, false);
  const textNodes = [];
  let node;
  while ((node = walker.nextNode())) {
    if (node.textContent.includes(mutation.oldText)) {
      textNodes.push(node);
    }
  }

  if (textNodes.length === 0) {
    // Fallback: direct textContent check
    if (el.textContent.includes(mutation.oldText)) {
      const oldContent = el.textContent;
      el.textContent = el.textContent.replace(mutation.oldText, mutation.newText);
      flashElement(el);
      log(scenarioName, 'Text Change', `"${mutation.oldText}" → "${mutation.newText}"`);
      revertJournal.push(() => {
        const target = document.querySelector(mutation.selector);
        if (target) target.textContent = oldContent;
      });
    }
    return;
  }

  const savedTexts = textNodes.map((tn) => ({ node: tn, original: tn.textContent }));

  textNodes.forEach((tn) => {
    tn.textContent = tn.textContent.replace(mutation.oldText, mutation.newText);
  });

  flashElement(el);
  log(scenarioName, 'Text Change', `"${mutation.oldText}" → "${mutation.newText}"`);

  revertJournal.push(() => {
    savedTexts.forEach(({ node: savedNode, original }) => {
      try {
        savedNode.textContent = original;
      } catch {
        // Node may have been replaced
      }
    });
  });
}

function handleReverseSiblings(mutation, scenarioName) {
  const parent = document.querySelector(mutation.parentSelector);
  if (!parent) {
    console.warn(`[AuraQA] Parent ${mutation.parentSelector} not found`);
    return;
  }

  const children = Array.from(parent.children);
  const originalOrder = children.map((c) => c);

  // Reverse order
  children.reverse().forEach((child) => parent.appendChild(child));
  flashElement(parent);

  log(scenarioName, 'Sibling Reorder', `Reversed ${children.length} children of ${mutation.parentSelector}`);

  revertJournal.push(() => {
    const currentParent = document.querySelector(mutation.parentSelector);
    if (!currentParent) return;
    originalOrder.forEach((child) => currentParent.appendChild(child));
  });
}

/* ─── Public API ─── */

/**
 * Apply a single drift scenario to the live DOM.
 * @param {object} scenario - A scenario object from scenarios.js
 */
export function applyScenario(scenario) {
  console.group(`%c🧬 AuraQA Drift Scenario #${scenario.id}: ${scenario.name}`, 'color: #a78bfa; font-size: 14px; font-weight: bold;');
  console.log(`%cDescription: ${scenario.description}`, 'color: #94a3b8;');
  console.log(`%cSeverity: ${scenario.severity} | Category: ${scenario.category}`, 'color: #94a3b8;');

  scenario.mutations.forEach((mutation) => {
    switch (mutation.type) {
      case 'renameId':
        handleRenameId(mutation, scenario.name);
        break;
      case 'renameClass':
        handleRenameClass(mutation, scenario.name);
        break;
      case 'wrapElement':
        handleWrapElement(mutation, scenario.name);
        break;
      case 'removeAttribute':
        handleRemoveAttribute(mutation, scenario.name);
        break;
      case 'changeTag':
        handleChangeTag(mutation, scenario.name);
        break;
      case 'changeText':
        handleChangeText(mutation, scenario.name);
        break;
      case 'reverseSiblings':
        handleReverseSiblings(mutation, scenario.name);
        break;
      default:
        console.warn(`[AuraQA] Unknown mutation type: ${mutation.type}`);
    }
  });

  console.groupEnd();
}

/**
 * Revert all applied mutations in reverse order.
 */
export function revertAll() {
  console.group('%c🔄 AuraQA — Reverting all mutations', 'color: #facc15; font-size: 14px; font-weight: bold;');
  console.log(`%cReverting ${revertJournal.length} mutation(s)...`, 'color: #94a3b8;');

  while (revertJournal.length > 0) {
    const revert = revertJournal.pop();
    try {
      revert();
    } catch (err) {
      console.warn('[AuraQA] Revert error:', err);
    }
  }

  console.log('%c✅ All mutations reverted', 'color: #34d399;');
  console.groupEnd();

  // Force a page-wide flash to indicate reset
  document.body.classList.add('mutation-flash');
  document.body.addEventListener('animationend', () => document.body.classList.remove('mutation-flash'), { once: true });
}

/**
 * Get mutation engine status.
 */
export function getStatus() {
  return {
    pendingReverts: revertJournal.length,
    hasMutations: revertJournal.length > 0,
  };
}
