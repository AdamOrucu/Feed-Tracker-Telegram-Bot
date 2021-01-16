# WEb Tracker Telegram Bot
A bot for telegram that periodically checks for changes on rss pages and sends a message if a change has occured.

## Usage
New bot needs to be created using *BotFather* from telegram. Instructions can be found in the following [link](https://core.telegram.org/bots). After the bot is created the API token needs to be added to the config.py file.

The bot can be run by sending the `/start` command needs to be sent to it.

In order to `/add` a new website to be tracked the best approach is to send the following command 
`/add https://seths.blog/feed/` 

Other available commands:

- `/delete` removes a website from the list
- `/list` lists all the websites that are being tracked
