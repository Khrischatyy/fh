import { ref, onUnmounted } from 'vue';
import type { PreparedPhotoSwipeOptions, SlideData } from 'photoswipe';
import type { Ref } from 'vue';

import PhotoSwipe from 'photoswipe';

// Helper function to get image dimensions
function getImageDimensions(url) {
    // SSR guard - return default dimensions during server-side rendering
    if (!process.client) {
        return Promise.resolve({ width: 1200, height: 900 });
    }

    return new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = () => {
            resolve({ width: img.naturalWidth, height: img.naturalHeight });
        };
        img.onerror = reject;
        img.src = url;
    });
}

export function usePhotoSwipe() {
    const pswpElement: Ref<HTMLDivElement | null> = ref(null);
    let gallery: PhotoSwipe | null = null;

    const openGallery = async (items: SlideData[], index: number) => {
        // SSR guard - prevent gallery from opening during server-side rendering
        if (!process.client || !pswpElement.value) return;

        // Fetch dimensions for each photo
        const processedItems = await Promise.all(items.map(async (photo) => {
            try {
                const dimensions = await getImageDimensions(photo.src);
                return {
                    src: photo.src,
                    w: dimensions.width || 1200, // Default width if not specified
                    h: dimensions.height || 900  // Default height if not specified
                };
            } catch {
                return {
                    src: photo.src,
                    w: 1200, // Default width if error
                    h: 900   // Default height if error
                };
            }
        }));

        const options: PreparedPhotoSwipeOptions = {
            dataSource: processedItems,
            bgOpacity: 0,
            spacing: 0.12,
            easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
            maxWidthToAnimate: 0.5,
            allowPanToNext: true,
            loop: true,
            pinchToClose: true,
            closeOnVerticalDrag: true,
            hideAnimationDuration: 333,
            showAnimationDuration: 333,
            zoomAnimationDuration: 333,
            escKey: true,
            arrowKeys: true,
            trapFocus: true,
            returnFocus: true,
            clickToCloseNonZoomable: true,
            imageClickAction: false,
            bgClickAction: false,
            wheelToZoom: true,
            tapAction: false,
            doubleTapAction: false,
            preloaderDelay: 200,
            indexIndicatorSep: ' of ',
            errorMsg: 'This image could not be loaded',
            preload: [1, 1],
            index: index,
            gallery: pswpElement.value  // Using gallery property
        };

        // Initialize the gallery
        gallery = new PhotoSwipe(options);
        gallery.init();
    };

    onUnmounted(() => {
        gallery?.destroy();
        gallery = null;
    });

    return { pswpElement, openGallery };
}