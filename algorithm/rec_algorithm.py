import os
import numpy as np
import pandas as pd
import math

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

def similarity(user_a, user_b):
    a_set , b_set, common_set = set(), set(), set()

    #Create the set of common movies between user_a and user_b

    #TODO: This for loop can be turned from an O(n^2) to an O(n) loop by merging loops
    for index, element in enumerate(matrix_data_mem[user_a]):
        if(element > 0):
            a_set.add(index)
    for index, element in enumerate(matrix_data_mem[user_b]):
        if(element > 0):
            b_set.add(index)

    

    for id in a_set:
        if(id in b_set and id != -1):
            common_set.add(id)

    

    a_average_rating = 0
    b_average_rating = 0
    
    for id in common_set:
        a_average_rating += matrix_data_mem[user_a, id]
        b_average_rating += matrix_data_mem[user_b, id]
    
    a_average_rating /= len(common_set)
    b_average_rating /= len(common_set)

    pcc_numerator = 0
    a_std_dev = 0
    b_std_dev = 0


    #TODO: Need to address bug where the denominator can resolve to 0.
    for id in common_set:
        pcc_numerator += (a_average_rating - matrix_data_mem[user_a, id])*(b_average_rating - matrix_data_mem[user_b, id])
        a_std_dev += (a_average_rating - matrix_data_mem[user_a, id]) ** 2
        b_std_dev += (b_average_rating - matrix_data_mem[user_b, id]) ** 2
    

    

    return pcc_numerator/math.sqrt(a_std_dev * b_std_dev)

def main():
    load_data("movie")
    sparsify("movie")
    print(similarity(0, 1))

if __name__ == "__main__":
    main()