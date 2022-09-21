import json
import dateutil.parser as parser
import requests
import datetime


def getDataset(url: str) -> dict:
    request = requests.get(url)
    if request.status_code == 200:
        return request.json()
    else:
        raise RuntimeError('Failed to get the dataset')


def postDataset(url: str, dataset: str):
    request = requests.post(url, data=dataset)
    if request.status_code == 200:
        print("Dataset post successfully.")
    elif request.status_code == 400:
        raise RuntimeError('Incorrect answer.')
    else:
        raise RuntimeError('Failed to post the dataset.')


def generateInvitationsByCountry(input: dict) -> dict:

    countries = []
    country_of_events = {}

    for partner in input["partners"]:
        if partner["country"] not in country_of_events:
            country_of_events[partner["country"]] = {}

        for date in partner["availableDates"]:
            if date not in country_of_events[partner["country"]]:
                country_of_events[partner["country"]][date] = []
            country_of_events[partner["country"]][date].append(partner)

    for country, dates_to_each_partner in country_of_events.items():
        sorted_dates = sorted(dates_to_each_partner.keys())

        total_attenders = float('-inf')
        event_start_day = None
        most_attenders = []

        for idx in range(len(sorted_dates[:-1])):

            today = sorted_dates[idx]
            tomorrow = sorted_dates[idx + 1]

            if parser.parse(tomorrow) - parser.parse(today) != datetime.timedelta(1):
                continue

            today_attenders = set([(el['firstName'], el['lastName'], el['email']) for el in dates_to_each_partner[today]])
            tomorrow_attenders = set(
                [(el['firstName'], el['lastName'], el['email']) for el in dates_to_each_partner[tomorrow]])

            common_attenders = today_attenders.intersection(tomorrow_attenders)
            attenders_count = len(common_attenders)

            if attenders_count > total_attenders:
                total_attenders = attenders_count
                event_start_day = today
                most_attenders = common_attenders

        countries.append({"attendeeCount": total_attenders,
                          "attendees": [x[2] for x in most_attenders],
                          "name": country,
                          "startDate": None if total_attenders == 0 else event_start_day
                          })

    return {"countries": countries}


if __name__ == '__main__':
    # url to get dataset
    urlGet = "https://candidate.hubteam.com/candidateTest/v3/problem/dataset?userKey=49bf578711459f61ae9863ba42f2"

    # url to post handled dataset
    urlPost = "https://candidate.hubteam.com/candidateTest/v3/problem/result?userKey=49bf578711459f61ae9863ba42f2"

    # Get dataset from the given url
    inputs = getDataset(urlGet)

    # # Get handled dataset
    outputs = generateInvitationsByCountry(inputs)

    # Send back the result of generateSessionByUser() to POST URL
    #postDataset(urlPost, json.dumps(outputs, indent=2))