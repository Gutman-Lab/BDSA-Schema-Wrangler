// Configuration settings for BDSA Schema Wrangler

// Auto-refresh data after DSA sync completion
// Set to true to automatically refresh data after sync, false to keep current behavior
// To override: create a .env file in the main project root with REACT_APP_AUTO_REFRESH_AFTER_SYNC=false

// Get environment variable - supports both Create React App (REACT_APP_*) and Vite (VITE_*)
const getEnvVar = (name) => {
    // Try Create React App format first
    if (typeof process !== 'undefined' && process.env && process.env[`REACT_APP_${name}`] !== undefined) {
        return process.env[`REACT_APP_${name}`];
    }
    // Try Vite format (will only work in Vite environment)
    // Use a function constructor to avoid Babel parsing issues with 'import' keyword
    try {
        const checkVite = new Function('return typeof import !== "undefined" && import.meta && import.meta.env');
        if (checkVite()) {
            const getViteEnv = new Function('name', 'return import.meta.env["VITE_" + name]');
            const viteValue = getViteEnv(name);
            if (viteValue !== undefined) {
                return viteValue;
            }
        }
    } catch (e) {
        // Vite not available, continue
    }
    return undefined;
};

export const AUTO_REFRESH_AFTER_SYNC = getEnvVar('AUTO_REFRESH_AFTER_SYNC') !== 'false'; // Default to true

// Other configuration options can be added here
export const CONFIG = {
    AUTO_REFRESH_AFTER_SYNC
};
