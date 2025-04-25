DESCRIPTION = "Rugix Ctrl"
LICENSE = "CLOSED"

RDEPENDS:${PN} = "util-linux-sfdisk e2fsprogs-e2fsck e2fsprogs-mke2fs"

SRC_URI:append:x86_64 = " https://github.com/silitics/rugix/releases/download/v${RUGIX_VERSION}/x86_64-unknown-linux-musl.tar;downloadfilename=rugix-${RUGIX_VERSION}-x86_64.tar;name=x86_64;subdir=rugix-binaries"
SRC_URI:append:aarch64 = " https://github.com/silitics/rugix/releases/download/v${RUGIX_VERSION}/aarch64-unknown-linux-musl.tar;downloadfilename=rugix-${RUGIX_VERSION}-aarch64.tar;name=aarch64;subdir=rugix-binaries"

S = "${WORKDIR}"

do_install() {
    install -d ${D}${bindir}
    install -m 0755 ${S}/rugix-binaries/rugix-ctrl ${D}${bindir}/rugix-ctrl
}
