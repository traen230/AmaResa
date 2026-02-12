//-firefox background events
if (typeof browser !== "undefined") {

    //console.log('FIREFOX Background');
    browser.runtime.onMessage.addListener((messageRequest, sender, sendResponse) => {

        if (sender.id === browser.runtime.id) {

            // Recieve and search query message
            if (messageRequest.action != undefined && messageRequest.action == 'SEARCH_QUERY') {
                return createSearchTab(browser, messageRequest, sender);
            };

            // Relay messages from tab to tab via this background script
            if (messageRequest.action != undefined && messageRequest.action == 'RELAY_SEARCH_RESULTS') {
                return relayMessageToTab(browser, messageRequest, sender);
            };

            // Relay messages from tab to tab via this background script
            if (messageRequest.action != undefined && messageRequest.action == 'REMOVE_TAB') {
                return removeTab(browser, messageRequest);
            };

        }
    });

}
//-firefox background events end

//-chrome background events
else if (typeof chrome !== "undefined") {

    //console.log('CHROME Background');
    chrome.runtime.onMessage.addListener(function (messageRequest, sender, sendResponse) {

        if (sender.id === chrome.runtime.id) {

            // Recieve and launch a new tab for making search queries
            if (messageRequest.action != undefined && messageRequest.action == 'SEARCH_QUERY') {
                createSearchTab(chrome, messageRequest, sender, sendResponse);
            };

            // Relay messages from tab to tab via this background script
            if (messageRequest.action != undefined && messageRequest.action == 'RELAY_SEARCH_RESULTS') {
                relayMessageToTab(chrome, messageRequest, sender, sendResponse);
            };

            // Relay messages from tab to tab via this background script
            if (messageRequest.action != undefined && messageRequest.action == 'REMOVE_TAB') {
                removeTab(chrome, messageRequest, sendResponse);
            };
        }
    });

}

// Relay any message that comes in to the proper tab
function relayMessageToTab(browser, messageRequest, sender, sendResponse = null) {

    if (messageRequest.originId == undefined) {
        throw new Error('Origin tab id not defined');
    }

    // FireFox promise handler
    if (sendResponse == null) {
        return browser.tabs.sendMessage(messageRequest.originId, messageRequest);
    }

    // Chrome handler
    browser.tabs.sendMessage(messageRequest.originId, messageRequest);
}

// Open a new tab for making searches and insert a content script
function createSearchTab(browser, messageRequest, sender, sendResponse = null) {

    // FireFox promise handler
    // TODO: FIREFOX MV3
    // if (sendResponse == null) {
    //
    //     return createTab(browser, { url: 'https://www.youtube.com/results?search_query=', active: false })
    //         .then((tab) => {
    //             browser.tabs.executeScript(tab.id, { file: "/TubeBuddyFetchSearchResults.js" });
    //             return { originId: sender.tab.id, tabId: tab.id };
    //         }).catch((error) => {
    //             console.error('TAG_RANKINGS createTab error', error);
    //         });
    // }

    // Chrome handler
    return createTab(browser, { url: 'https://www.youtube.com/results?search_query=', selected: false }, function (tab) {
        sendResponse({ originId: sender.tab.id, tabId: tab.id });
        chrome.scripting.executeScript({
            target: {tabId: tab.id},
            files: ['TubeBuddyFetchSearchResults.js']
        });
    });

}

// Remove an existing tab
function removeTab(browser, messageRequest, callback = null) {

    if (messageRequest.tabId == undefined) {
        throw new Error('Tab id does not exist');
    }

    if (callback == null) {
        return browser.tabs.remove(messageRequest.tabId);
    }

    browser.tabs.remove(messageRequest.tabId, callback);

    return true;
}


// Create a new tab
function createTab(browser, options, callback = null) {

    if (options.url == undefined) {
        throw new Error('url is not defined');
    }

    // For FireFox
    if (callback == null) {
        return browser.tabs.create(options);
    }

    browser.tabs.create(options, callback);

    return true;
}