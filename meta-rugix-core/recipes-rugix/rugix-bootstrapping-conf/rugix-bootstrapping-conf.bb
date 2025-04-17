LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/Apache-2.0;md5=89aea4e17d99a7cacdbeed46a0096b10" 

SRC_URI = "file://bootstrapping.toml"

do_install:append() {
    install -d ${D}${sysconfdir}/rugix
    install -m 0644 ${WORKDIR}/bootstrapping.toml ${D}${sysconfdir}/rugix/
}
