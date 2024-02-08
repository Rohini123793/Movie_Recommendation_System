import pickle
import pandas as pd
import requests
from flask import Flask, jsonify, request
from db2 import Database
from flask_cors import CORS

movie_dict = pickle.load(open('mov_dict11.pkl', 'rb'))
similarity = pickle.load(open("simil11.plk", "rb"))
movies = pd.DataFrame(movie_dict)

db= Database()

app = Flask(__name__)
CORS(app)

@app.route ('/register1', methods = ['POST'])

def register(): 
    try:
        data = request.get_json()
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        
        if name and email and password:
            response = db.register(name, email, password)
            if response == 1:
                return jsonify({"message": "Registration successful"}), 200
            elif response == -2:
                return jsonify({"message": "User Already Exist"}), 200
        else:
            missing_fields = []
            if not name:
                missing_fields.append("name")
            if not email:
                missing_fields.append("email")
            if not password:
                missing_fields.append("password")
            
            return jsonify({"message": f"Missing fields: {', '.join(missing_fields)}"}), 400
            
    except Exception as e:
        return jsonify({"message": "Registration failed"}), 500



@app.route ('/login1', methods = ['POST'])
def login_user():
    try:
        data = request.get_json()
        
        email = data["email"]
        password = data["password"]
        password = str(password)
        
        response = db.login(email, password)
        if response[2] == email and response[3]== password:
            
            return jsonify({"message": "User Login successfull ","data":{
                "user_id":response[0],"name":response[1]
                }}), 200
        else:
            return jsonify({"message": "User does not exsist login Failed"}), 200
    except :
        return jsonify({"message": "Login failed. Invalid email/password"}), 500




@app.route ('/popularity', methods = ['GET'])

def popular1():
   
    popular = db.popular()
    if popular is not None:
        lis = []  
    
    for movie_info in popular:
        movie_id = movie_info['movie_id']  
        
        poster_url = requests.get("https://api.themoviedb.org/3/movie/{}?api_key=7c156447f829a2274f315f2a9d5e5b5f".format(movie_id))
        data = poster_url.json()
        res1 = 'https://image.tmdb.org/t/p/w185/' + data['poster_path']

        lis.append({
            "movie_id": str(movie_info['movie_id']),
            "title": str(movie_info['title']),
            "vote_average": str(movie_info['vote_average']),
            "poster": res1
        })
    else:
        print("No popular movies found in the database.")


    if lis:
        res = {
            "http_response_code": 200,
            "http_response_message": "OK",
            "response": {
                "ErrorCode": 0,
                "ErrorMessage": "Data Found",
                "total": 5,
                "data":lis
            }
        }
    else:
        res = {
        "http_response_code": 200,
        "http_response_message": "OK",
        "response": {
            "ErrorCode": 0,
            "ErrorMessage": "Data not Found",
            
        }
    }
        
    return jsonify(res)
    



 
@app.route ('/recommend', methods = ['GET'])

def hello():
    movie = request.args.get('name')
    uid=request.args.get("user_id")
    
    mov = db.movie_search(movie)
    if mov is not None:
        movie_id = mov[0]
        response = db.insert(movie_id, uid)
       
    else:
        print(f"The movie '{movie}' was not found in the database.")
    uid = int(uid)
    lisst = []
    if mov and response is not None:
        if response[0] == uid:
            filtered_movies = movies[movies['title'].str.contains(movie, case=False)]
            if not filtered_movies.empty:
                movie_index = filtered_movies.index[0]
                distances = similarity[movie_index]
                movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
                    
                for i in movie_list:
                    movie_id = movies.iloc[i[0]].movie_id
                    poster_url = requests.get("https://api.themoviedb.org/3/movie/{}?api_key=7c156447f829a2274f315f2a9d5e5b5f".format(movie_id))
                    data = poster_url.json()
                    res1 = 'https://image.tmdb.org/t/p/w185/' + data['poster_path']
                    lisst.append(
                        {"movie_id": str(movies.iloc[i[0]].movie_id), "title": str(movies.iloc[i[0]].title), "genres": str(movies.iloc[i[0]].genres),
                        "poster": res1})
            else:
                print(f"No movies found matching '{movie}' in the database.")
                return "No movies found matching the query.", 404
    
    
    if lisst:
        res = {
            "http_response_code": 200,
            "http_response_message": "OK",
            "response": {
                "ErrorCode": 0,
                "ErrorMessage": "Data Found",
                "total": 5,
                "data":lisst 
            }
        }
    else:
        res = {
        "http_response_code": 200,
        "http_response_message": "OK",
        "response": {
            "ErrorCode": 0,
            "ErrorMessage": "Data not Found",
            
        }
    }
        
    return jsonify(res)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000,debug = True)
        
        

    
