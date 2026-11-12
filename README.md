# Sovereign Audio Intelligence

**Local music analysis, audio processing, and model-assisted production tools**

Sovereign Audio Intelligence is an engineering project focused on practical tools for music production and analysis. It brings together audio measurements, model inference, source separation, and local data management. Ableton Live is one supported area of development, not the sole purpose of the project.

The aim is to build a dependable system that can examine an audio recording, choose a documented processing step, run it, and report what changed. Accuracy, repeatability, and understandable results take priority over performance claims.

## Project status

**Active development — November 2026.** Individual parts of the system have been tested, but the complete automated processing sequence is not yet validated.

| Area | Current position |
| --- | --- |
| Audio analysis | Measured loudness, dynamics, and frequency characteristics; time-based measurements are under review |
| Source separation | Demucs ONNX has produced four stems from a short audio excerpt |
| Music generation | Experimental arrangement and sample-selection tools have produced audio |
| Model evaluation | The original Sovereign Big Brain ONNX model loads and runs in ONNX Runtime |
| Mastering | A separate processing script has produced a mastered test file; automatic approval by Big Brain is not established |
| Data management | DuckDB, Lance, Parquet, and JSON registries record models, files, and processing information |
| Ableton Live | Session inspection and device control are a separate integration area |

The Big Brain model accepts a **64-value input** and returns a **12-value output**. We still need to verify exactly how the correct input is prepared and how the results should be evaluated. The model's output alone is not proof that a master is ready for release.

For the technical findings and remaining work, read the [Music Engine architecture and verification report](docs/SOVEREIGN_MUSIC_ENGINE_ARCHITECTURE_2026-11-12.md).

## How the work is organized

**Audio and production.** Separate generation, stem separation, audio analysis, and mastering operations so that their results can be tested independently.

**Recorded data.** Reuse existing databases, model inventories, and processing records. Do not rebuild a catalog each time a request is made.

**Processing and review.** Record the input, the operation performed, the relevant model and version, the output, and the measurements before and after processing. A process is not considered approved until its evaluation rules have been verified.

**Ableton integration.** Treat Ableton projects, clips, devices, and automation as an application of the engine rather than a dependency for every feature.

## Repository contents

- `Sovereign_Audio_Intelligence_Engine.ipynb` — exploratory notebook.
- `audio_deep_dive_report.parquet` — sample analysis data.
- `sovereign_audio_deep_dive_langgraph.py` — experimental audio-analysis workflow.
- `sovereign_kernel.cpp` — native-code experiment.
- `docs/` — technical documentation and verification notes.
- `.github/workflows/` — repository checks run by GitHub Actions.

The repository contains research code and examples. It is **not** a packaged mastering application. Some scripts require local files or services that are not included in this public repository.

## Getting started

For document review, browse the source files and the [architecture report](docs/SOVEREIGN_MUSIC_ENGINE_ARCHITECTURE_2026-11-12.md).

For local Python experiments, start with a separate environment and review a script's required input files and side effects before running it:

```bash
python -m venv .venv
python -m pip install -r requirements.txt
```

The requirements file covers the published Python experiments; it does not install the entire workstation system or supply model weights, audio files, or native Windows components.

## Maintenance and scheduled checks

GitHub Actions can check repository files on a schedule, create reports, and run tests in a temporary hosted environment. **It is not the local audio workstation** and cannot automatically access the Windows databases, named pipes, licensed audio tools, or private models.

The [operations guide](docs/OPERATIONS_AND_SCHEDULES.md) describes appropriate daily, weekly, and on-demand tasks; security requirements for connecting a machine; and the difference between repository checks and local background services.

The scheduled repository check is deliberately limited to truthful, read-only checks of material that is committed to GitHub. It does not claim to benchmark ONNX inference or run audio mastering.

## Next milestones

1. Identify the Big Brain model's original input preparation and decision rules from existing records.
2. Demonstrate one documented **before → processing → after** evaluation on real audio.
3. Preserve measurements for each section of a track, including time positions.
4. Add tests based on actual outputs, not hard-coded success messages.
5. Offer Ableton Live controls once the underlying processing is dependable.

## Data handling and publication

This repository is public. Do not commit personal file inventories, credentials, API keys, proprietary samples, private music projects, or model weights without a deliberate release decision. Workstation-specific configuration and unpublished Kimi work belong in access-controlled storage.

## Contact

Maintained by **Adam Scar McCoy**. For project inquiries, use the [GitHub profile](https://github.com/adamscarmccoy-boop).

---

*Last reviewed: November 12, 2026. This README describes the current development state; it is not a certification of performance, commercial readiness, or regulatory compliance.*
