"""
Shared pytest fixtures for AuraQA backend tests.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

import pytest
from fastapi.testclient import TestClient

# Ensure test-friendly environment variables BEFORE importing settings
os.environ.setdefault("AURAQA_APP_ENV", "development")
os.environ.setdefault("AURAQA_LOG_LEVEL", "DEBUG")


from backend.config.settings import get_settings
from backend.main import create_app
from backend.models.schemas import (
    CandidateSelector,
    DOMElement,
    HealedSelectorResponse,
    HealingState,
    HealingStatus,
    OriginalElementAttributes,
    SelectorType,
    TestFailurePayload,
)


# ------------------------------------------------------------------
# HTML fixtures
# ------------------------------------------------------------------

SAMPLE_DOM = """\
<!DOCTYPE html>
<html>
<head><title>Test Page</title></head>
<body>
  <div id="app" class="container">
    <header class="header">
      <h1>Welcome</h1>
    </header>
    <main class="content">
      <form id="login-form" class="form" data-testid="login-form">
        <label for="email">Email</label>
        <input id="email" type="email" class="input email-input" data-testid="email-input" />
        <label for="password">Password</label>
        <input id="password" type="password" class="input password-input" />
        <button id="submit-btn" type="submit" class="btn primary" data-testid="submit-btn">
          Sign In
        </button>
      </form>
      <div class="info-panel">
        <p class="help-text">Forgot your password?</p>
        <a href="/reset" class="link reset-link">Reset it here</a>
      </div>
    </main>
    <footer class="footer">
      <span>© 2026 AuraQA</span>
    </footer>
  </div>
</body>
</html>
"""

SAMPLE_DOM_DRIFTED = """\
<!DOCTYPE html>
<html>
<head><title>Test Page</title></head>
<body>
  <div id="app" class="container">
    <main class="content">
      <form id="login-form-v2" class="form-new" data-testid="login-form">
        <label for="user-email">Email Address</label>
        <input id="user-email" type="email" class="input email-field" data-testid="email-input" />
        <label for="user-pass">Password</label>
        <input id="user-pass" type="password" class="input pass-field" />
        <button id="login-btn" type="submit" class="btn btn-primary" data-testid="login-btn">
          Log In
        </button>
      </form>
    </main>
  </div>
</body>
</html>
"""


# ------------------------------------------------------------------
# Pydantic model fixtures
# ------------------------------------------------------------------

@pytest.fixture
def sample_dom() -> str:
    """Return sample DOM HTML."""
    return SAMPLE_DOM


@pytest.fixture
def drifted_dom() -> str:
    """Return drifted DOM HTML."""
    return SAMPLE_DOM_DRIFTED


@pytest.fixture
def original_attributes() -> OriginalElementAttributes:
    """Original element attributes for the submit button."""
    return OriginalElementAttributes(
        tag="button",
        element_id="submit-btn",
        classes=["btn", "primary"],
        text="Sign In",
        attributes={"type": "submit"},
        data_testid="submit-btn",
        depth=3,
        parent_tag="form",
    )


@pytest.fixture
def original_attributes_dict(original_attributes: OriginalElementAttributes) -> dict[str, Any]:
    return original_attributes.model_dump(mode="json")


@pytest.fixture
def test_failure_payload(sample_dom: str, original_attributes: OriginalElementAttributes) -> TestFailurePayload:
    """A valid TestFailurePayload for the submit button."""
    return TestFailurePayload(
        test_case_id="TC-001",
        test_suite_id="TS-LOGIN",
        broken_selector="#submit-btn",
        selector_type=SelectorType.CSS,
        dom_snapshot=sample_dom,
        original_element_attributes=original_attributes,
        page_url="http://localhost:5173/login",
        error_message="Element not found: #submit-btn",
        environment="staging",
        retry_count=0,
    )


@pytest.fixture
def drifted_failure_payload(
    drifted_dom: str,
    original_attributes: OriginalElementAttributes,
) -> TestFailurePayload:
    """Payload where the DOM has drifted from the original."""
    return TestFailurePayload(
        test_case_id="TC-001",
        test_suite_id="TS-LOGIN",
        broken_selector="#submit-btn",
        selector_type=SelectorType.CSS,
        dom_snapshot=drifted_dom,
        original_element_attributes=original_attributes,
        page_url="http://localhost:5173/login",
        error_message="Element not found: #submit-btn",
        environment="staging",
        retry_count=0,
    )


@pytest.fixture
def sample_dom_element() -> DOMElement:
    """A sample DOMElement representing the submit button."""
    return DOMElement(
        tag="button",
        element_id="submit-btn",
        classes=["btn", "primary"],
        text="Sign In",
        attributes={"type": "submit"},
        data_testid="submit-btn",
        depth=3,
        child_index=4,
        xpath="/html/body/div/main/form/button",
        parent_tag="form",
        child_count=0,
    )


@pytest.fixture
def fastapi_client() -> TestClient:
    """Return a FastAPI test client."""
    app = create_app()
    return TestClient(app)
