# Deploy individual partitions created by WIC.
#
# When creating a Rugix update bundle, we need to be able to access the individual
# partitions of the created image. To this end, this class extends the `image` class
# through the `IMAGE_CLASSES` variables. It adds the `deploy_partitions_wic` task
# which copies the partitions created by WIC to the deployment directory.

do_deploy_partitions_wic() {
    wic_build_dir="${WORKDIR}/build-wic"
    target_dir="${IMGDEPLOYDIR}/partitions"
    for partition_file in "${wic_build_dir}"/*.direct.*; do
        partition_name=$(basename "${partition_file}")
        partition_id="${partition_name##*.}"
        mkdir -p "${target_dir}"
        cp "${partition_file}" "${target_dir}/${IMAGE_NAME}.wic.${partition_id}"
    done
}

addtask deploy_partitions_wic after do_image_wic before do_image_complete
