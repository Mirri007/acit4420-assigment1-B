"""Podcast Voice and Recording Analyzer.

This module converts the generated dictionaries into typed objects, validates
values, analyzes a recording session, and produces a human-readable report.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean
from typing import Iterable, List, Tuple


VALID_SCENARIOS = (
    "consistent",
    "energetic",
    "deliberate",
    "noise_affected",
    "insufficient_data",
)


class ValidatedRecord:
    """Base class that demonstrates encapsulation and overridable validation."""

    def validate(self) -> list[str]:
        return []


@dataclass
class SpeakerProfile(ValidatedRecord):
    speaker_id: str
    usual_pitch: float
    usual_energy: float
    usual_speech_rate: int
    usual_pause_ratio: float

    @classmethod
    def from_dict(cls, data: dict) -> "SpeakerProfile":
        required_fields = {
            "speaker_id",
            "usual_pitch",
            "usual_energy",
            "usual_speech_rate",
            "usual_pause_ratio",
        }
        missing = sorted(required_fields - set(data))
        if missing:
            raise ValueError(f"Missing required profile fields: {', '.join(missing)}")

        speaker = cls(
            speaker_id=str(data["speaker_id"]).strip(),
            usual_pitch=float(data["usual_pitch"]),
            usual_energy=float(data["usual_energy"]),
            usual_speech_rate=int(data["usual_speech_rate"]),
            usual_pause_ratio=float(data["usual_pause_ratio"]),
        )
        speaker.validate()
        return speaker

    def validate(self) -> list[str]:
        issues = []
        if not self.speaker_id:
            issues.append("speaker_id must be a non-empty string")
        if not 45 <= self.usual_pitch <= 450:
            issues.append("usual_pitch must be between 45 and 450 Hz")
        if not 0 <= self.usual_energy <= 1:
            issues.append("usual_energy must be between 0 and 1")
        if not 30 <= self.usual_speech_rate <= 260:
            issues.append("usual_speech_rate must be between 30 and 260")
        if not 0 <= self.usual_pause_ratio <= 1:
            issues.append("usual_pause_ratio must be between 0 and 1")
        if issues:
            raise ValueError("; ".join(issues))
        return issues


@dataclass
class Observation(ValidatedRecord):
    timestamp: int
    speech_present: bool
    pitch: float | None
    energy: float | None
    speech_rate: int | None
    pause_ratio: float | None
    background_noise: float
    signal_quality: float

    @classmethod
    def from_dict(cls, data: dict) -> "Observation":
        required_fields = {
            "timestamp",
            "speech_present",
            "pitch",
            "energy",
            "speech_rate",
            "pause_ratio",
            "background_noise",
            "signal_quality",
        }
        missing = sorted(required_fields - set(data))
        if missing:
            raise ValueError(f"Missing required observation fields: {', '.join(missing)}")

        obs = cls(
            timestamp=int(data["timestamp"]),
            speech_present=bool(data["speech_present"]),
            pitch=_coerce_optional_float(data["pitch"]),
            energy=_coerce_optional_float(data["energy"]),
            speech_rate=_coerce_optional_int(data["speech_rate"]),
            pause_ratio=_coerce_optional_float(data["pause_ratio"]),
            background_noise=float(data["background_noise"]),
            signal_quality=float(data["signal_quality"]),
        )
        return obs

    def validate(self) -> list[str]:
        issues = []
        if self.timestamp < 0:
            issues.append("timestamp must be 0 or greater")
        if self.background_noise < 0 or self.background_noise > 1:
            issues.append("background_noise must be between 0 and 1")
        if self.signal_quality < 0 or self.signal_quality > 1:
            issues.append("signal_quality must be between 0 and 1")

        if self.speech_present:
            if self.pitch is None or self.energy is None or self.speech_rate is None or self.pause_ratio is None:
                issues.append(f"Speech-present observation at timestamp {self.timestamp} is missing speech features")
            else:
                if not 45 <= self.pitch <= 450:
                    issues.append(f"pitch for timestamp {self.timestamp} must be 45..450 Hz")
                if not 0 <= self.energy <= 1:
                    issues.append(f"energy for timestamp {self.timestamp} must be between 0 and 1")
                if not 30 <= self.speech_rate <= 260:
                    issues.append(f"speech_rate for timestamp {self.timestamp} must be between 30 and 260")
                if not 0 <= self.pause_ratio <= 1:
                    issues.append(f"pause_ratio for timestamp {self.timestamp} must be between 0 and 1")
        return issues


@dataclass
class RecordingSession:
    speaker: SpeakerProfile
    observations: List[Observation]
    _validation_issues: List[str] = field(default_factory=list, init=False)

    @property
    def validation_issues(self) -> List[str]:
        return self._validation_issues

    @validation_issues.setter
    def validation_issues(self, value: List[str]) -> None:
        self._validation_issues = list(value)

    @classmethod
    def from_data(cls, speaker: SpeakerProfile, observations: Iterable[dict]) -> "RecordingSession":
        parsed = [Observation.from_dict(item) for item in observations]
        session = cls(speaker=speaker, observations=parsed)
        session.validate_and_collect_issues()
        return session

    @property
    def total_windows(self) -> int:
        return len(self.observations)

    @property
    def speech_windows(self) -> int:
        return sum(1 for obs in self.observations if obs.speech_present)

    @property
    def avg_background_noise(self) -> float:
        values = [obs.background_noise for obs in self.observations]
        return round(mean(values), 3) if values else 0.0

    @property
    def avg_signal_quality(self) -> float:
        values = [obs.signal_quality for obs in self.observations]
        return round(mean(values), 3) if values else 0.0

    @property
    def quality_rating(self) -> str:
        score = self.avg_signal_quality
        if score >= 0.8:
            return "Excellent"
        if score >= 0.6:
            return "Good"
        if score >= 0.4:
            return "Fair"
        return "Poor"

    @property
    def average_pitch(self) -> float:
        pitches = [obs.pitch for obs in self.observations if obs.speech_present and obs.pitch is not None]
        return round(mean(pitches), 2) if pitches else 0.0

    @property
    def average_energy(self) -> float:
        energies = [obs.energy for obs in self.observations if obs.speech_present and obs.energy is not None]
        return round(mean(energies), 3) if energies else 0.0

    @property
    def average_speech_rate(self) -> float:
        rates = [obs.speech_rate for obs in self.observations if obs.speech_present and obs.speech_rate is not None]
        return round(mean(rates), 2) if rates else 0.0

    @property
    def average_pause_ratio(self) -> float:
        pauses = [obs.pause_ratio for obs in self.observations if obs.speech_present and obs.pause_ratio is not None]
        return round(mean(pauses), 3) if pauses else 0.0

    @property
    def session_label(self) -> str:
        if self.speech_windows == 0 or self.avg_signal_quality < 0.2:
            return "insufficient_data"
        if self.avg_background_noise > 0.6:
            return "noise_affected"
        if self.avg_signal_quality < 0.5:
            return "insufficient_data"

        pitch_delta = abs(self.average_pitch - self.speaker.usual_pitch) / max(self.speaker.usual_pitch, 1)
        energy_delta = abs(self.average_energy - self.speaker.usual_energy)
        rate_delta = abs(self.average_speech_rate - self.speaker.usual_speech_rate)
        pause_delta = abs(self.average_pause_ratio - self.speaker.usual_pause_ratio)

        if rate_delta > 25 and pause_delta > 0.12:
            return "deliberate"
        if rate_delta > 18 and energy_delta > 0.12:
            return "energetic"
        if pitch_delta < 0.08 and rate_delta < 10 and pause_delta < 0.06:
            return "consistent"
        if rate_delta > 12 or pause_delta > 0.09:
            return "temporarily_varied"
        return "consistent"

    def compare_with_profile(self) -> dict:
        return {
            "pitch_difference": round(self.average_pitch - self.speaker.usual_pitch, 2),
            "energy_difference": round(self.average_energy - self.speaker.usual_energy, 3),
            "speech_rate_difference": round(self.average_speech_rate - self.speaker.usual_speech_rate, 2),
            "pause_ratio_difference": round(self.average_pause_ratio - self.speaker.usual_pause_ratio, 3),
            "classification": self.session_label,
        }

    def validate_and_collect_issues(self) -> None:
        self.validation_issues = []
        for obs in self.observations:
            self.validation_issues.extend(obs.validate())

        if self.speech_windows == 0:
            self.validation_issues.append("No speech was detected in any observation window")

        if self.avg_background_noise > 0.5:
            self.validation_issues.append("Background noise is high for this session")

        if self.avg_signal_quality < 0.5:
            self.validation_issues.append("Signal quality is low for this session")

    def describe(self) -> str:
        comparison = self.compare_with_profile()
        lines = [
            f"Speaker report for {self.speaker.speaker_id}",
            f"Status: {self.quality_rating}",
            f"Classification: {self.session_label}",
            f"Total windows: {self.total_windows}",
            f"Speech windows: {self.speech_windows}",
            f"Average pitch: {self.average_pitch} Hz vs usual {self.speaker.usual_pitch} Hz",
            f"Average energy: {self.average_energy} vs usual {self.speaker.usual_energy}",
            f"Average speech rate: {self.average_speech_rate} vs usual {self.speaker.usual_speech_rate}",
            f"Average pause ratio: {self.average_pause_ratio} vs usual {self.speaker.usual_pause_ratio}",
            f"Average background noise: {self.avg_background_noise:.3f}",
            f"Average signal quality: {self.avg_signal_quality:.3f}",
        ]
        if comparison:
            lines.append("Profile comparison:")
            lines.append(f"- pitch difference: {comparison['pitch_difference']}")
            lines.append(f"- energy difference: {comparison['energy_difference']}")
            lines.append(f"- speech rate difference: {comparison['speech_rate_difference']}")
            lines.append(f"- pause ratio difference: {comparison['pause_ratio_difference']}")
        if self.validation_issues:
            lines.append("Validation issues:")
            lines.extend(f"- {issue}" for issue in self.validation_issues)
        else:
            lines.append("Validation issues: none")
        return "\n".join(lines)


def _coerce_optional_float(value):
    if value is None:
        return None
    return float(value)


def _coerce_optional_int(value):
    if value is None:
        return None
    return int(value)


def analyze_recording_session(profile: dict, observations: Iterable[dict]) -> str:
    """Convert raw dictionaries to typed objects, validate them, and return a report."""
    speaker = SpeakerProfile.from_dict(profile)
    session = RecordingSession.from_data(speaker, observations)
    return session.describe()


__all__ = [
    "SpeakerProfile",
    "Observation",
    "RecordingSession",
    "analyze_recording_session",
]
