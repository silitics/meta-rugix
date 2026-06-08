SRC_URI = "git://github.com/rugix/rugix.git;branch=main;protocol=https"

LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/Apache-2.0;md5=89aea4e17d99a7cacdbeed46a0096b10" 

inherit cargo

do_compile[network] = "1"
CARGO_DISABLE_BITBAKE_VENDORING = "1"
CARGO_BUILD_FLAGS:append = " --bin rugix-ctrl "

# With the following commit: https://github.com/yoctoproject/poky/commit/d4c14304c92d76a2bdb612ffa3ca3477cd06cb6e
# --frozen flag was introduced to supersede --offline flag and guarantee that Cargo.lock file will not be modified during the build.
# In consequence it prevents network access that we need to load source for x509-parser library.
CARGO_BUILD_FLAGS:remove = "--frozen"

# rust-common.bbclass already remaps WORKDIR via RUST_DEBUG_REMAP, and this
# broadens it to TMPDIR (covers staging dirs). Paths from C code in Rust deps
# may still leak since --remap-path-prefix only affects rustc, not cc.
RUSTFLAGS:append = " --remap-path-prefix=${TMPDIR}=/usr/src/debug/${PN}/${PV}"
INSANE_SKIP:${PN}-dbg += "buildpaths"

# Yocto has its own stripping mechanism, so it raises an error if binaries produced by `cargo build` are already stripped.
# To prevent this, override `profile.release.strip` in Cargo.toml to "none".
# References:
# https://doc.rust-lang.org/cargo/reference/profiles.html#strip
# https://doc.rust-lang.org/cargo/reference/config.html#command-line-overrides
CARGO_BUILD_FLAGS:append = " --config 'profile.release.strip="none"'"

# Inject the Rugix version from Git tags into the build environment.
do_compile:prepend() {
    export RUGIX_GIT_VERSION="$(git -C ${S} describe --tags --always 2>/dev/null || echo '${PV}')"
}

# remove unsupported panic mode from Cargo build
cargo_do_compile:prepend:class-target() {
    sed -i '/panic = \"abort\"/d' ${S}/${CARGO_SRC_DIR}/Cargo.toml
}
