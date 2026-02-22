var insert_node = document.createElement('div');
insert_node.id = "tubebuddy_chrome_extension_installed";
document.documentElement.appendChild(insert_node);

function receiveMessage(event) {

    if (event.origin !== "https://studio.youtube.com")
        return;

    if (event.data.tbevent && event.data.tbevent === "ScreenCapRequest") {
        var imageUrl = null;
        try {
            imageUrl = getStillFromVideo();
        }
        catch (ex) {
            console.log(ex);
        }
        finally {
            event.data.tbevent = "ScreenCapResponse";
            event.data.imageUrl = imageUrl;
            event.source.postMessage(event.data,
                event.origin);
        }
    }
}
window.addEventListener("message", receiveMessage, false);

//capute image from the iframe player
function getStillFromVideo() {

    //set cors options on all video streaming tags
    var videoStream = document.getElementsByClassName('video-stream')[0];
    videoStream.setAttribute('crossorigin', 'anonymous');

    var imageUrl = null;
 
    var video = document.getElementsByClassName('html5-main-video')[0];


    //create canvas to capture
    var newCanvas = document.createElement('canvas');
    newCanvas.id = "tb-thumbnail-temp-canvas";
    newCanvas.width = 1280;
    newCanvas.height = 720;
    
    document.body.appendChild(newCanvas);

    var canvas = document.getElementById('tb-thumbnail-temp-canvas');
    var context = canvas.getContext('2d');

    canvas.width = 1280;
    canvas.height = 720;

    // Define the size of the rectangle that will be filled (basically the entire element)
    context.fillRect(0, 0, 1280, 720);

    // Grab the image from the video
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    //return the url so we can use it 
    imageUrl = canvas.toDataURL();


    return imageUrl;
}
