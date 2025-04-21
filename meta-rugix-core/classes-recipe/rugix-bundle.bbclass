# Class for creating Rugix bundles.

LICENSE ?= "MIT"

DEPENDS = "rugix-bundler-native"

inherit nopackages

RUGIX_BUNDLE_PAYLOADS ??= ""

RUGIX_BUNDLE_BASE_NAME ??= "${PN}"
RUGIX_BUNDLE_NAME ??= "${RUGIX_BUNDLE_BASE_NAME}-${MACHINE}-${DATETIME}"
RUGIX_BUNDLE_NAME[vardepsexclude] = "DATETIME"
RUGIX_BUNDLE_LINK_NAME ??= "${RUGIX_BUNDLE_BASE_NAME}-${MACHINE}"

BUNDLE_DIR ??= "${WORKDIR}/bundle"

python __anonymous() {
    payloads = d.getVar("RUGIX_BUNDLE_PAYLOADS").split()
    for payload in payloads:
        payload_var = f"RUGIX_PAYLOAD_{payload}"
        payload_flags = d.getVarFlags(payload_var) or {}
        d.appendVarFlag("do_unpack", "vardeps", f" {payload_var}")

        payload_image = payload_flags.get("image")

        if not payload_image:
            bb.error(f"No image set for payload {repr(payload)}.")
            return

        d.appendVarFlag('do_unpack', 'depends', f" {payload_image}:do_image_complete")
}


python do_configure() {
    import os
    import shutil

    from pathlib import Path

    machine = d.getVar("MACHINE")

    deploy_dir_image = Path(d.getVar("DEPLOY_DIR_IMAGE"))
    deploy_dir_partitions = deploy_dir_image / "partitions"

    payloads = d.getVar("RUGIX_BUNDLE_PAYLOADS").split()

    bundle_dir = Path(d.getVar("BUNDLE_DIR"))
    os.makedirs(bundle_dir, exist_ok=True)

    payloads_dir = bundle_dir / "payloads"
    os.makedirs(payloads_dir, exist_ok=True)

    lines = ['update-type = "full"', 'hash-algorithm = "sha512-256"']

    for partition, payload in enumerate(payloads, 1):
        payload_var = f"RUGIX_PAYLOAD_{payload}"
        payload_flags = d.getVarFlags(payload_var) or {}
        d.appendVarFlag("do_unpack", "vardeps", f" {payload_var}")

        payload_image = payload_flags.get("image")
        payload_partition = payload_flags.get("partition")

        if not payload_partition:
            bb.error(f"No partition set for payload {repr(payload)}.")
            return
        
        partition_prefix = f"{payload_image}-{machine}"
        partition_suffix = f"p{payload_partition}"
        partition_file = None
        for file in deploy_dir_partitions.iterdir():
            if not file.name.startswith(partition_prefix):
                continue
            if not file.name.endswith(partition_suffix):
                continue
            partition_file = file
            break
        if not partition_file:
            bb.error(f"Partition {payload_partition} of image {payload_image} not found.")
            return
        shutil.copy2(partition_file, payloads_dir / f"partition{partition}.img")

        lines.append("[[payloads]]")
        lines.append(f'filename = "partition{partition}.img"')
        lines.append("[payloads.delivery]")
        lines.append('type = "slot"')
        lines.append(f'slot = "{payload}"')
    
    with open(bundle_dir / "rugix-bundle.toml", "wt", encoding="utf-8") as rugix_bundle:
        rugix_bundle.write("\n".join(lines))
}

do_bundle() {
    rugix-bundler bundle "${BUNDLE_DIR}" "${WORKDIR}/system.rugixb"

}

addtask bundle after do_configure before do_deploy

inherit deploy

do_deploy() {
    install -d ${DEPLOYDIR}
	install -m 0644 ${WORKDIR}/system.rugixb ${DEPLOYDIR}/${RUGIX_BUNDLE_NAME}.rugixb
    ln -sf ${RUGIX_BUNDLE_NAME}.rugixb ${DEPLOYDIR}/${RUGIX_BUNDLE_LINK_NAME}.rugixb
}

addtask deploy before do_build
