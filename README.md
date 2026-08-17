# Rugix Yocto Layers

This repository provides Yocto layers for integrating
[Rugix Ctrl](https://rugix.org/docs/ctrl) and the optional
[Rugix Admin](https://rugix.org/docs/admin) management interface into a custom,
[Yocto-based](https://www.yoctoproject.org) Linux distribution tailored to
your embedded device.
Rugix Ctrl **enables secure and efficient over-the-air (OTA) updates and provides robust state management capabilities** designed to streamline the development and maintenance of embedded Linux devices at scale.
Rugix Ctrl is part of the [Rugix Project](https://rugix.org).

Rugix Ctrl is a state-of-the-art update and state management engine:

- **A/B Updates**: Atomic system updates with automatic rollback on failure.
- **Delta Updates**: [Highly-efficient delta updates](https://rugix.org/blog/efficient-delta-updates) minimizing bandwidth.
- **Signature Verification**: Cryptographic verification _before_ installing anything anywhere.
- **State Management**: Flexible state management inspired by container-based architectures.
- **Application Updates**: Atomic deployment and rollback of [application workloads](https://rugix.org/docs/ctrl/application-updates/).
- **Vendor-Agnostic**: Compatible with [various fleet management solutions](https://rugix.org/docs/ctrl/advanced/fleet-management) (avoids lock-in).
- **Flexible Boot Flows**: Supports [any bootloader and boot process](https://rugix.org/docs/ctrl/advanced/boot-flows).

Rugix Ctrl supports different update strategies (symmetric A/B, asymmetric with recovery, incremental updates) and can be adapted to almost any requirements you may have for robust and secure updates.

For details, check out
[Rugix Ctrl's documentation](https://rugix.org/docs/ctrl) and the
[Yocto integration guide](https://rugix.org/docs/ctrl/integration/build-systems/yocto/).

## Supported Yocto Versions

We only support Yocto LTS releases and maintain a dedicated branch for each (e.g., `wrynose`, `scarthgap`, `kirkstone`). Non-LTS Yocto releases are not officially supported.

This branch targets Yocto Wrynose. The Rugix core layer, QEMU BSP examples, and Raspberry Pi BSP examples are the supported baseline.

This branch carries Rugix Ctrl 1.2.0 and 1.3.0 recipes. BitBake selects the
latest compatible version unless the distribution pins another one.

## Getting Started

We provide [kas](https://github.com/siemens/kas)-based [examples](./examples/) to help you get started quickly.
Each active example has a matching KAS lockfile next to it. Update a lockfile with `kas lock examples/<example>.yaml` when intentionally moving the branch baseline forward.

## Provided Layers

The layer [`meta-rugix-core`](./meta-rugix-core/) provides everything required
for installing Rugix Ctrl, optionally installing Rugix Admin, and building
Rugix-compatible update bundles.
In addition the following board-specific layers (Rugix BSP layers) are provided:

- [`meta-rugix-qemu-arm64-uboot`](./meta-rugix-qemu-arm64-uboot/): supported BSP layer for QEMU ARM64 with U-Boot-based A/B updates.
- [`meta-rugix-qemu-x86_64-grub`](./meta-rugix-qemu-x86_64-grub/): supported BSP layer for QEMU x86_64 with GRUB EFI-based A/B updates.
- [`meta-rugix-rpi-tryboot`](./meta-rugix-rpi-tryboot/): supported BSP layer for Raspberry Pi with [`tryboot`](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#fail-safe-os-updates-tryboot)-based A/B updates (official A/B update mechanism of Raspberry Pi). This requires Raspberry Pi 4 (CM4, Raspberry Pi 400) or newer. The Wrynose example uses upstream `meta-raspberrypi` from its `master` branch.
- [`meta-rugix-rpi-uboot`](./meta-rugix-rpi-uboot/): supported BSP layer for Raspberry Pi with U-Boot-based A/B updates. This is meant as a reference implementation. For actual field deployments, always use the `tryboot` integration. The Wrynose example uses upstream `meta-raspberrypi` from its `master` branch.

The board-specific layers serve as **examples** for how to integrate Rugix Ctrl with specific boards and boot flows.
Depending on your project and requirements, you may need to adapt those layers or write your own.

## Rugix Admin

Add Rugix Admin to an image that already integrates Rugix Ctrl by installing
the `rugix-admin` package:

```bitbake
IMAGE_INSTALL:append = " rugix-admin"
```

The package pulls in `rugix-ctrl-daemon` and a compatible `rugix-ctrl` release.
Both systemd services are enabled automatically. Rugix Admin listens on the
loopback interface by default, and optional privileged operation families
remain disabled until explicitly enabled.

All examples select Rugix Ctrl 1.3 and include Rugix Admin and the privileged
operation daemon.

Configure the daemon recipe from your distribution configuration or
`local.conf` with the following Boolean variables:

```bitbake
RUGIX_CTRL_DAEMON_FACTORY_RESET = "true"
RUGIX_CTRL_DAEMON_SYSTEM_COMMIT = "true"
RUGIX_CTRL_DAEMON_SYSTEM_REBOOT = "true"
RUGIX_CTRL_DAEMON_APP_LIFECYCLE = "true"
```

Enable only the operations required by the device. See the
[privileged operation daemon reference](https://rugix.org/docs/ctrl/reference/privileged-daemon/)
for the authoritative policy documentation. The recipe builds Rugix Admin and
its embedded browser interface from a pinned source revision.

## Rugix BSP Layers

A Rugix BSP layer configures the image build for a specific target, defining how the disk is partitioned, how the system boots, and what additional packages are required. A BSP layer typically provides:

- **WKS file** for the disk/partition layout.
- **Rugix configuration** via `system.toml` (boot flow, slots) and `bootstrapping.toml` (first-boot bootstrapping).
- **Slot mapping** defining which WIC partitions correspond to update slots (`RUGIX_SLOTS`).
- **`packagegroup-rugix-bsp`** with additional required packages (bootstrapping tools, system configuration, etc.).
- **Bootloader recipes** for target-specific boot artifacts (e.g., GRUB EFI image, U-Boot boot script).

Not all of these are required. For instance, a BSP that uses an external bootstrapping mechanism can omit the bootstrapping configuration (`bootstrapping.toml`) and the associated packages.

**How it works.** The BSP layer's `layer.conf` sets standard Yocto variables with machine overrides:

```bitbake
WKS_FILE:my-machine ?= "my-target.wks"
WKS_FILE_DEPENDS:append:my-machine = " efi-boot-image"
RUGIX_SLOTS:my-machine ?= "system:2"
IMAGE_INSTALL:append:my-machine = " packagegroup-rugix-bsp"
```

- **`WKS_FILE`** sets the WKS file for the disk layout. Override in `local.conf` to use a custom layout.
- **`WKS_FILE_DEPENDS`** declares build-time dependencies of the WKS file.
- **`RUGIX_SLOTS`** maps slot names to WIC partition numbers (e.g., `"system:2"` or `"boot:2 system:4"`).

**Creating a BSP layer.** To create a Rugix BSP layer for a new board, start from one of the provided BSP layers and adapt it. See the [Rugix documentation](https://rugix.org/docs/ctrl/advanced/boot-flows) for the available boot flows and configuration options.

## Community Showcase

- [Nexigon](https://github.com/nexigon) is a device management and remote access solution. Its [`meta-nexigon`](https://github.com/nexigon/meta-nexigon) layers come with an official Rugix integration, enabling seamless system updates through the cloud.
- [Sulka](https://codeberg.org/AltidSec/meta-sulka-distro) is a Yocto Linux distribution with a strong focus on security hardening. Sulka comes with an official Rugix integration using Rugix Ctrl for secure, atomic OTA updates.
- [thin-edge.io](https://github.com/thin-edge) is a lightweight edge agent for IoT devices. Its [`meta-tedge`](https://github.com/thin-edge/meta-tedge) layers come with an official Rugix integration, enabling seamless system updates through the cloud.

## Licensing

This project is licensed under either [MIT](https://github.com/rugix/rugix/blob/main/LICENSE-MIT) or [Apache 2.0](https://github.com/rugix/rugix/blob/main/LICENSE-APACHE) at your option.

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in this project by you, as defined in the Apache 2.0 license, shall be dual licensed as above, without any additional terms or conditions.

---

Made with ❤️ for OSS by [Silitics](https://www.silitics.com)
