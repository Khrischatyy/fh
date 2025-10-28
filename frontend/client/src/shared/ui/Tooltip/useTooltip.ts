import {provide, reactive} from "vue";
type TooltipType = {
    tooltipData: TooltipData;
    showTooltip: (event: MouseEvent, content: string) => void;
    hideTooltip: () => void;
}
type TooltipData = {
    isVisible: boolean;
    content: string;
    position: { x: number, y: number };
}
export const useTooltip = () => {

    const tooltipData = reactive({
        isVisible: false,
        content: '',
        position: { x: 0, y: 0 }
    });


    function showTooltip(event: MouseEvent, content: string) {
        const targetElement = event.target as HTMLElement;
        const rect = targetElement.getBoundingClientRect();
        const tooltipElement = document.querySelector('.tooltip'); // Selects the tooltip element

        // Temporarily update the tooltip content and make it visible for measurement
        tooltipElement.textContent = content;
        tooltipElement.style.visibility = 'hidden'; // Make it invisible but still renderable
        tooltipElement.style.position = 'absolute'; // Avoid affecting other elements
        tooltipElement.style.display = ''; // Ensure it is not display: none

        // Force a reflow/repaint to ensure the measurement is accurate
        const tooltipHeight = tooltipElement.clientHeight;

        // Determine the spacing and positioning
        const spacing = 10; // Spacing from the target element

        // Check if there is enough space at the bottom
        if (window.innerHeight - rect.bottom > tooltipHeight + spacing) {
            // If there is enough space, show the tooltip at the bottom
            tooltipData.position = { x: rect.left + window.scrollX + 10, y: rect.bottom + window.scrollY + spacing };
        } else {
            // If there is not enough space at the bottom, show the tooltip at the top
            tooltipData.position = {
                x: rect.left + window.scrollX + 10,
                y: rect.top + window.scrollY - tooltipHeight - spacing // Anchor the tooltip by its bottom edge
            };
        }

        // Set tooltipData properties to update the tooltip and make it visible
        tooltipData.content = content;
        tooltipData.isVisible = true;

        // Remove temporary styles used for measurement
        tooltipElement.style.visibility = ''; // Reset visibility to default
        tooltipElement.style.position = ''; // Reset position to default
        tooltipElement.style.display = ''; // Ensure it is display as needed (not none)
    }

    function hideTooltip() {
        tooltipData.isVisible = false;
    }
    provide<TooltipType>('tooltipData', {tooltipData, showTooltip, hideTooltip});
}