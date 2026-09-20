import pytest

from podcast_analyzer import SpeakerProfile, RecordingSession, analyze_recording_session
from data_generator import generate_recording_data


def test_profile_validation_and_session_summary():
    profile, observations = generate_recording_data(
        speaker_id="SP001",
        scenario="energetic",
        seed=42,
        number_of_windows=12,
    )

    speaker = SpeakerProfile.from_dict(profile)
    session = RecordingSession.from_data(speaker, observations)

    assert speaker.speaker_id == "SP001"
    assert session.total_windows == 12
    assert session.speech_windows > 0
    assert session.avg_background_noise >= 0
    assert session.avg_signal_quality >= 0
    assert session.session_label in {
        "consistent",
        "energetic",
        "deliberate",
        "temporarily_varied",
        "noise_affected",
        "insufficient_data",
    }


def test_invalid_pause_ratio_is_detected():
    profile, observations = generate_recording_data(
        speaker_id="SP002",
        scenario="insufficient_data",
        seed=7,
        number_of_windows=12,
    )

    speaker = SpeakerProfile.from_dict(profile)
    session = RecordingSession.from_data(speaker, observations)

    assert any("pause_ratio" in issue.lower() for issue in session.validation_issues)
    assert session.session_label == "insufficient_data"


def test_analyze_recording_session_returns_report_text():
    profile, observations = generate_recording_data(
        speaker_id="SP003",
        scenario="noise_affected",
        seed=99,
        number_of_windows=12,
    )

    report = analyze_recording_session(profile, observations)

    assert "Speaker report" in report
    assert "Status:" in report
    assert "signal quality" in report.lower()
    assert "Classification:" in report
