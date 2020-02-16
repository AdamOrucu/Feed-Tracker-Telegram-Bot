# Feed Tracker Telegram Bot
A bot for telegram that periodically checks for changes in a pages and sends a message if a change has occured.

### Usage
New bot needs to be created using *BotFather* from telegram

After this code is run the user needs to add the bot through telegram and send the `/start`command.

In order to `/add` a new website to be tracked the best approach is to send the following command 
`/add https://seths.blog/feed/` 

Other available commands:

- `/delete` removes a website from the list
- `/list` lists all the websites that are being tracked
