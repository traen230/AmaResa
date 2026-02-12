var getUrlParameter = function (sParam) {

    var sPageURL = window.location.search.substring(1);
    var sURLVariables = sPageURL.split('&');
    for (var i = 0; i < sURLVariables.length; i++) {
        var sParameterName = sURLVariables[i].split('=');
        if (sParameterName[0] == sParam) {
            return sParameterName[1];
        }
    }

    try {

        if (window.location.href.indexOf('studio.youtube.com') >= 0) {

            // If there are no parameters
            if (window.location.href.indexOf('/#/') > 0) {
                return null;
            }

            var poundLocation = window.location.href.indexOf('#');
            var querystring = window.location.href.substring('https://studio.youtube.com/'.length, poundLocation);
            var sURLVariables = querystring.split('&');
            for (var i = 0; i < sURLVariables.length; i++) {
                var sParameterName = sURLVariables[i].split('=');
                if (sParameterName[0] == sParam) {
                    return sParameterName[1];
                }
            }


        }
    }
    catch (e) {

    }

    return null;
};

var tokenParam = getUrlParameter('t');
var channelParam = getUrlParameter('c');
var redirectParam = getUrlParameter('r');

if (tokenParam) {

    if (tokenParam == 'remove') {

        // When debugging with web-ext change sync to local in line below.
        chrome.storage.sync.remove("tubebuddyToken-" + channelParam, function () { console.log('token removed'); })
    }
    else {
        var dbSaveObject = {};
        dbSaveObject["tubebuddyToken-" + channelParam] = tokenParam;

        // When debugging with web-ext change sync to local in line below.
        chrome.storage.sync.set(dbSaveObject, function () {

            if (redirectParam) {
                var url = '';

                if (window.location.href.indexOf('studio.youtube.com') >= 0) {

                    redirectParam = decodeURIComponent(redirectParam);
                    var poundLocation = redirectParam.indexOf('#');
                    var fullPath = redirectParam.substring(poundLocation);                    
                    if (redirectParam.indexOf('cid=') > 0) {
                        url = redirectParam.substring(0, poundLocation) + '&tbft=1' + fullPath;                        
                    } else {
                         url = 'https://studio.youtube.com/?tbft=1' + fullPath;                        
                   }

                } else {
                    if (redirectParam.indexOf('?') > 0 || redirectParam.indexOf('%3F') > 0 || redirectParam.indexOf('%3f') > 0)
                        url = decodeURIComponent(redirectParam) + '&tbft=1';
                    else
                        url = decodeURIComponent(redirectParam) + '?tbft=1';
                }

                window.location = url;
            }

        });
    }

}
