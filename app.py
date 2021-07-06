import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template
import pickle
import spotipy
import spotipy.util as util
import requests


app = Flask(__name__)
bc = pickle.load(open('model.pkl', 'rb'))


def get_id(track_name: str, token: str) -> str:
    headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token,
    }
    params = [
    ('q', track_name),
    ('type', 'track'),
    ]
    try:
        response = requests.get('https://api.spotify.com/v1/search', 
                    headers = headers, params = params, timeout = 5)
        json = response.json()
        first_result = json['tracks']['items'][0]
        track_id = first_result['id']
        return track_id
    except:
        return None

def get_features(track_id: str, token: str) -> dict:
    sp = spotipy.Spotify(auth=token)
    try:
        features = sp.audio_features([track_id])
        return features[0]
    except:
        return None

username = '13drm60sjnzr1ckmvqo0ealiz'
client_id ='3e6e06b723204e5c9e741db2ae2fd0e8'
client_secret = '574c497b18814610ba2a0f6a12942086'
redirect_uri = 'http://localhost:7777/callback'
scope = 'user-read-recently-played'

token = util.prompt_for_user_token(username=username, scope=scope, client_id=client_id,client_secret=client_secret,redirect_uri=redirect_uri)
#print(token)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict',methods=['POST'])
def predict():
    '''
    For rendering results on HTML GUI
    '''
    #int_features = [int(x) for x in request.form.values()]
    #final_features = [np.array(int_features)]
    text = request.form['text']
    #processed_text = text.upper()
    
    spotify_id = get_id(text, token)
    song_features = get_features(spotify_id, token)
    print(song_features)
    res = {key: song_features[key] for key in song_features.keys() 
                               & {'acousticness','danceability','liveness','loudness','speechiness'}}
    k={}
    for i in res.keys():
        k[i]=[res[i]]
    df=pd.DataFrame(k) 
    print(df)
    
    output = bc.predict(df)
    

    return render_template('index.html', prediction_text='It seems like you are {}'.format(output[0]))

if __name__ == "__main__":
    app.run(debug=True)