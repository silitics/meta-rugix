# Rugix bundle image type.
#
# Produces a .rugixb update bundle. BSP sublayers set RUGIX_SLOTS in
# their layer.conf to map slot names to sources:
#   "system:2"                     - WIC partition number
#   "boot:file:fitImage"           - file in DEPLOY_DIR_IMAGE (relative)
#   "boot:file:/path/to/file.img"  - absolute path (e.g., IMGDEPLOYDIR)

IMAGE_TYPES += "rugixb"
IMAGE_TYPEDEP:rugixb = "wic"

CONVERSIONTYPES += "hash"
CONVERSION_CMD:hash = "rugix-bundler hash ${IMAGE_NAME}.${type} >${IMAGE_NAME}.${type}.hash"
CONVERSION_DEPENDS_hash = "rugix-bundler-native"

RUGIX_SLOTS ??= ""

do_image_rugixb[depends] += "rugix-bundler-native:do_populate_sysroot"

IMAGE_CMD:rugixb () {
    bundle_dir="${WORKDIR}/build-rugixb"
    rm -rf "${bundle_dir}"
    mkdir -p "${bundle_dir}/payloads"

    wic_build_dir="${WORKDIR}/build-wic"

    cat > "${bundle_dir}/rugix-bundle.toml" << 'EOF'
update-type = "full"
hash-algorithm = "sha512-256"
EOF

    payload_idx=1
    for slot_spec in ${RUGIX_SLOTS}; do
        slot_name="${slot_spec%%:*}"
        slot_source="${slot_spec#*:}"

        case "${slot_source}" in
            file:*)
                # File-based slot. Relative paths resolve against
                # DEPLOY_DIR_IMAGE; absolute paths are used as-is, letting
                # BSP layers point at files that only live in IMGDEPLOYDIR
                # at do_image_rugixb time.
                slot_file="${slot_source#file:}"
                case "${slot_file}" in
                    /*) src_path="${slot_file}" ;;
                    *)  src_path="${DEPLOY_DIR_IMAGE}/${slot_file}" ;;
                esac
                if [ ! -f "${src_path}" ]; then
                    bbfatal "File ${src_path} not found for slot ${slot_name}"
                fi
                cp "${src_path}" "${bundle_dir}/payloads/payload${payload_idx}.raw"
                ;;
            *)
                # Partition-based slot: copy from WIC build directory.
                partition_num="${slot_source}"
                partition_file=""
                for f in "${wic_build_dir}"/*.direct.p${partition_num}; do
                    if [ -f "$f" ]; then
                        partition_file="$f"
                        break
                    fi
                done
                if [ -z "${partition_file}" ]; then
                    bbfatal "Partition ${partition_num} not found in WIC build directory for slot ${slot_name}"
                fi
                cp "${partition_file}" "${bundle_dir}/payloads/payload${payload_idx}.raw"
                ;;
        esac

        cat >> "${bundle_dir}/rugix-bundle.toml" << SLOTEOF

[[payloads]]
filename = "payload${payload_idx}.raw"

[payloads.delivery]
type = "slot"
slot = "${slot_name}"

[payloads.block-encoding]
hash-algorithm = "sha512-256"
chunker = "casync-64"
compression = { type = "xz", level = 9 }
deduplication = true
SLOTEOF

        payload_idx=$(expr ${payload_idx} + 1)
    done

    if [ "${payload_idx}" -eq 1 ]; then
        bbfatal "RUGIX_SLOTS is empty, set it in the BSP layer to define the slot-to-partition mapping."
    fi

    # Native filesystem tools must bypass pseudo so missing output paths retain
    # their real errno; Rugix Bundler uses that to validate distinct paths.
    PSEUDO_UNLOAD=1 rugix-bundler bundle "${bundle_dir}" "${IMGDEPLOYDIR}/${IMAGE_NAME}.rugixb"
}
