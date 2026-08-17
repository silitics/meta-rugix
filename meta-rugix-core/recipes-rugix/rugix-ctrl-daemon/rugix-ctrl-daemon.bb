SUMMARY = "Privileged operation daemon for Rugix Ctrl"
DESCRIPTION = "Installs and configures the privileged Rugix Ctrl daemon used by unprivileged management services."
HOMEPAGE = "https://rugix.org/docs/ctrl/reference/privileged-daemon/"
PV = "1.3.0"

LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/Apache-2.0;md5=89aea4e17d99a7cacdbeed46a0096b10"

SRC_URI = "\
    file://daemon.toml.in \
    file://rugix-ctrl-daemon.service \
"

S = "${UNPACKDIR}"

inherit features_check systemd useradd

REQUIRED_DISTRO_FEATURES = "systemd"

RUGIX_CTRL_DAEMON_DANGEROUSLY_INSECURE ?= "false"
RUGIX_CTRL_DAEMON_FACTORY_RESET ?= "false"
RUGIX_CTRL_DAEMON_SYSTEM_COMMIT ?= "false"
RUGIX_CTRL_DAEMON_SYSTEM_REBOOT ?= "false"
RUGIX_CTRL_DAEMON_APP_LIFECYCLE ?= "false"

python __anonymous() {
    settings = (
        "RUGIX_CTRL_DAEMON_DANGEROUSLY_INSECURE",
        "RUGIX_CTRL_DAEMON_FACTORY_RESET",
        "RUGIX_CTRL_DAEMON_SYSTEM_COMMIT",
        "RUGIX_CTRL_DAEMON_SYSTEM_REBOOT",
        "RUGIX_CTRL_DAEMON_APP_LIFECYCLE",
    )
    for setting in settings:
        value = d.getVar(setting)
        if value not in ("true", "false"):
            bb.fatal(f"{setting} must be either 'true' or 'false', got {value!r}")
}

do_compile[noexec] = "1"

do_install() {
    install -d -m 0755 ${D}${sysconfdir}/rugix
    sed \
        -e 's/@DANGEROUSLY_INSECURE@/${RUGIX_CTRL_DAEMON_DANGEROUSLY_INSECURE}/g' \
        -e 's/@FACTORY_RESET@/${RUGIX_CTRL_DAEMON_FACTORY_RESET}/g' \
        -e 's/@SYSTEM_COMMIT@/${RUGIX_CTRL_DAEMON_SYSTEM_COMMIT}/g' \
        -e 's/@SYSTEM_REBOOT@/${RUGIX_CTRL_DAEMON_SYSTEM_REBOOT}/g' \
        -e 's/@APP_LIFECYCLE@/${RUGIX_CTRL_DAEMON_APP_LIFECYCLE}/g' \
        ${UNPACKDIR}/daemon.toml.in > ${D}${sysconfdir}/rugix/daemon.toml
    chmod 0644 ${D}${sysconfdir}/rugix/daemon.toml

    install -D -m 0644 ${UNPACKDIR}/rugix-ctrl-daemon.service \
        ${D}${systemd_system_unitdir}/rugix-ctrl-daemon.service
}

USERADD_PACKAGES = "${PN}"
GROUPADD_PARAM:${PN} = "--system rugix-daemon"

SYSTEMD_SERVICE:${PN} = "rugix-ctrl-daemon.service"
SYSTEMD_AUTO_ENABLE:${PN} = "enable"

CONFFILES:${PN} = "${sysconfdir}/rugix/daemon.toml"
RDEPENDS:${PN} = "rugix-ctrl (>= 1.3.0)"
