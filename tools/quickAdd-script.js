module.exports = {
    entry: async (params, settings) => {
        const captures = await fetch(settings["API URL"]+ "/capture").catch(async (error) => {
            // throw error with quickAdd dialog in case of network error
            await params.quickAddApi.infoDialog("API Error",
                ["quickAdd could not communicate with the Obsidian Audio Capture API.",
                "Make sure that you gave the correct API URL and key in the macro settings",
                "Otherwise, check that the API is running and accessible."])
        })

        if (captures.status >= 400 && captures.status < 600) {
            // throw error with quickAdd dialog in case of HTTP error
            await params.quickAddApi.infoDialog("API Error",
                ["quickAdd could not communicate with the Obsidian Audio Capture API.",
                "Make sure that you gave the correct API URL and key in the macro settings",
                "Otherwise, check that the API is running and accessible."])
            return ""
        }

        let returnString = "";
        const captureIDs = []
    
        const capturesJSON = await captures.json();
        
        Object.keys(capturesJSON).forEach( (capture) => {
            // add capture ID to array to update later
            captureIDs.push(capturesJSON[capture].capture_id)

            if (capturesJSON[capture].todo) {
                returnString = `${returnString}- [ ] ${capturesJSON[capture].text}\n`
            } else {
                returnString = `${returnString}${capturesJSON[capture].text}\n`
            }
            
        } )

        fetch(settings["API URL"] + "/capture/update", {
            method: "POST",
            body: JSON.stringify({
                captureIDs: captureIDs
            }),
            headers: { "Content-type": "application/json; charset=UTF-8"}
        });

        return returnString
    },
    settings: {
        name: "Obsidian Audio Capture",
        author: "BenBaja",
        description: "https://github.com/benbaja/obsidian-audio-capture",
        options: {
            "API URL": {
                type: "text",
                defaultValue: "",
                description: "URL of the Obsidian Audio Capture API",
            },
            "API key": {
                type: "text",
                defaultValue: "",
                description: "Obsidian Audio Capture API key",
            },
        }
    }
}