SUMMARY = "Sidex schema compiler for native builds"
DESCRIPTION = "Builds the Sidex command-line generator used by Rugix Admin's frontend build."
HOMEPAGE = "https://oss.silitics.com/sidex"

LICENSE = "MIT | Apache-2.0"
LIC_FILES_CHKSUM = "\
    file://LICENSE-APACHE;md5=175792518e4ac015ab6696d16c4f607e \
    file://LICENSE-MIT;md5=4b1b4dd7b2889ad5831bbdf51797f0c1 \
"

SRC_URI = "git://github.com/silitics/sidex.git;branch=main;protocol=https"
SRCREV = "53f5e11480ebf471ba37a97fa2a683be1e2bf235"
S = "${WORKDIR}/git"

inherit cargo native

do_compile[network] = "1"
CARGO_DISABLE_BITBAKE_VENDORING = "1"
CARGO_BUILD_FLAGS:remove = "--frozen"
CARGO_BUILD_FLAGS:append = " --package sidex-cli --bin sidex "
CARGO_BUILD_FLAGS:append = " --config 'profile.release.strip="none"'"

do_install() {
    install -D -m 0755 \
        ${B}/target/${CARGO_TARGET_SUBDIR}/sidex \
        ${D}${bindir}/sidex
}
