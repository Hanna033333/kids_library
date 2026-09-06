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
 * Detects if the current browser is a bot or automation tool
 */
const isBotOrAutomation = (): boolean => {
    if (typeof window === "undefined" || typeof navigator === "undefined") return true;

    // 1. Check for headless browsers
    if (navigator.webdriver) {
        console.log("🤖 Bot detected: WebDriver flag");
        return true;
    }

    // 2. Check User-Agent for common bot patterns
    const userAgent = navigator.userAgent.toLowerCase();
    const botPatterns = [
        'headless',
        'phantom',
        'selenium',
        'puppeteer',
        'playwright',
        'chrome-lighthouse',
        'bot',
        'crawler',
        'spider',
        'scraper',
    ];

    for (const pattern of botPatterns) {
        if (userAgent.includes(pattern)) {
            console.log(`🤖 Bot detected: User-Agent contains "${pattern}"`);
            return true;
        }
    }

    // 4. Check for automation-specific properties
    if ((window as any).__nightmare || (window as any)._phantom || (window as any).callPhantom) {
        console.log("🤖 Bot detected: Automation framework detected");
        return true;
    }

    return false;
};

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
    if (localStorage.getItem("checkjari_ignore_tracking") === "true") {
        return true;
    }

    // Check for bot/automation
    if (isBotOrAutomation()) {
        return true;
    }

    return false;
};

export const sendGAEvent = (eventName: string, eventParams?: Record<string, any>) => {
    const ignored = shouldIgnoreTracking();

    // 개발 환경에서는 차단 여부와 관계없이 콘솔에 로그를 출력하여 이벤트를 검증할 수 있도록 함
    if (process.env.NODE_ENV === "development") {
        console.log(`📢 [GA4 Event] ${eventName}`, eventParams, ignored ? "(Ignored by tracking policy)" : "");
    }

    if (ignored) return;

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

/**
 * GA 이벤트 전송 후 페이지 이동 — OAuth 콜백처럼 이벤트 직후 리다이렉트하는 상황에서 사용.
 * gtag의 event_callback으로 전송 완료를 기다린 뒤 navigate하여 이벤트 유실을 방지한다.
 * gtag 미초기화 시 300ms 타임아웃 후 폴백 이동.
 */
export const sendGAEventAndRedirect = (
    eventName: string,
    eventParams: Record<string, any>,
    redirectUrl: string
) => {
    const ignored = shouldIgnoreTracking();

    if (process.env.NODE_ENV === "development") {
        console.log(`📢 [GA4 Event+Redirect] ${eventName}`, eventParams, `→ ${redirectUrl}`, ignored ? "(Ignored)" : "");
    }

    const doRedirect = () => window.location.replace(redirectUrl);

    if (ignored || typeof window === "undefined" || !window.gtag) {
        doRedirect();
        return;
    }

    // 전송 완료 콜백으로 리다이렉트, 300ms 타임아웃 안전장치
    const timer = setTimeout(doRedirect, 300);
    window.gtag("event", eventName, {
        ...eventParams,
        event_callback: () => {
            clearTimeout(timer);
            doRedirect();
        },
    });
};
