LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/Apache-2.0;md5=89aea4e17d99a7cacdbeed46a0096b10"

SRC_URI = "file://bootstrapping.toml"
S = "${UNPACKDIR}"

RUGIX_SYSTEM_SIZE ?= "4GiB"
RUGIX_BOOT_SIZE ?= "128MiB"

do_install:append() {
    install -d ${D}${sysconfdir}/rugix
    sed -e 's/@@RUGIX_SYSTEM_SIZE@@/${RUGIX_SYSTEM_SIZE}/g' \
        -e 's/@@RUGIX_BOOT_SIZE@@/${RUGIX_BOOT_SIZE}/g' \
        ${UNPACKDIR}/bootstrapping.toml > ${D}${sysconfdir}/rugix/bootstrapping.toml
    chmod 0644 ${D}${sysconfdir}/rugix/bootstrapping.toml
}
