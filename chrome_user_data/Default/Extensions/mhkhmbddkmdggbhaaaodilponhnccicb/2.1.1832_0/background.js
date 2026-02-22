// receive a message from content scripts
async function tubeBuddyMessageReceived(messageRequest, callback) {
  // return true so the extension knows it's an async call
  const isAsyn = true;

  if (messageRequest.type === 'tb-corb-record') return false;

  switch (messageRequest.type) {
    // record url for corb url check
    // ajax requests
    case 'tb-xhr': {
      try {
        FetchUtilities.MakeFetchRequest(messageRequest, callback);
      } catch (ex) {
        callback({
          success: false,
          response: '',
          error: ex,
        });
      }
      break;
    }
    case 'tb-fetch': {
      try {
        const res = await FetchUtilities.MakeAsyncFetchRequest(messageRequest);
        callback(res);
      } catch (ex) {
        callback({
          success: false,
          response: '',
          error: ex,
        });
      }
      break;
    }
  }

  return isAsyn;
}

// -firefox background events
if (typeof browser !== 'undefined') {
  // console.log('FIREFOX Background');
  browser.runtime.onMessage.addListener(async (messageRequest, sender, sendResponse) => {
    if (sender.id === browser.runtime.id) {
      try {
        return await tubeBuddyMessageReceived(messageRequest, sendResponse);
      } catch (ex) {
        console.log('ex');
      }
    }
  });

  // Welcome new user on install
  browser.runtime.onInstalled.addListener((details) => {
    if (details.reason === 'install') {
      createTab(browser, { url: 'https://www.tubebuddy.com/account?from-ext=true' });
    } else if (details.reason === 'update') {
      clearReportedExtensionDOMIssues();
    }
  });
}
// -firefox background events end

// -chrome background events
else if (typeof chrome !== 'undefined') {
  // console.log('CHROME Background');
  chrome.runtime.onMessage.addListener(async (messageRequest, sender, sendResponse) => {
    if (sender.id === chrome.runtime.id) {
      try {
        return await tubeBuddyMessageReceived(messageRequest, sendResponse);
      } catch (ex) {
        console.log(ex);
      }
    }
  });

  // Welcome new user on install
  chrome.runtime.onInstalled.addListener((details) => {
    if (details.reason === 'install') {
      createTab(chrome, { url: 'https://www.tubebuddy.com/account?from-ext=true' });
    } else if (details.reason === 'update') {
      clearReportedExtensionDOMIssues();
    }
  });
}
// -chrome background events end

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
}

function clearReportedExtensionDOMIssues() {
  chrome.storage.sync.remove('tbReportedExtensionDOMIssues', () => {
    console.log('Removed DOM issues');
  });
}
