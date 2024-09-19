<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a id="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->
<!-- PROJECT LOGO -->
<br />
<div align="center">

<h3 align="center">Obsidian REST</h3>

  <p align="center">
    Self-hostable API for quick Obsidian captures
    <br />
    <a href="https://github.com/benbaja/obsidian-rest/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    ·
    <a href="https://github.com/benbaja/obsidian-rest/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

This project was developped as an API middleware to quickly capture notes or audio-notes to a self-hosted REST API for later upload and organisation on Obsidian.

It grew out of frustration with the mobile Obsidian app that makes quick capture mostly impossible in case of inspiration burst

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- GETTING STARTED -->
## Getting Started

### With Docker

Running this command will start the service on port 8888 (replace with the one you want)
```
  docker run -d -p 8888:8000 -v /your/persistent/directory:/obsidian-rest/var --name obsidian-rest ghcr.io/benbaja/obsidian-rest:latest
```
Make sure to map the X folder to a persistent space in your disk to keep the database alive

### Setup

1. Connect to your Obsidian-REST instance and create an admin password
2. Generate your API token
3. (Optional) Create a [Swiftink](https://www.swiftink.io/) account, and enter your Swiftink API token 
4. Download the quickAdd script and add it to your Obsidian vault
5. In Obsidian, install [quickAdd](https://github.com/chhoumann/quickadd)
6. Create a new quickAdd macro named `Obsidian-REST`, add the downloaded script as the only step
7. In the script settings, add the Obsidian-REST endpoint URL and the token 
8. Create a quickAdd capture choice, and use `{{MACRO:Obsidian-REST}}` as the capture format


<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

### POST /capture/create

Payload :

`capture_type: note | audio`

for text notes

`todo: boolean` (optional) formats the captured note as a to-do item

`text: string` text of the note to capture

for audio

`audio: base64` base64 encoding of the audio file

`file_name: string` name of the audio file

Returns : `new_note_id` or `new_audio_id`


### POST /capture/update

Payload :

`captureIDs: string[]` note IDs to mark as "fetched" on the database

Returns : `captureIDs`


### GET /capture/

Returns for each capture :

`text: string`

`date_added: date`

`todo: boolean`

`following: note_id` (optional)

`audio_id: audio_id` (optional)

`capture_id: note_id`


### GET /capture/<note_id>

Returns :

`text: string`

`date_added: date`

`todo: boolean`

`following: note_id` (optional)

`audio_id: audio_id` (optional)

`capture_id: note_id`


### iOS Shortcut

An iOS shortcut can be downloaded [here](https://www.icloud.com/shortcuts/7894978280be44558b51494cb8f78563)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [ ] Swagger API documentation
- [ ] Browsable captures
  - [ ] Re-trigger speech-to-text in case of failure
- [ ] Option for alternative speech-to-text (whisper)
- [ ] CI/CD
- [ ] Custom capture type and handling
    - [ ] Auto-generated quickAdd script for custom captures

See the [open issues](https://github.com/github_username/repo_name/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [Swiftink](https://www.swiftink.io/)

<p align="right">(<a href="#readme-top">back to top</a>)</p>
