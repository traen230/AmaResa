
chrome.runtime.onMessage.addListener((request, sender, sendResponse)=>{

    if(request.request === 'tb-react') {
        fetch(request.url, {
            headers: {
                // Set headers
                "currentChannelId": request.headers.currentChannelId,
                "currentChannelToken": request.headers.currentChannelToken.toString(),
            }
        })
            .then(res => {
                if (res.ok) {
                    console.log(res);
                    return res.json();
                }
            })
            .then(res => {
                sendResponse({
                    ...res,
                    success: true,
                });
            })
            .catch(err => {
                console.error(err);
                // Getting an error for TBUtilities here...
                sendResponse({
                    ...err,
                    success: false
                })
            })
    }
    return true;
});