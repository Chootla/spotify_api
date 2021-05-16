import sqlite3
import requests
import base64
import json


def check_status(status_code):
    if (status_code != 200):
        print("Error authorizaing: Helting...")
        exit(0)


conn = sqlite3.connect('top_songs_by_artists.sqlite')
c = conn.cursor()

url = "https://accounts.spotify.com/api/token"
headers = {}
data = {}

clientSecret = "099bf37c94cf4fb489a04e881cfdf16a"
clientId = "24b461a974084b09949f1b6312c40cbb"

message = f"{clientId}:{clientSecret}"
messageBytes = message.encode('ascii')
base64Bytes = base64.b64encode(messageBytes)
base64Message = base64Bytes.decode('ascii')

headers['Authorization'] = f"Basic {base64Message}"
data['grant_type'] = "client_credentials"

r = requests.post(url, headers=headers, data=data)

check_status(r.status_code)

token = r.json()['access_token']

while True:
    order = int(input("Enter '1' to see your database of songs \nEnter '2' to search for the artist \nEnter '3' to "
                      "delete your database \nEnter '4' to stop\n"))
    if order == 4:
        exit(0)

    if order == 1:
        ants = input("Which artist do you want to see from your database? ")
        resul = c.execute("SELECT song_name,release_date FROM top_songs WHERE artist_name = (?)", (ants,))
        records = c.fetchall()
        if len(records) == 0:
            print("Sadly there are not any songs in your database by this artist")
        else:
            print(*records, sep="\n")

    if order == 2:
        artist_name = input("Enter the artist: ")

        search_url = f"https://api.spotify.com/v1/search?q={artist_name}&type=track&limit=10"
        headers = {
            "Authorization": "Bearer " + token
        }

        res = requests.get(url=search_url, headers=headers)
        check_status(r.status_code)
        result = res.json()

        # write into a database
        all_rows = []
        for track in result['tracks']['items']:
            row = (artist_name, track['name'], track['album']['release_date'])
            all_rows.append(row)

        c.executemany('INSERT INTO top_songs (artist_name,song_name,release_date) VALUES (?,?,?)', all_rows)
        conn.commit()

        second_order = int(input("Enter '1' to save the result as a json file \nEnter '2' to stop\n"))
        if second_order == 1:
            #write into a file as a json
            with open('data.txt', 'w') as outfile:
                json.dump(result, outfile, indent=4)
                print("Done!!!")
        else:
            pass

    if order == 3:
        c.execute("DELETE FROM top_songs")
        conn.commit()
        print("Your database has been cleared")
