# Flight Deal Finder

Automatically searches for cheap flights from a configured origin city to a list of destinations and sends an email alert when a price drops below your threshold.

## How It Works

1. Reads destination cities and price thresholds from a Google Sheet (via Sheety)
2. If a city has a missing IATA code or lowest price, asks **Gemini AI** to fill it in automatically
3. Searches for the cheapest flight for each destination over the next 6 months (via Amadeus API)
4. Sends an email alert with flight details and a Google Flights link if the price is below the threshold

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/Perel23/flight-deals.git
cd flight-deals
```

### 2. Install dependencies

```bash
pip install amadeus requests python-dotenv google-genai
```

### 3. Create a `.env` file

```
AMADEUS_API_KEY=your_amadeus_api_key
AMADEUS_SECRET=your_amadeus_secret
SHEETY_ENDPOINT=your_sheety_endpoint_url
SHEETY_BEARER_TOKEN=your_sheety_bearer_token
MY_EMAIL=your_gmail_address
GMAIL_APP_PASSWORD=your_gmail_app_password
ORIGIN_CITY_IATA=TLV
DESTINATION_EMAIL=email_to_send_alerts_to
GEMINI_API_KEY=your_gemini_api_key
```

### 4. Set up the Google Sheet

Create a Google Sheet with the following columns:

| city | iataCode | lowestPrice |
|------|----------|-------------|
| Paris | PAR | 90 |
| Bangkok | BKK | 330 |

Connect it to [Sheety](https://sheety.co) and use the endpoint as `SHEETY_ENDPOINT`.
Leave `iataCode` and `lowestPrice` empty for new cities — Gemini will fill them in automatically on the next run.

### 5. Get API keys

- **Amadeus** — [developers.amadeus.com](https://developers.amadeus.com) (free test account)
- **Sheety** — [sheety.co](https://sheety.co) (free tier)
- **Gemini** — [aistudio.google.com/apikey](https://aistudio.google.com/apikey) (free tier)
- **Gmail** — Enable 2FA on your Google account and generate an [App Password](https://myaccount.google.com/apppasswords)

### 6. Run

```bash
python main.py
```

## Project Structure

| File | Description |
|------|-------------|
| `main.py` | Entry point — orchestrates the full flow |
| `flight_search.py` | Amadeus API — searches for cheapest flights |
| `data_manager.py` | Sheety API — reads and updates the Google Sheet |
| `notification_manager.py` | Sends email alerts via Gmail SMTP |
| `ai_assistant.py` | Gemini AI — auto-fills missing IATA codes and price thresholds |