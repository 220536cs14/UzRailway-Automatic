# UzRailway-Automatic

Automated Train Ticket Monitoring & Alert System

This project is an automation tool designed to monitor train ticket availability on the UzRailway platform. It continuously checks for available seats and updates for specific routes and dates, and sends notifications when changes occur.

Key Features:

- Real-time monitoring of train ticket availability
- Detection of new trains, wagons, and price changes
- Telegram bot integration for sending alerts and updates
- Interactive Telegram messages with buttons for user decisions
- State tracking to avoid duplicate or spam notifications
- JSON-based logging system to store monitoring history

Tech Stack:

- Python
- Selenium WebDriver for browser automation
- ChromeDriverManager for automatic driver management
- Telegram Bot API (via requests library)

How It Works:
The script opens a browser and navigates to the UzRailway website. It selects the departure and arrival stations (enter them into config file), as well as the travel date. After that, it starts a continuous monitoring loop where it checks available trains and their wagons. If any changes are detected, it sends an update to Telegram. The user can then choose whether to continue or stop the monitoring process through Telegram buttons.

Disclaimer:
This project is intended for educational and personal use only. It demonstrates automation techniques and should not be used for unauthorized or commercial scraping purposes.

Author: Azizxon Qahhorov
Goal: Senior Full-Stack QA Engineer
