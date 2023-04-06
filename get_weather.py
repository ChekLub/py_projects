import datetime
import json
import requests
import datetime as dt
import numpy as np


def get_weather_data(d_start, d_end):
    d_start = str(d_start)
    d_end = str(d_end)

    url = 'https://meteostat.p.rapidapi.com/stations/daily'
    headers = {
            'X-RapidAPI-Key': '###',
            'X-RapidAPI-Host': 'meteostat.p.rapidapi.com'
            }
    params = {
            'station': 27612, # moscow_id
            'start': d_start,
            'end': d_end
            }
    r = requests.get(url, params=params, headers=headers).text
    r_json = json.loads(r)

    n = len(r_json['data'])
    dates = np.empty(n, dtype= datetime.date)
    temps = np.empty((n, 3), dtype= np.float32)
    for i, date in enumerate(r_json['data']):
        dates[i] = datetime.date.fromisoformat(date['date'])
        temps[i, :] = date['tmin'], date['tmax'], date['tavg']

    return dates, temps

if __name__ == "__main__":
    d_start = dt.date(2020, 3, 1)
    d_end = dt.date.today() - dt.timedelta(days = 1)

    d, t = get_weather_data(d_start, d_end)
    print(d[0], t[0])