# Option B | Podcast Voice and Recording Analyzer

## Project title and selected option
This project implements Option B: Podcast Voice and Recording Analyzer.

## Student information
- Student name: [Insert student name]
- Student number: [Insert student number]

## Short description of the application
This application receives extracted acoustic features from speech windows and organizes them into speaker and session objects. It validates the numerical measurements, excludes or flags windows without usable speech, compares each session to the speaker's usual profile, and produces an interpretable quality and speaking-style report without needing the original audio or transcript.

## Class design and the responsibility of each class
- ValidatedRecord: base class used to demonstrate inheritance and an overridable validation API.
- SpeakerProfile: represents a speaker's usual acoustic profile, including usual pitch, energy, speech rate and pause ratio. It validates the profile before use.
- Observation: represents one speech window and stores pitch, energy, speech rate, pause ratio, background noise, signal quality, and speech presence.
- RecordingSession: composes a speaker and multiple observations, calculates session summaries, compares the session to the speaker profile, and collects validation issues.

## Where composition, encapsulation, inheritance and overriding are demonstrated
- Composition: RecordingSession contains a SpeakerProfile and a list of Observation objects.
- Encapsulation: each class stores and validates its own data privately within the object and exposes structured methods and properties.
- Inheritance: SpeakerProfile and Observation inherit from ValidatedRecord.
- Overriding: SpeakerProfile.validate() and Observation.validate() override the base validation behavior defined in ValidatedRecord.

## Assumptions and classification rules
- The program does not have access to raw audio or transcript text; it only works with extracted measurements.
- A speech-present observation must include usable pitch, energy, speech rate and pause-ratio values.
- Values outside their valid range are flagged and included in the session report rather than crashing the program.
- Windows with no usable speech are excluded from feature summaries or marked as invalid depending on the context.
- The session is classified using the average recorded measurements compared to the speaker's usual profile.
- Classification categories include:
  - consistent speaking style
  - energetic delivery
  - slow or deliberate delivery
  - temporarily varied delivery
  - high background noise
  - insufficient data or poor recording quality
- Overall quality is interpreted from signal-quality and noise indicators.

## Exact installation and running instructions
1. Make sure Python 3 is installed on the machine.
2. Open a terminal in the project folder.
3. Run the example program:
   python3 example_usage.py
4. Run the tests:
   python3 -m pytest -q

## Example output
```text
Available scenarios: ('consistent', 'energetic', 'deliberate', 'noise_affected', 'insufficient_data')

Speaker profile
{'speaker_id': 'SP001', 'usual_pitch': 168.9, 'usual_energy': 0.26, 'usual_speech_rate': 112, 'usual_pause_ratio': 0.22}

First three observations
{'timestamp': 0, 'speech_present': True, 'pitch': 180.0, 'energy': 0.38, 'speech_rate': 118, 'pause_ratio': 0.22, 'background_noise': 0.71, 'signal_quality': 0.46}
{'timestamp': 1, 'speech_present': True, 'pitch': 177.5, 'energy': 0.37, 'speech_rate': 112, 'pause_ratio': 0.26, 'background_noise': 0.76, 'signal_quality': 0.68}
{'timestamp': 2, 'speech_present': True, 'pitch': 173.6, 'energy': 0.48, 'speech_rate': 123, 'pause_ratio': 0.32, 'background_noise': 0.71, 'signal_quality': 0.51}

Report
Speaker report for SP001
Status: Fair
Classification: noise_affected
Total windows: 10
Speech windows: 10
Average pitch: 182.93 Hz vs usual 168.9 Hz
Average energy: 0.438 vs usual 0.26
Average speech rate: 115 vs usual 112
Average pause ratio: 0.236 vs usual 0.22
Average background noise: 0.780
Average signal quality: 0.548
Validation issues:
- Background noise is high for this session
```

## Known limitations
- The solution only analyzes the extracted feature values provided by the generator; it does not reconstruct original speech audio or transcripts.
- The classification is heuristic and based on comparisons between the session and the speaker's usual profile; it is intentionally simplified for the assignment.
- The project is designed around the supplied generator data and is not intended for arbitrary, unseen audio datasets.
