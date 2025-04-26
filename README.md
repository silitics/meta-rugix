# Rugix Yocto Layers

This repository provides Yocto layers for integrating [Rugix Ctrl](https://rugix.org/docs/ctrl) into a custom, [Yocto-based](https://www.yoctoproject.org) Linux distribution tailored to your embedded device.
Rugix Ctrl **enables secure and efficient over-the-air (OTA) updates and provides robust state management capabilities** designed to streamline the development and maintenance of embedded Linux devices at scale.
Rugix Ctrl is part of the [Rugix Project](https://rugix.org).

> [!WARNING]
> This repository is **work-in-progress and not intended for production use** at this time.
> We appreciate any feedback you may have regarding this Yocto integration.
> Feel free to [open an issue](https://github.com/silitics/meta-rugix/issues/new/choose).

Rugix Ctrl has all features you would expect from a state-of-the-art update solution and more:

- **Atomic A/B system updates** with popular bootloaders out of the box.
- **Streaming updates** as well as **adaptive delta updates** out of the box.
- Builtin **cryptographic integrity checks** _before_ installing anything anywhere.
- Supports **any update scenario**, including **non-A/B updates and incremental updates**.
- Supports **any bootloader and boot process** through [custom _boot flows_](https://rugix.org/docs/ctrl/advanced/boot-flows).
- **Robust state management mechanism** inspired by container-based architectures.
- Integrates well with [different fleet management solutions](https://rugix.org/docs/ctrl/advanced/fleet-management) (avoids vendor lock-in).
- Provides powerful interfaces to built your own update workflow upon.

Rugix Ctrl **supports or can be adapted to almost any requirements you may have** when it comes to robust and secure updates of your entire system as well as its individual components.

For details, check out [Rugix Ctrl's documentation](https://rugix.org/docs/ctrl) and the [documentation on the Yocto layers](https://oss.silitics.com/rugix/docs/ctrl/advanced/yocto-integration/).

## Getting Started

We provide [kas](https://github.com/siemens/kas)-based [examples](./examples/) to help you get started quickly.

## Provided Layers

The layer [`meta-rugix-core`](./meta-rugix-core/) provides everything required for installing Rugix Ctrl and building Rugix-compatible update bundles.
In addition the following board-specific layers are provided:

- [`meta-rugix-rpi-tryboot`](./meta-rugix-rpi-tryboot/): BSP layer for building Raspberry Pi images with [`tryboot`](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#fail-safe-os-updates-tryboot) support. This layer has so far only been tested on Raspberry Pi 5.

The board-specific layers serve as **examples** for how to integrate Rugix Ctrl with specific boards.
Depending on your project and requirements, you may need to adapt those layers or write your own.

## Known Limitations

The `rugix-ctrl` recipe building Rugix Ctrl from source is not working at the moment due to some compilation issue.
For the time being, use the binary variant `rugix-ctrl-bin`, which installs pre-build binaries.

## ⚖️ Licensing

This project is licensed under either [MIT](https://github.com/silitics/rugix/blob/main/LICENSE-MIT) or [Apache 2.0](https://github.com/silitics/rugix/blob/main/LICENSE-APACHE) at your opinion.

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in this project by you, as defined in the Apache 2.0 license, shall be dual licensed as above, without any additional terms or conditions.

---

Made with ❤️ for OSS by [Silitics](https://www.silitics.com)