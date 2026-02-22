(() =>  {
    // Hook XMLHttpRequest prototype
    const XHR = XMLHttpRequest.prototype;
    const send = XHR.send;
    const open = XHR.open;


    // Open hook
    XHR.open = function (method, url) {
        this.url = url;
        return open.apply(this, arguments);
    }

    // Send hook
    XHR.send = function() {

        this.addEventListener('load', function() {
            if (this.url.includes('v1/ars/grst')) {

                // Parse the JSON from v1/ars/grst
                const response = JSON.parse(this.response);

                // Pull sessionToken from the object
                const sessionToken = response ? response.sessionToken : null;

                if(sessionToken) {

                    // Dispatch event for the content_script.js to receive the token
                    const event = new CustomEvent('tb-token-found', {
                        detail: {sessionToken}
                    });

                    

                    window.dispatchEvent(event);

                }
            }
        });

        return send.apply(this, arguments);
    };
})();