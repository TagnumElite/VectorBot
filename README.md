# VectorBot
#### A discord bot created for [Vector eSports](http://vectoresports.co.za)

## Installation
Check the [Wiki](https://github.com/TagnumElite/VectorBot/wiki)

## Contributing
I don't have any rules yet but I will in the future!

## Features:
- [ ] Database Extension
    - [x] MessageDB
    - [ ] ServerDB
    - [ ] MembersDB
- [ ] Multi Server Support (Requires Database Extension to be done)
- [x] Splash (Member Splash Management)
- [ ] Steam Extension ([SteamRep API](https://github.com/EliteKast/libzaek.py))
- [ ] Wordpress API Support (More Importantly REST API Support)
- [ ] Feeds Extension (RSS, ATOM, MOAR)
- [ ] Twitch, Twitter, Facebook, etc. `I have no idea how to explain`
- [ ] Image Extension (Image Manipulation) `Only Enabled In Dev Mode`
- [ ] Email Support (Send emails when needed) `No Extension, will have no commands.`
- [ ] Music Player (Will be done in the future)  `Only Enabled In Dev Mode`
- [ ] Record Player (Prep. Not Possible right now) `Currently Impossible`

## TODO:
- [ ] Clean Out Code
- [ ] Flesh Out Documentation
- [ ] Change database logging to be similar to wordpress meta system `This allows me to change the database without having to drop tables or modify them`

## Discord
[![Join me on discord](http://splash.vectoresports.co.za/members/179891973795086336.png 'Join me on discord')](https://discord.gg/qJbwA7d)

### Image Extension?
This will be used for a few things like when adding a new team on a website (WORDPRESS API SUPPORT) and it has an avatar. We will take that avatar and find the most used color and make them a role on discord with that color. Like I said, experimental and will not be enabled by default means.

## FAQ : The Short Version
### Where is the main FAQ?
In the [Wiki](https://github.com/TagnumElite/VectorBot/wiki)!
### This bot looks familiar?
Thats because to understand discord.py I forked @Rapptz RoboDanny and built off on that.
### I want to report a bug:heavy_exclamation_mark:
Make an issue, same goes for suggestions!
### How did you learn to code? :coffee:
Self taught. Going around, looking at docs and taking apart existing code to see how everything works.
### I got an JSON Error with the configs.json!
Please remove all 'comments' EG `//This is a comment` from the configs.json. These comments are for guidelines and break the JSONDecoder
### Why start on version 6?
Because this is an continuation of my other bots