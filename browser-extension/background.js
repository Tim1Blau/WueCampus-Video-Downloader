// Setup Context Menu
chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: "downloadWuecampusVideo",
        title: "Save WueCampus Video",
        contexts: ["frame"]
    });
});

// Context Menu Item Selected
chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === "downloadWuecampusVideo") {
        const iframeUrl = info.frameUrl;
        console.log('Iframe URL:', iframeUrl);
        chrome.scripting.executeScript({
            target: { tabId: tab.id, frameIds: [info.frameId] },
            function: extractVideoUrl
        }, (results) => {
            if (results && results[0].result) {
                const videoUrl = results[0].result;
                const filename = videoUrl.split('/').pop();

                chrome.downloads.download({
                    url: videoUrl,
                    filename: filename,
                    saveAs: true
                }, (downloadId) => {
                    if (chrome.runtime.lastError) {
                        alertExtern('Download failed:', chrome.runtime.lastError);
                    } else {
                        console.log('Download started, download ID:', downloadId);
                    }
                });
            } else {
                alertExtern("Failed to extract video URL. Maybe this site hides the URL in a different way?");
            }
        });
    }
});

function alertExtern(msg) {
    chrome.scripting.executeScript({
        target: { tabId: tab.id },
        function: (a) => alert(a),
        args: [msg]
    });
}

function extractVideoUrl() {
    // Loop through all <script> tags to find the right one with the variables
    for (let script of document.scripts) {
        const scriptContent = script.textContent;

        // Look for the script that contains the Video_Server and Video_Properties
        if (scriptContent.includes('var Video_Properties')) {
            // Extract the values using a regular expression or by parsing the script content
            const videoServerMatch = scriptContent.match(/var Video_Server = "(https:\/\/[^\s]+)"/);
            const videoPropertiesMatch = scriptContent.match(/var Video_Properties = (\{[^\}]+\});/);

            if (videoServerMatch && videoPropertiesMatch) {
                // Parse the JSON-like string for Video_Properties
                const videoServer = videoServerMatch[1];
                const videoPropertiesStr = videoPropertiesMatch[1];

                // Convert the Video_Properties string to an object
                const videoProperties = JSON.parse(videoPropertiesStr.replace(/(\w+):/g, '"$1":'));

                // Get the path from Video_Properties
                const videoUrl = `${videoServer}${videoProperties.Application}/${videoProperties.path}`;

                console.log('Extracted WueCampus Video URL:', videoUrl);

                return videoUrl; // Exit after the first match, or handle multiple iframes
            }
        }
    }

    console.log('Unable to find the necessary variables inside the iframe.');
    return null;
}