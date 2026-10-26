# VTUBE Connect — Android companion plan

Target: native Kotlin Android app. This folder documents the integration contract; it does not yet contain an APK.

Screens: Home/pair, Webcam, Microphone, Face Tracking, Mobile Gaming, Remote Control, Connection Status, Privacy, History.

Transport roadmap:
- USB/local transport where supported
- LAN discovery and pairing using a one-time code
- Encrypted control and media sessions
- Internet Anywhere mode using encrypted direct connectivity or a relay
- Explicit camera/microphone/screen-capture permissions, revocable pairing, no hidden capture

Android screen mirroring must use Android-supported capture permissions/APIs; protected content may not be capturable. Phone audio capture varies by device and Android version.
