const addXhrListenerScript = async (nonce) => {

    const xhrOverrideScript = document.createElement('script');
    xhrOverrideScript.id = 'tb_listeners';
    xhrOverrideScript.setAttribute('nonce', nonce);
    xhrOverrideScript.src = chrome.runtime.getURL('tokenListener.js');
    document.head.prepend(xhrOverrideScript);

};

const addTokenListener = () => {
    
    window.addEventListener('tb-token-found', (e) => {
        
        let sessionToken;
        if(e && e.detail && e.detail.sessionToken)
            sessionToken = e.detail.sessionToken;

        if(!sessionToken) {
            TBUtilities.Log('No session token passed')
            return;
        }
        
        const tokenKey = `tb-session-token-${TBGlobal.CurrentChannelId()}`;
        // Store to local extension storage
        TBExtension.SetDbValue(tokenKey, sessionToken);
        
        TBUtilities.Log(`Saved session token to extension db key: ${tokenKey}, value: ${sessionToken}`);

    })
}

const waitForProfile = () => {
  return new Promise((resolve)=>{
      let inc = 0;
      const interval = setInterval(()=> {
          if(++inc >= 10){
              clearInterval(interval);
              resolve(false);
          }
          
          if(TBGlobal.Profile() !== null){
              clearInterval(interval);
              resolve(true);
          }
      }, 400)
  })  
};
const sleep = ms => new Promise(r => setTimeout(r, ms));

// Run script
(async () => {
    
    const profileFetched = await waitForProfile();
    
    if(!profileFetched){
        TBUtilities.Log(`Session token capture failed. Profile not fetched.`);
        return;
    }
    
    TBUtilities.Log(`Proceeding to capture session token for channelId: ${TBGlobal.CurrentChannelId()}`);
    
    addTokenListener();
    
    await sleep(300);

    // Try 10 times then bail
    let attempts = 0;

    while (true) {

        await sleep(300);

        if (attempts++ > 10) break;

        const body = document.head.innerHTML;
        
        const nonce = body.substring(
            body.lastIndexOf('"cspNonce":"'),
            body.lastIndexOf('","canaryState"')
        ).replace('"cspNonce":"', '');

        if (!nonce) {
            continue;
        }

        await addXhrListenerScript(nonce);
        return;

    }

    await TBUtilities.ReportProductEvent('Session Token Capture Failure',
    {
        timestamp: new Date().toISOString(),
        channel_id: TBGlobal.CurrentChannelId(),
        current_page: window.location.href
    });

    TBUtilities.Log('Failed to find a nonce')

})()