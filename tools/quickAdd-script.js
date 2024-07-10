module.exports = {
    entry: async (params, settings) => {
        const headers = {
            "Content-Type": "application/json",
            "authorization": settings.token
          }
        const captures = await fetch(settings["API URL"]+ "/capture/", {headers: headers}).catch(async (error) => {
            console.error(error)
            // throw error with quickAdd dialog in case of network error
            await params.quickAddApi.infoDialog("Network Error",
                ["quickAdd could not communicate with the Obsidian Audio Capture API.",
                "Please check your connection, or that the API is running and accessible."])
        })

        if (captures.status >= 400 && captures.status < 600) {
            // throw error with quickAdd dialog in case of HTTP error
            await params.quickAddApi.infoDialog(`HTTP Error ${captures.status}`,
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
            headers: headers
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
            "token": {
                type: "text",
                defaultValue: "",
                description: "Obsidian Audio Capture token",
            },
        }
    }
}