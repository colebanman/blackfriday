import datetime
import threading
import time
import json
import pick
import csv
import tkinter as tk
from tkinter import ttk

import requests
from GoatScript import GoatScript

accountData = {}
aiAnswers = {}

with open("cards.csv", "r") as f:
    reader = csv.reader(f)
    cards = list(reader)

with open("accounts.json","r") as accounts:    
    data = json.load(accounts)
    fullJson = data
    accounts = data["accounts"]
    pxApiKey = data["pxApiKey"]
    

options = [ "- GOAT Trivia", "- GOAT Drops", "- GOAT Account Generator", "- Delete Accounts", "- AIO"]
option, index = pick.pick(options, f"SELECT BOT MODE ({len(accounts)} ACCOUNTS LOADED)", indicator='=>', default_index=0)

if option == "- GOAT Drops":
    headers = {
        'host': 'www.goat.com',
        'accept': 'application/json',
        'authorization': 'Token token=""',
        'accept-language': 'en-US,en;q=0.9',
        'user-agent': 'GOAT/2.66.3 (iPhone; iOS 17.0.3; Scale/3.00) Locale/en',
        'connection': 'keep-alive',
        'content-type': 'application/x-www-form-urlencoded',
    }

    # get current date in 2023-11-17T18:59:16.890383959Z format
    current_date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    data = '{"salesChannels":[1],"recordTypes":[5],"pageLimit":"125","eventTimeAfter":"' + str(current_date) + '","eventTimeBefore":"2023-11-26T13:45:00Z","pageNumber":"2","collapseOn":1,"eventGroupIncludes":[1],"collapseLimit":"25"}'

    response = requests.post(
        'https://www.goat.com/api/v1/consumer-search/event-search',
        headers=headers,
        data=data
    )
    
    shoes = []
    for shoe in response.json()["resultItems"]:
        shoe = shoe["drop"]
        if "soldOut" in shoe and shoe["soldOut"]:
            continue
        name = shoe["name"]
        id = shoe["id"]

        shoes.append(f"{name} ||| {id}")
    
    shoeOption, shoeOptionIndex = pick.pick(shoes, f"SELECT DROP", indicator='=>', default_index=0)
    shoeOptionId = shoeOption.split(" ||| ")[1]

else:
    shoeOptionId = ""

def main(index, fullJson):
    # get card from cards list based on index, but since there's only 125 cards once we get to 125 we just loop back to 0
    card = cards[index % len(cards)]

    goat = GoatScript(index, shoeOptionId, card, fullJson)
    if option == "- GOAT Account Generator":
        goat.createAccount()
        goat.onboard()
        return
    goat.getSession()
    if option == "- GOAT Trivia":
        goat.getTickets()
    elif option == "- GOAT Drops":
        goat.enterDrop()
    elif option == "- AIO":
        goat.getTickets()
        goat.enterDrop()

startThread = int(input("STARTING INDEX: "))
maxThreads = int(input("STOPPING INDEX: "))
args = [
    x for x in range(startThread, maxThreads)
]  # replace with actual arguments

if option == "- Delete Accounts":
    # delete from startThread to maxThreads
    del fullJson["accounts"][startThread:maxThreads]

    with open("accounts.json", "w") as outfile:
        json.dump(fullJson, outfile, indent=4)

    exit()

count = 0

for arg in args:
    count += 1

    thread = threading.Thread(target=main, args=(arg, fullJson,))
    thread.daemon = True  # Daemonize thread
    thread.start()

    if count == 1 and option == "- GOAT Trivia":
        time.sleep(25) # Ensures that the trivia AI only runs once
    time.sleep(0.05)  # Wait a bit for it to start
    if count == len(args):
        time.sleep(5000) # Ensures user can use CTRL+C to stop tasks.