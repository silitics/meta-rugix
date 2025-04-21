# Rugix Yocto Layers

This repository provides Yocto layers for integrating Rugix Ctrl into a custom Linux distribution tailored to your embedded device.
Rugix Ctrl enables robust over-the-air (OTA) updates and system state management, streamlining the development and maintenance of embedded Linux systems.

> [!WARNING]
> This repository is a work in progress and is not intended for production use at this time.

## Provided Layers

- `meta-rugix-core`: Core layer for installing Rugix Ctrl and building Rugix-compatible update bundles.
- `meta-rugix-rpi-tryboot`: BSP layer for building images with Rugix support on Raspberry Pi using Tryboot.
