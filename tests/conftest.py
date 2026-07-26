"""Shared test fixtures for PathReview."""

import pytest

from core.logging import configure_logging


@pytest.fixture(autouse=True)
def configure_test_logging() -> None:
    """Configure structlog to route through stdlib logging for every test.

    Without this, structlog uses its own default renderer and prints directly
    to stdout, bypassing Python's standard logging module entirely. Pytest's
    caplog fixture only captures records that pass through stdlib logging
    handlers, so without this fixture, caplog-based assertions never see
    structlog output even though the log event is genuinely emitted.
    """
    configure_logging()


@pytest.fixture
def sample_resume_text() -> str:
    """Return a sample resume text for testing."""
    return """
    Jane Doe
    Software Engineer
    jane.doe@example.com | github.com/janedoe
    Experience:
    - Software Engineer at TechCorp (2022-2024)
      Built REST APIs using Python and FastAPI.
    Education:
    - B.S. Computer Science, State University (2022)
    Skills: Python, JavaScript, React, PostgreSQL, Docker
    """


@pytest.fixture
def sample_readme_text() -> str:
    """Return a sample README text for testing."""
    return """
    # Weather App
    A weather forecasting application built with React and OpenWeatherMap API.
    ## Features
    - Current weather display
    - 5-day forecast
    - Location search
    ## Tech Stack
    - React 18
    - TypeScript
    - Tailwind CSS
    - OpenWeatherMap API
    """
