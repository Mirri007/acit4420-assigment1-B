"""Minimal demonstration of the instructor-supplied recording generator."""

from data_generator import available_scenarios, generate_recording_data
from podcast_analyzer import analyze_recording_session


def main():
    print("Available scenarios:", available_scenarios())

    profile, observations = generate_recording_data(
        speaker_id="SP001",
        scenario="noise_affected",
        seed=42,
        number_of_windows=10,
    )

    print("\nSpeaker profile")
    print(profile)
    print("\nFirst three observations")
    for observation in observations[:3]:
        print(observation)

    print("\nReport")
    print(analyze_recording_session(profile, observations))


if __name__ == "__main__":
    main()
