import os
import numpy as np
import pandas as pd
import math
import heapq

matrix_data_disk = None
matrix_data_mem = None

num_users = 0
num_medium = 0

""" 
load_data() is responsible for loading training data from the disk. 

If loaded for the first time, then it will process the data to store in a 
userID vs mediumID format.
If not loaded for the first time, then it will simply load the data from the
disk.
"""
def load_data(medium = ""):
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
    matrix_data_disk = pd.read_csv(f"data/{medium}_ratings.csv")
    
    matrix_data_disk.loc[:, "userId"] -= 1
    matrix_data_disk.loc[:, f"{medium}Id"] -= 1
    
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
    num_users = max(matrix_data_disk.get("userId")) + 1
    num_medium = max(matrix_data_disk.get(f"{medium}Id")) + 1
    
    # We are using -1 to represent a "no-rating"
    matrix_data_mem = np.ones((num_users, num_medium)) * -1
    
    matrix_data_mem[(matrix_data_disk.loc[:, "userId"].values)[:], (matrix_data_disk.loc[:, f"{medium}Id"].values)[:]] = (matrix_data_disk.loc[:, "rating"].values)[:]
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

    matrix_data_mem[user_id][medium_id] = rating

    return

""" 
similarity() is responsible for calculating the Pearson's Correlation Coefficient between two users
to compare how similar their ratings on the same movies are.
"""
def similarity(user_a, user_b):

    #Create the set of common movies between user_a and user_b


    common_list = np.logical_and(matrix_data_mem[user_a, :] > 0, matrix_data_mem[user_b, :] > 0)
    
    common_list = np.where(common_list > 0)[0]

    common_list = common_list.astype(np.int32)
    
    a_average_rating = np.average(matrix_data_mem[user_a, common_list[:]])
    b_average_rating = np.average(matrix_data_mem[user_b, common_list[:]])
    


    covariance = np.sum(np.multiply((a_average_rating - matrix_data_mem[user_a, common_list[:]]), (b_average_rating - matrix_data_mem[user_b, common_list[:]])))
    a_std_dev = np.sum(np.square((a_average_rating - matrix_data_mem[user_a, common_list[:]])))
    b_std_dev = np.sum(np.square((b_average_rating - matrix_data_mem[user_b, common_list[:]])))
    
    if(covariance == 0 or a_std_dev == 0 or b_std_dev == 0):
        return (np.dot(matrix_data_mem[user_a, common_list[:]], matrix_data_mem[user_b, common_list[:]])/
                (np.linalg.norm(matrix_data_mem[user_a, common_list[:]]) * 
                 np.linalg.norm(matrix_data_mem[user_b, common_list[:]])))
    

    return covariance/math.sqrt(a_std_dev * b_std_dev)
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
def predict(userId, mediumId, k):
    pq = []
    similarity_dictionary = {}
    #Calculate similarity between all users and the given user.
    for i in range(num_users):
        if(i == userId or matrix_data_mem[i][mediumId] == -1):
            continue

        sim_value = similarity(userId, i)

        similarity_dictionary[i] = sim_value
        pq.append((abs(sim_value) * -1, i))

    
    #Sort via heapify for O(n) time complexity
    heapq.heapify(pq)

    collection = []

    for j in range(k):
        collection.append(heapq.heappop(pq))
    
    numerator = 0
    denominator = 0
    for j in range(k):
        numerator += (similarity_dictionary[collection[j][1]]) * (matrix_data_mem[collection[j][1]][mediumId] - calculate_average(collection[j][1]))
        denominator += abs(similarity_dictionary[collection[j][1]])
    
    
    return calculate_average(userId) + numerator/denominator

def main():
    load_data("movie")
    sparsify("movie")

if __name__ == "__main__":
    main()