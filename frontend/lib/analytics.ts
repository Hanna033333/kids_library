/**
 * Google Analytics 4 Event Tracking Utility
 */

export const GA_TRACKING_ID = "G-FG2WYB82L9";

// Extend the Window interface to include dataLayer
declare global {
    interface Window {
        dataLayer: any[];
        gtag: (...args: any[]) => void;
    }
}

/**
 * Checks if the current session should be ignored for tracking
 */
const shouldIgnoreTracking = () => {
    if (typeof window === "undefined") return true;

    // Check if URL has ?ignore=true
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get("ignore") === "true") {
        localStorage.setItem("checkjari_ignore_tracking", "true");
        return true;
    }

    // Check localStorage
    return localStorage.getItem("checkjari_ignore_tracking") === "true";
};

/**
 * Sends a custom event to Google Analytics
 * @param eventName Name of the event
 * @param eventParams Additional parameters for the event
 */
export const sendGAEvent = (eventName: string, eventParams?: Record<string, any>) => {
    if (shouldIgnoreTracking()) return;

    if (typeof window !== "undefined" && window.gtag) {
        window.gtag("event", eventName, eventParams);
    } else {
        // Fallback if gtag is not initialized yet
        if (typeof window !== "undefined") {
            window.dataLayer = window.dataLayer || [];
            window.dataLayer.push({
                event: eventName,
                ...eventParams,
            });
        }
    }
};
