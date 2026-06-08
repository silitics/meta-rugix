# Builds a FAT image for the EFI System Partition containing GRUB.

SUMMARY = "EFI boot image for Rugix GRUB A/B updates"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = "file://grub.cfg"

inherit nopackages deploy

do_compile[noexec] = "1"
do_install[noexec] = "1"
deltask do_populate_sysroot

do_deploy[depends] += " \
    dosfstools-native:do_populate_sysroot \
    mtools-native:do_populate_sysroot \
    grub-efi:do_deploy \
    grub-native:do_populate_sysroot \
"

do_deploy() {
    FATSOURCEDIR="${WORKDIR}/efi-boot"
    mkdir -p ${FATSOURCEDIR}/EFI/BOOT
    mkdir -p ${FATSOURCEDIR}/rugix
    mkdir -p ${FATSOURCEDIR}/rugpi

    cp ${DEPLOY_DIR_IMAGE}/grub-efi-bootx64.efi ${FATSOURCEDIR}/EFI/BOOT/bootx64.efi
    cp ${UNPACKDIR}/grub.cfg ${FATSOURCEDIR}/EFI/BOOT/grub.cfg

    touch ${FATSOURCEDIR}/rugix/bootstrap

    # Initialize GRUB environment files with default boot state.
    #
    # Variable names use the `rugpi_` prefix for backward compatibility.
    grub-editenv ${FATSOURCEDIR}/rugpi/primary.grubenv create
    grub-editenv ${FATSOURCEDIR}/rugpi/primary.grubenv set rugpi_bootpart=2
    grub-editenv ${FATSOURCEDIR}/rugpi/boot_spare.grubenv create
    grub-editenv ${FATSOURCEDIR}/rugpi/boot_spare.grubenv set rugpi_boot_spare=false

    FATIMG="${WORKDIR}/efi-boot.vfat"
    BLOCKS=65536

    rm -f ${FATIMG}
    mkdosfs -n "EFI" -C ${FATIMG} ${BLOCKS}
    mcopy -i ${FATIMG} -s ${FATSOURCEDIR}/* ::/
    chmod 644 ${FATIMG}

    mv ${FATIMG} ${DEPLOYDIR}/
}

do_deploy[cleandirs] += "${WORKDIR}/efi-boot"

addtask deploy after do_install
