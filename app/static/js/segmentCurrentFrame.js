function segmentCurrentFrame() {
    const frameNumber = currentFrameIndex;
    const frameName = `frame_${frameNumber + 1}.jpg`;

    console.log(`Segmenting: /segment_frame/${currentFolder}/${frameName}`);

    fetch(`/segment_frame/${currentFolder}/${frameName}?model=${selectedModel}`)
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                const maskUrl = result.mask_url;

                // Update the metrics in HTML
                document.getElementById('iou-value').innerText = result.metrics.IoU;
                document.getElementById('dsc-value').innerText = result.metrics.DSC;
                document.getElementById('ssim-value').innerText = result.metrics.SSIM;

                // Display the segmentation result
                const resDiv = document.getElementById('segment-result');
                if (resDiv) {
                    resDiv.innerHTML = `<img src="${maskUrl}" alt="Segmentation mask">`;
                }

                const tile1 = document.querySelector('.video-right .video-wrapper:nth-child(1) .video-tile');
                tile1.innerHTML = `<img src="${maskUrl}" style="max-width: 100%; max-height: 100%;">`;

            } else {
                alert('Error: ' + result.error);
            }
        })
        .catch(error => {
            console.error('Error during segmentation:', error);
        });
}
