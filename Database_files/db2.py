import mysql.connector
import sys 
import json
import ast

class Database:
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password="",  
                database='login'
            )
            self.mycursor = self.conn.cursor()
            print("Connected to the database")
        except mysql.connector.Error as e:
            print(f"Error connecting to MySQL: {e}")
            sys.exit(1)

    def register(self, name, email, password):
        try:
            # Check if the user already exists
            check_user_query = "SELECT * FROM `users` WHERE `email` = %s"
            self.mycursor.execute(check_user_query, (email,))
            existing_user = self.mycursor.fetchone()

            if existing_user:
                print("User already exists")
                return -2
            else:
                # Insert the user if they don't exist
                insert_query = "INSERT INTO `users` (`user_id`, `name`, `email`, `password`) VALUES (NULL, %s, %s, %s)"
                insert_values = (name, email, password)
                self.mycursor.execute(insert_query, insert_values)
                self.conn.commit()
                print("Data inserted successfully")
                return 1
        except mysql.connector.Error as e:
            print(f"Error inserting data: {e}")
            return -1


    def login(self, email, password):
        try:
            sql = "SELECT * FROM users WHERE email = %s AND password = %s"
            values = (email, password)
            self.mycursor.execute(sql, values)
            
            data = self.mycursor.fetchall()
            if data :
                print("login successfull")
                d = data[0]
                return d
            else:
                print("Login Failed, Invalid email/password")
                return None
        except mysql.connector.Error as e:
            print(f"Error searching data: {e}")
            sys.exit(1)
       

     
    def movie_search(self, name):
        try:
            sql = "SELECT * FROM `movie` WHERE `title` LIKE %s LIMIT 1 "
            name_pattern = f"%{name}%"
            self.mycursor.execute(sql, (name_pattern,))
            
            data1 = self.mycursor.fetchall()[0]
            if data1:
                return data1
            else:
                return None
        except mysql.connector.Error as e:
            print(f"Error searching data: {e}")
            return None



    
    def insert(self, movie_id, user_id):
        try:
            check_user_query = "SELECT * FROM users WHERE user_id = %s"
            self.mycursor.execute(check_user_query, (user_id,))
            existing_user = self.mycursor.fetchone()
            
            if existing_user:
                check_movie_query = "SELECT * FROM movie WHERE movie_id = %s"
                self.mycursor.execute(check_movie_query, (movie_id,))
                existing_movie = self.mycursor.fetchall()
                
                

                genres = existing_movie[0][2]
                print(genres)

              
                if existing_movie:
                    sql = "INSERT IGNORE INTO relation_table (user_id, movie_id, genres) VALUES (%s, %s,%s )"
                    val = (user_id, movie_id,genres)
                    self.mycursor.execute(sql, val)
                    self.conn.commit()  
                    print("Data Inserted Successfully In Your Database")
                    return existing_user
                else:
                    print("Movie does not exist. Cannot insert in your database.")
                    return None
            else:
                print("Invalid user, User is not registered.")
                return None

        except mysql.connector.Error as e:
            print(f"Error insert data: {e}")
        
   
        
        
        

    def get_user_intrest(self, user_id):
        try:
            check_user_query = "SELECT DISTINCT m.genres FROM movie m JOIN relation_table r ON m.movie_id = r.movie_id WHERE r.user_id = %s ;"
            self.mycursor.execute(check_user_query, (user_id,))
            existing_user = self.mycursor.fetchall()
            if existing_user :
                print("Genres getting successfully") 
                return existing_user    
        except mysql.connector.Error as e:
            print(f"Error getting data: {e}")
            return -1

    
    
    def popular(self):
        try:
            check_user_query = "SELECT * from movie  ORDER BY vote_average DESC LIMIT 20;"
            self.mycursor.execute(check_user_query, )
            existing_user = self.mycursor.fetchall()
            if existing_user :
                print("Genres getting successfully") 
                result_list = []
                for row in existing_user:
                    movie_data = {
                        'movie_id': row[0],
                        'title': row[1],
                    
                        'vote_average': row[3],
                        # Add more columns as needed
                    }
                    result_list.append(movie_data)
                json_data = json.dumps(result_list, indent=2)
                with open('movies.json', 'w') as json_file:
                    json_file.write(json_data)

                return result_list
   
        except mysql.connector.Error as e:
            print(f"Error getting data: {e}")
            return -1







    def fetch_movie(self, uid):
        try:
            sql = "SELECT DISTINCT `movie_id` FROM `relation_table` WHERE `user_id` = %s"
            self.mycursor.execute(sql, (uid,))   
            data1 = self.mycursor.fetchall()
            
            if data1:
                movie_ids = [movie_id[0] for movie_id in data1] 
                
                # Use placeholders to prevent SQL injection
                placeholders = ', '.join(['%s' for _ in movie_ids])
                query = f"SELECT title FROM movie WHERE movie_id IN ({placeholders})"
                self.mycursor.execute(query, movie_ids)
                results = self.mycursor.fetchall()

                # Extract movie titles directly from the SQL query results
                movie_titles = [row[0] for row in results]
                
                # print(movie_titles)
                return movie_titles
            else:
                return None
        except mysql.connector.Error as e:
            print(f"Error searching data: {e}")
            return None   
            
           
           
            
    # def fetch_genres(self,movie_ids):
    #     try:
    #         placeholders = ', '.join(['%s' for _ in movie_ids])
    #         query = f"SELECT title FROM movie WHERE movie_id IN ({placeholders})"
    #         self.mycursor.execute(query, movie_ids)
    #         results = self.mycursor.fetchall()
    #         distinct_genres = set()

    #         for row in results:
    #             genres_str = row
    #             genres_list = ast.literal_eval(genres_str[0])  
    #             distinct_genres.update(genres_list)
    #             distinct_genres_list = list(distinct_genres)

    #         print(f"Distinct Genres: {distinct_genres_list}")
                            
      
    #     except mysql.connector.Error as e:
    #         print(f"Error searching data: {e}")
    #         return None
   

# a=Database()
# z=a.popular()
# print(z)