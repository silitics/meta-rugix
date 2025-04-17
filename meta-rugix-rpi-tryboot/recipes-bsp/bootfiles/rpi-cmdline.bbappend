RUGIX_ROOT_PARTITION ?= "/dev/mmcblk0p4"

CMDLINE_ROOT_PARTITION = "${RUGIX_ROOT_PARTITION}"
CMDLINE:append = " console=tty1 init=/usr/bin/rugix-ctrl ro"