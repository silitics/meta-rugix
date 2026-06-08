# Builds a FAT image for the boot partition containing the U-Boot boot script.

SUMMARY = "U-Boot boot image for Rugix A/B updates on QEMU ARM64"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = "file://boot.cmd"

inherit nopackages deploy

do_compile[noexec] = "1"
do_install[noexec] = "1"
deltask do_populate_sysroot

do_deploy[depends] += " \
    dosfstools-native:do_populate_sysroot \
    mtools-native:do_populate_sysroot \
    u-boot-tools-native:do_populate_sysroot \
"

do_deploy() {
    FATSOURCEDIR="${WORKDIR}/uboot-boot"
    mkdir -p ${FATSOURCEDIR}/rugix

    # Compile boot command script to boot.scr.
    mkimage -T script -d ${UNPACKDIR}/boot.cmd ${FATSOURCEDIR}/boot.scr

    # Mark partition for Rugix bootstrapping.
    touch ${FATSOURCEDIR}/rugix/bootstrap

    # Create FAT image.
    FATIMG="${WORKDIR}/uboot-boot.vfat"
    BLOCKS=65536

    rm -f ${FATIMG}
    mkdosfs -n "BOOT" -C ${FATIMG} ${BLOCKS}
    mcopy -i ${FATIMG} -s ${FATSOURCEDIR}/* ::/
    chmod 644 ${FATIMG}

    mv ${FATIMG} ${DEPLOYDIR}/
}

do_deploy[cleandirs] += "${WORKDIR}/uboot-boot"

addtask deploy after do_install
