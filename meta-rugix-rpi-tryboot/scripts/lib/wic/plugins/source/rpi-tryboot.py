#
# Copyright: Silitics GmbH
#
# SPDX-License-Identifier: MIT
#

import logging

from wic.misc import exec_cmd
from wic.pluginbase import SourcePlugin


AUTOBOOT_TXT = """
[all]
tryboot_a_b=1
boot_partition=2
[tryboot]
boot_partition=3
""".strip()


logger = logging.getLogger("wic")


class RpiTrybootPlugin(SourcePlugin):
    name = "rpi-tryboot"

    @classmethod
    def do_configure_partition(
        cls,
        part,
        source_params,
        cr,
        cr_workdir,
        oe_builddir,
        bootimg_dir,
        kernel_dir,
        native_sysroot,
    ):
        hdddir = f"{cr_workdir}/boot.{part.lineno}"
        exec_cmd(f"install -d {hdddir}")

        with open(f"{hdddir}/autoboot.txt", "w", encoding="utf-8") as autoboot_txt:
            autoboot_txt.write(AUTOBOOT_TXT)

        exec_cmd(f"install -d {hdddir}/.rugix")
        exec_cmd(f"touch {hdddir}/.rugix/bootstrap")

    @classmethod
    def do_prepare_partition(
        cls,
        part,
        source_params,
        cr,
        cr_workdir,
        oe_builddir,
        bootimg_dir,
        kernel_dir,
        rootfs_dir,
        native_sysroot,
    ):
        hdddir = f"{cr_workdir}/boot.{part.lineno}"

        logger.debug(f"Prepare config partition in {hdddir}")
        part.prepare_rootfs(cr_workdir, oe_builddir, hdddir, native_sysroot, False)

        rootfs = "%s/rootfs_%s.%s.%s" % (
            cr_workdir,
            part.label,
            part.lineno,
            part.fstype,
        )
        exec_cmd(f"mcopy -i {rootfs} -o -s {hdddir}/.rugix ::/.rugix")
