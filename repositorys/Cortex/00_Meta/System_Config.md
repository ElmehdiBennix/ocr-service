# System Configuration & Reproducibility

This node tracks the core settings and environmental requirements for Aether's operational integrity.

## Core Components
- **Transcription**: Local OpenAI Whisper (`base` model) running in `.venv`.
- **TTS**: OpenClaw integrated TTS engine.
- **Communication**: WhatsApp Gateway (International format linked).
- **Workspace**: `__PROJECTS__/Aether` (Personal Forge) & `__PROJECTS__/HiveMind` (External Brain).

## Configuration Strategy
- All system changes (e.g., `mediaMaxMb`, `typingMode`) are documented here before execution.
- Dependency chains for local tools are scripted in `setup.sh` within the Forge.

## Reproducibility Protocol
1.  Maintain Git history in `__PROJECTS__/Aether`.
2.  Use Obsidian `HiveMind` to map non-linear logic and project dependencies.
3.  Mirror critical `openclaw.json` snippets here for reference.
