# TG Star Gift Sniper

A Telegram bot that monitors and automatically purchases profitable star gifts on the resale market.

## Features

- Continuous monitoring of Telegram star gift resale market
- Profit margin analysis for gift arbitrage opportunities
- Concurrent scanning for improved performance
- Discord notifications for successful purchases
- Configurable price ranges and profit thresholds
- Session persistence for uninterrupted operation

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd tgsniper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
pip install -U https://github.com/LonamiWebs/Telethon/archive/v1.zip
```

3. Create environment configuration:
```bash
cp .env.example .env
```

4. Configure your settings in `.env`:
   - Get your Telegram API credentials from https://my.telegram.org
   - Set up Discord webhook URL for notifications (optional)
   - Adjust price ranges and profit thresholds as needed

## Configuration

All configuration is handled through environment variables in the `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `API_ID` | Telegram API ID | Required |
| `API_HASH` | Telegram API Hash | Required |
| `SESSION_NAME` | Telegram session name | marketchecker |
| `DISCORD_WEBHOOK_URL` | Discord webhook for notifications | Optional |
| `MIN_PRICE` | Minimum gift price to consider | 600 |
| `MAX_PRICE` | Maximum gift price to consider | 1600 |
| `MIN_PROFIT_PERCENTAGE` | Minimum profit margin required | 30 |
| `USE_CONCURRENT` | Enable concurrent scanning | true |
| `BATCH_SIZE` | Concurrent batch size | 50 |
| `SCAN_INTERVAL` | Seconds between scans | 1.0 |
| `SUMMARY_INTERVAL` | Scans between Discord summaries | 100 |

## Usage

Run the sniper:
```bash
python main.py
```

The bot will:
1. Connect to Telegram using your credentials
2. Fetch all available star gifts
3. Continuously scan for resale opportunities
4. Analyze profit margins
5. Automatically purchase profitable gifts
6. Send Discord notifications for successful purchases

## How It Works

1. **Market Scanning**: Fetches all available star gifts and their resale listings
2. **Profit Analysis**: Groups gifts by type and calculates profit margins between lowest and second-lowest prices
3. **Filtering**: Only considers gifts within configured price range and minimum profit threshold
4. **Automated Purchase**: Attempts to purchase profitable opportunities automatically
5. **Notifications**: Sends Discord alerts for successful purchases and periodic summaries

## Safety Features

- Floor price filtering to avoid low-value collections
- Error handling for network issues and API limits
- Session persistence to maintain login state
- Configurable scan intervals to avoid rate limiting

## Disclaimer

This tool is for educational purposes. Use responsibly and in accordance with Telegram's terms of service. The authors are not responsible for any financial losses or account restrictions. 