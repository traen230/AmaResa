// Manifest V3 wrapper for existing background scripts

try {
    importScripts('./background.js');
    importScripts('./backgroundMessaging.js');
    importScripts('./FetchUtilities.js');
    importScripts('./destBackground.js');
} catch (e) {
    console.log(e);
}
