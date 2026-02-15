# Communication Protocols

This node documents the logic for Aether's multi-channel communication and content delivery.

## 🎧 Context-Aware Audio
- **Source: PC (Dashboard/TUI)**
    - **Action**: Play audio directly through system speakers using `mpv`.
    - **Hardware Target**: **System Default** (Follows user's GUI selection: Headset, HDMI, etc.).
- **Source: Phone (WhatsApp)**
    - **Action**: Send a voice note (`.mp3`/`.ogg`) via the WhatsApp gateway.

## 📝 Content Delivery Protocol
- **Technical Details**: All file paths, links, long-form code, and specific technical specs must be sent as **Text**.
- **Contextual Summary**: The accompanying **Audio** should provide a brief summary of the technical details without repeating raw data.

## 🧠 Evolving Structure
- Every change to these protocols is mirrored in the Hive Mind to ensure an evolving, synchronized "brain map."
