import pytz, datetime
import requests
import json
import sys


def API_CALL_STR(subreddit, start, end): 
    return ("https://api.pushshift.io/reddit/submission/search/?" +
        f"after={start}&" +
        f"before={end}&" +
        "size=500&" +
        f"sort_type=created_utc&sort=asc&" +
        f"subreddit={subreddit}")

def scrape(subreddit, start, end, output_file=None):
    if output_file is None:
        output_file = f'{subreddit}_start={start}_end={end}.json'
    start = utc_timestamp(start)
    end = utc_timestamp(end)
    objs = []
    while True:
        call_str = API_CALL_STR(subreddit, start, end)
        try:
            response = requests.get(call_str)
        except:
            print(f'Error in request: {call_str}'); exit()
        if not response.status_code == 200:
            print(f'Error in response: {response.status_code}'); exit()
        # try:
        data = response.json()['data']
        if len(data) < 1:
            print('Terminated due to no data')
            # fromtimestamp always uses local
            sdt = datetime.datetime.fromtimestamp(start)
            edt = datetime.datetime.fromtimestamp(end)
            print(f'start: {sdt} | end: {edt}')
            break
        objs.extend(data)
        start = data[-1]['created_utc']
    with open(output_file, 'w') as output:
        output.write(json.dumps({'comments' : objs}, indent=4))

def utc_timestamp(time):
    # found on stack: answer by John Millikin, edited by jo jo
    # https://stackoverflow.com/questions/79797/how-to-convert-local-time-string-to-utc
    # accounts for daylight savings time
    # args: time = f'{year}-{month}-{day} {hour}:{minute}:{second}'
    local = pytz.timezone ("America/New_York")
    naive = datetime.datetime.strptime (time, "%Y-%m-%d-%H:%M:%S")
    local_dt = local.localize(naive, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)
    return int(utc_dt.timestamp())


if __name__ == '__main__':
    _, subreddit, start, end, *_ = sys.argv
    scrape(subreddit, start, end)

