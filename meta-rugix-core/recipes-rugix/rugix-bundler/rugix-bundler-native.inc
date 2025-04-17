DESCRIPTION = "Native version of Rugix Bundler"
LICENSE = "CLOSED"

inherit native

python __anonymous() {
    arch = d.getVar("BUILD_ARCH")
    target = {
        "x86_64": "x86_64-unknown-linux-musl",
        "aarch64": "aarch64-unknown-linux-musl",
    }.get(arch, None)

    if target is None:
        raise bb.parse.SkipRecipe("Unsupported build architecture: %s" % arch)
    
    version = d.getVar('RUGIX_VERSION')

    d.setVar("SRC_URI", f"https://github.com/silitics/rugix/releases/download/v{version}/{target}.tar;name={arch};subdir=rugix-binaries")
}

S = "${WORKDIR}"

do_install() {
    install -d ${D}${bindir}
    install -m 0755 ${S}/rugix-binaries/rugix-bundler ${D}${bindir}/rugix-bundler
}