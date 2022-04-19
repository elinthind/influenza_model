
#########################################
#import libs
import os
import glob

import numpy as np
import pandas as pd
#########################################

#Grab path names for each county

state_path = r'C:\Users\Jennings\OneDrive\Desktop\Capstone_Data\Alaska'
counties = os.listdir(state_path) 
county_paths = []

for i in range(len(counties)):
    county_paths.append(state_path + '\\' + str(counties[i]))

#########################################

#set up data structures

#We want a square grid of latitudes and longitudes
lats = np.arange(51, 188) #for just Alaska
# lats = np.arange(33, 95) #for just Arkansas
longs = lats

#This is the array where we will store our travel data
BigGuy = np.zeros((len(lats), len(longs), len(lats), len(longs)))
#The indices for this are [house_lat_box, house_long_box, work_lat_box, work_long_box]

#########################################

#define the box function, returns the lat/long "box" that an ID belongs to
def box(id, coords, lat, long):
  """identifies the 'box' in the latitude/longitude grid that an ID belongs to"""
  boxed_ids = np.zeros_like(coords)

  #iterate through each 'row' (1 row is 1 location)
  for x in range(len(id)):
    lat_index = long_index = 0

  #the biggest coordinate that our value is bigger than is our coordinate
    for i in range(len(lat)):
      if coords[x,0] > lat[i]:
        lat_index = i
      
      if coords[x,1] > long[i]:
        long_index = i
  
    boxed_ids[x, 0] = lat_index
    boxed_ids[x, 1] = long_index

  boxed_ids = boxed_ids.astype(int)
  return boxed_ids


#########################################
#define how to iterate through a single county, count the travel
def SingleCounty(path, MasterArray):
    """Runs through a single county, adds the travel to the master array"""
    os.chdir(path)
    files = glob.glob('*.txt')
    #for reference, in each county folder, here are the files:
    #['gq.txt', 'gq_people.txt', 'hospitals.txt', 'households.txt', 
    # 'METADATA.txt', 'people.txt', 'schools.txt', 'workplaces.txt']

    #we're sorting workplace data first, so we'll be referencing files[7]

    p_data = pd.read_csv(files[5], delimiter = '\t', header = 0)
    hh_data = pd.read_csv(files[3], delimiter = '\t', header = 0)
    w_data = pd.read_csv(files[7], delimiter = '\t', header = 0)
    s_data = pd.read_csv(files[6], delimiter = '\t', header = 0)
    #####################################################################

    #coordinates of places will always be (latitude, longitude)
    #the longitudes are given as negative values and that's annoying, so we just multiply by -1

    #find the box of each workplace
    w_ids = w_data.sp_id
    w_coords = np.stack((w_data.latitude, w_data.longitude*-1), axis = 1)
    w_boxes = box(w_ids, w_coords, lats, longs)

    #find the box of each school
    s_ids + s_data.sp_id
    s_coords = np.stack((s_data.latitude, s_data.longitude*-1), axis = 1)
    s_boxes = box(s_ids, s_coords, lats, longs)


    #Find the box of each household
    hh_ids = hh_data.sp_id
    hh_coords = np.stack((hh_data.latitude, hh_data.longitude*-1), axis = 1)
    hh_boxes = box(hh_ids, hh_coords, lats, longs)

    #find the box that each person lives in
    p_ids = p_data.sp_id #ids of people
    p_hhs = p_data.sp_hh_id #ids of each person's household
    p_boxes = np.stack((np.zeros_like(p_ids), np.zeros_like(p_ids)), axis = 1) #set up array to store people boxes
    idP_boxHH = np.stack((p_ids, p_boxes[:,0], p_boxes[:, 1]), axis =1) #Stands for People ids & HouseHold boxes

    #put each person in a box based on the box their house is in
    for i in range(len(p_ids)):
        p_boxes[i] = hh_boxes[np.where(hh_ids == p_hhs[i])]


    #find each person's workplace
    p_ws = p_data.work_id.to_numpy() #ids of each person's workplace
    #If a person does not have a workplace, their entry is 'X'
    #we need to change this to 0 so it can be an int
    p_ws[p_ws == 'X'] = 0 
    #we have to retype these as integers so that we can read them later
    p_ws = p_ws.astype('int64') 


   
    #find each person's school
    p_s = p_data.school_id.to_numpy() #ids of each person's school
    #If a person does not have a school, their entry is 'X'
    #we need to change this to 0 so it can be an int
    p_s[p_s == 'X'] = 0 
    #we have to retype these as integers so that we can read them later
    p_s = p_s.astype('int64') 

    for i in range(len(p_ids)):
        p_index = i
        w_index = np.where(w_ids == p_ws[i])
        s_index = np.where(w_ids == p_ws[i])
        
        #count work travel
        if p_ws[i] != 0:   #if the work id is 0, then that person does not have a workplace and should *not* be counted
            hh_lat = idP_boxHH[p_index, 1]
            hh_long = idP_boxHH[p_index, 2]
            w_lat = w_boxes[w_index, 0]
            w_long = w_boxes[w_index, 1]

            MasterArray[hh_lat, hh_long, w_lat, w_long] += 1
      
        #count school travel
        if p_s[i] != 0:   #if the school id is 0, then that person does not have a school and should *not* be counted
              hh_lat = idP_boxHH[p_index, 1]
              hh_long = idP_boxHH[p_index, 2]
              s_lat = s_boxes[s_index, 0]
              s_long = s_boxes[s_index, 1]

              MasterArray[hh_lat, hh_long, s_lat, s_long] += 1
      
    return MasterArray

#########################################

#actually run through each county, count the travel
for i in range(len(county_paths)):
    path = county_paths[i]
    SingleCounty(path, BigGuy)


#save this to a file
np.save(r'C:\Users\Jennings\OneDrive\Desktop\Capstone_Data\TravelMatrix', BigGuy)

#note: to load this file, just have
#loaded_array = np.load(r'C:\Users\Jennings\OneDrive\Desktop\Capstone_Data\TravelMatrix.npy')
