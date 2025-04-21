SRC_URI = "git://github.com/silitics/rugix.git;branch=main;protocol=https"

SRCREV="main"

LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/Apache-2.0;md5=89aea4e17d99a7cacdbeed46a0096b10" 

S = "${WORKDIR}/git"

inherit cargo

do_compile[network] = "1"
CARGO_DISABLE_BITBAKE_VENDORING = "1"
CARGO_BUILD_FLAGS:append = " --bin rugix-ctrl --bin rugix-bundler "