import os
import numpy as np
import pandas as pd
import math
import heapq

matrix_data_disk = None
matrix_data_mem = None
database = None
num_users = 0
num_medium = 0

""" 
load_data() is responsible for loading training data from the disk. 

If loaded for the first time, then it will process the data to store in a 
userID vs mediumID format.
If not loaded for the first time, then it will simply load the data from the
disk.
"""
def load_data(app, medium = ""):
    global matrix_data_disk
    # Handle error-checking here.
    medium_list = []
    medium_list.append("movie")
    medium_list.append("book")
    medium_list.append("anime")

    if(medium not in medium_list):
        print(f"{medium} is not a valid medium to train on")
        return
    elif(not os.path.isfile(f"data/{medium}_ratings.csv")):
        print(f"{medium} training data is missing")
        return
    with app.app_context():
        matrix_data_disk = pd.read_sql('rating', database.engine)

    matrix_data_disk = matrix_data_disk[1:]

    matrix_data_disk.loc[:, "user_id"] -= 1
    matrix_data_disk.loc[:, f"{medium}_id"] -= 1
    
""" 
store_data() is responsible for storing the dataframe into a .csv to be accessed
at some other time.
TODO: matrix_data_disk can also contain predicted values for the user. Need to wipe those
before writing back.
"""
def store_data(medium = ""):
    global matrix_data_disk

    # Handle error-checking here.
    medium_list = []
    medium_list.append("movie")
    medium_list.append("book")
    medium_list.append("anime")

    #TODO: Need to handle bug where the medium that is edited can be stored as the csv for another medium
    matrix_data_disk.to_csv(f"data/{medium}_ratings")
    return

"""
sparsify() is responsible for converting the .csv file in the data into a userID-mediumID rating
matrix.
"""
def sparsify(medium = ""):
    
    global num_users, num_medium, matrix_data_mem

    #Need to increment by 1 because data is 1-indexed
    num_users = max(matrix_data_disk.get("user_id")) + 1
    num_medium = max(matrix_data_disk.get(f"{medium}_id")) + 1
    
    # We are using -1 to represent a "no-rating"
    matrix_data_mem = np.ones((num_users, num_medium)) * -1
    
    matrix_data_mem[(matrix_data_disk.loc[:, "user_id"].values)[:], (matrix_data_disk.loc[:, f"{medium}_id"].values)[:]] = (matrix_data_disk.loc[:, "rating"].values)[:]
    return



"""
add_user() is responsible for adding new users to the recommendation matrix.
"""
def add_user():
    num_users += 1
    matrix_data_mem.append(np.ones(num_medium) * -1)
    return


""" 
alter_matrix_data_mem() is responsible for indexing into the dataframe and then changing rating values
given a specific user_id, for a specific medium_id, with a specific rating.
"""
def alter_matrix_data_mem(user_id, medium_id, rating):
    
    if(user_id < 0 or user_id > num_users):
        print("userId is invalid")
        return
    elif(medium_id < 0 or medium_id > num_medium):
        print("mediumId is invalid")
        return
    elif(rating < 0 or rating > 5):
        print("rating is invalid")
        return

    matrix_data_mem[user_id + num_users][medium_id] = rating

    return

""" 
similarity() is responsible for calculating the Pearson's Correlation Coefficient between two users
to compare how similar their ratings on the same movies are.
"""
def similarity(user_a):

    #Create the set of common movies between user_a and user_b
    
    common_matrix = np.logical_and(np.repeat(np.array([matrix_data_mem[user_a], ]), num_users, axis=0) > 0, matrix_data_mem > 0)
    
    common_matrix = common_matrix.astype(np.int32)
    
    common_a = np.multiply(np.repeat(np.array([matrix_data_mem[user_a], ]), num_users, axis=0), common_matrix)
    common_b = np.multiply(matrix_data_mem, common_matrix)
    
    #Creating the matrices that hold the average ratings on the set of all common mediums
    a_average_rating = np.sum(common_a, axis = 1) / np.sum(common_matrix, axis = 1)
    b_average_rating = np.sum(common_b, axis = 1) / np.sum(common_matrix, axis = 1)
    
    a_difference = np.repeat(np.array([a_average_rating, ]).T, num_medium, axis = 1) - common_a
    a_difference = np.multiply(a_difference, common_matrix)
    
    b_difference = np.repeat(np.array([b_average_rating, ]).T, num_medium, axis = 1) - common_b
    b_difference = np.multiply(b_difference, common_matrix)

    #Calculating the covariance and the standard deviation needed for the Pearson Correlation Coefficient
    covariance_array = np.sum(np.multiply(a_difference, b_difference), axis = 1)
    a_std_dev = np.sum(np.square(a_difference), axis = 1)
    b_std_dev = np.sum(np.square(b_difference), axis = 1)


    return covariance_array / np.sqrt(np.multiply(a_std_dev, b_std_dev))
"""
calculate_average() is responsible for calculating the average rating that a user
gives for every movie that they have reviewed.
"""
def calculate_average(userId):
    sum = 0
    count = 0
    for rating in matrix_data_mem[userId]:
        if(rating > 0):
            sum += rating
            count += 1
    return sum/count

"""
predict() is responsible for predicting the rating that a user would give a certain
movie given what it knows about other users in the matrix_data_mem matrix.

"""
def predict(userId, mediumId, k, results):
    pq = []
    #Calculate similarity between all users and the given user.
    
    #Filter out all users who have not consumed mediumId
    
    for user, similarity_measure in enumerate(results):
        if(matrix_data_mem[user, mediumId] != -1):
            pq.append((abs(similarity_measure) * -1, user))
    #Sort via heapify for O(n) time complexity
    heapq.heapify(pq)

    collection = []
    for j in range(min(k, len(pq))):
        collection.append(heapq.heappop(pq))
    
    numerator = 0
    denominator = 0
    for j in range(min(k, len(collection))):
        numerator += (results[collection[j][1]]) * (matrix_data_mem[collection[j][1]][mediumId] - calculate_average(collection[j][1]))
        denominator += abs(results[collection[j][1]])
    
    
    return calculate_average(userId) + numerator/denominator


def return_prediction_list(userId, k, elements_to_return):
    results = similarity(userId)
    pq = []
    for movie in range(10):
        if(matrix_data_mem[userId, movie] == -1):
            prediction = predict(userId=userId, mediumId=movie, k=k, results=results)
            
            pq.append((prediction * -1, movie))
    heapq.heapify(pq)
    returnList = []
    for i in range(elements_to_return):
        returnList.append(pq[i][1])
    return returnList

def start_up(db, app):
    global database
    database = db
    load_data(app, "movie")
    sparsify("movie")

def main():
    load_data("movie")
    sparsify("movie")
    return_prediction_list(0)
if __name__ == "__main__":
    main()