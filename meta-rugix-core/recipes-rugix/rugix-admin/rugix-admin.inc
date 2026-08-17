SUMMARY = "Browser-based management interface for Rugix devices"
DESCRIPTION = "Rugix Admin provides a browser-based management interface for system updates, application workloads, and component compatibility."
HOMEPAGE = "https://rugix.org/docs/admin/"

LICENSE = "MIT | Apache-2.0"
LIC_FILES_CHKSUM = "\
    file://LICENSE-APACHE;md5=175792518e4ac015ab6696d16c4f607e \
    file://LICENSE-MIT;md5=0fe01b40d66d50621bc223cf437ca5dd \
"

SRC_URI = "\
    git://github.com/rugix/rugix-admin.git;branch=main;protocol=https \
    file://admin.toml \
    file://rugix-admin.service \
"
S = "${WORKDIR}/git"

inherit cargo features_check systemd

REQUIRED_DISTRO_FEATURES = "systemd"

DEPENDS += "nodejs-native sidex-cli-native"

# Scarthgap provides Node.js 20. Use the latest pnpm 10 release, which supports
# Node.js 20 and the version 9 lockfile in the pinned Rugix Admin source.
RUGIX_ADMIN_PNPM_VERSION = "10.34.5"

# Cargo and pnpm use the lockfiles from the pinned source revision. As with the
# existing Rugix Ctrl recipes, dependencies are downloaded while compiling.
do_compile[network] = "1"
CARGO_DISABLE_BITBAKE_VENDORING = "1"
CARGO_BUILD_FLAGS:remove = "--frozen"
CARGO_BUILD_FLAGS:append = " --bin rugix-admin "
CARGO_BUILD_FLAGS:append = " --config 'profile.release.strip="none"'"

RUSTFLAGS:append = " --remap-path-prefix=${TMPDIR}=/usr/src/debug/${PN}/${PV}"
INSANE_SKIP:${PN}-dbg += "buildpaths"

do_compile:prepend() {
    export COREPACK_HOME="${WORKDIR}/corepack"
    export COREPACK_ENABLE_PROJECT_SPEC=0
    install -d "${WORKDIR}/corepack-bin"
    corepack enable --install-directory "${WORKDIR}/corepack-bin" pnpm
    corepack prepare "pnpm@${RUGIX_ADMIN_PNPM_VERSION}" --activate
    export PATH="${WORKDIR}/corepack-bin:${PATH}"
    cd ${S}/frontend
    pnpm install --frozen-lockfile
    pnpm run build
}

# Yocto configures the target's panic runtime; do not override it from the
# upstream release profile.
cargo_do_compile:prepend:class-target() {
    sed -i '/panic = "abort"/d' ${S}/Cargo.toml
}

do_install() {
    install -D -m 0755 \
        ${B}/target/${CARGO_TARGET_SUBDIR}/rugix-admin \
        ${D}${bindir}/rugix-admin
    install -D -m 0644 ${WORKDIR}/admin.toml \
        ${D}${sysconfdir}/rugix/admin.toml
    install -D -m 0644 ${WORKDIR}/rugix-admin.service \
        ${D}${systemd_system_unitdir}/rugix-admin.service
}

SYSTEMD_SERVICE:${PN} = "rugix-admin.service"
SYSTEMD_AUTO_ENABLE:${PN} = "enable"

CONFFILES:${PN} = "${sysconfdir}/rugix/admin.toml"
RDEPENDS:${PN} = "rugix-ctrl-daemon"
