# This is a prototype code for calculating the signal conduction velocity in a H-reflex.


import matplotlib.pyplot as plt
import pandas as pd
import os
from os import listdir
from os.path import isfile, join



column_names = ['timestamp', 'channel 1', 'channel 2', 'channel 3', 'channel 4', 'channel 5',
                            'channel 6', 'channel 7', 'channel 8', 'channel 9', 'channel 10', 'channel 11',
                'channel 12', 'channel 13', 'channel 14', 'channel 15', 'channel 16', 'channel 17',
                            'channel 18', 'channel 19', 'channel 20', 'channel 21', 'channel 22', 'channel 23',
                'channel 24', 'channel 25', 'channel 26', 'channel 27', 'channel 28', 'channel 29',
                            'channel 30', 'channel 31', 'channel 32', 'channel 33', 'channel 34', 'channel 35',
                'channel 36', 'channel 37', 'channel 38', 'channel 39', 'channel 40', 'channel 41',
                            'channel 42', 'channel 43', 'channel 44', 'channel 45', 'channel 46', 'channel 47',
                'channel 48', 'channel 49', 'channel 50', 'channel 51', 'channel 52', 'channel 53',
                            'channel 54', 'channel 55', 'channel 56', 'channel 57', 'channel 58', 'channel 59'
                                        ]

    #function for reading and cleaning whole csv into the right format
def data_extract(filename: str):
    raw = pd.read_csv(filename)

    frame = []
    channels = 0
    for n in raw.index:


        #get the individual series
        series = raw.iloc[n,0]

        #make into list of strings
        list = series.split(";")

        #make list of strings into list of floats
        for index, number  in enumerate(list):
            list[index] = float(number)

        #add list to list of lists
        frame.append(list)
        channels = len(list)

        #account for files with fewer channels than 60.
        global column_names
        column_names = column_names[0:channels]

    #create a new dataframe with the extracted list of lists
    clean_data = pd.DataFrame(frame,
                              columns=column_names)
    clean_data_copy = clean_data.copy()
    clean_data_copy.set_index('timestamp',inplace=True, drop=True)
    pd.options.display.width = 0
    return clean_data

#mask the times from separate file to identify the individual stimulations and the proceeding signal.
def mask_times(data: pd.DataFrame, timestamps: pd.DataFrame):

    frames = []
    count = 0
    new_data = pd.DataFrame(columns=column_names)
    for time in data['timestamp']:

        #check if the square wave is set high
        if timestamps[timestamps['timestamp'] == time].iloc[0,1] > 0.5:
            ide = timestamps.index[timestamps['timestamp'] == time][0]


            # new_data.loc[ide] = data.iloc[ide]
            for col in data.columns:

                new_data.loc[ide,col] = data.loc[ide,col]
            count = 1
        elif count == 1:
            frames.append(new_data)
            new_data = pd.DataFrame(columns=column_names)
            count = 0
        else:
            pass


    return frames

#filter out the dataframe within 20 ms of beginning of file - only required when looking for H reflex, since in high stimulus intensities a remaining M wave may be observed within 20ms and may affect H reflex reading. 
def twenty_ms(dataset: pd.DataFrame):  

    id = 0
    for n in dataset.index.to_list():

        #keep updating value for last timestamp untill it surpasses 20ms
        if dataset.loc[n][0] < dataset.iloc[0][0] + 0.02:
            id = n
        else:
            pass


    new = pd.DataFrame()
    new = dataset.loc[id:].copy()

    return new

#find the key values of the wave 
def find_keys(dataset):

    #blank dataframe
    keys = pd.DataFrame()

    #display full window
    pd.options.display.width = 0

    for n in list(dataset.columns):

        if n != 'timestamp':




            #max is defined by max peak, calculate by absolute value of negative peak
            dataset[n] = pd.to_numeric(dataset[n])
            peak_time = dataset['timestamp'][dataset[n].abs().idxmax()]
            peak = -(dataset[n].abs().max())


            # calculate latency from
            lat = peak_time - dataset['timestamp'].iloc[0]

            #filter for all timestamps after the max peak
            after = dataset[dataset['timestamp'] >peak_time][['timestamp',n]]

            if peak_time == dataset['timestamp'][dataset[n].idxmin()]:
                min_time = after['timestamp'][after[n].idxmax()]
                min = after[n].max()
            else:
                min_time = after['timestamp'][after[n].idxmin()]
                min = after[n].min()

            #filter for all timestamps between max and min peaks
            between = after[after['timestamp'] < min_time]

            #calculate mean and find timestamp closest
            mean = (peak + min) / 2
            estimates = between.iloc[(between[n] - mean).abs().argsort()[:1]]
            mean_estimate = estimates[n].iloc[0]
            mean_time = estimates['timestamp'].iloc[0]

            #calculate peak-peak amplitude
            amp = -peak + min



            #store in summary dataframe
            keys[n] = [peak_time, peak, min_time, min, mean_time, mean, mean_estimate, amp, lat]





    keys.rename(index= {0:"Peak Time", 1:"Peak Amp", 2:"Post-Peak Max Time", 3: "Post-Peak Max Amp", 4: "Est. Mean Time", 5: "Calculated Mean", 6: "Estimated Mean", 7:"Peak-Peak Amp", 8:"Latency"}, inplace=True)


    return keys


def find_velocity(dataset, distance: int, instance:int):

    #blank dataframe to store conduction velocities
    velocities = pd.DataFrame()
    inter_node = 0.012  # single differential!!!
    for n,val in enumerate(dataset.columns):

        if n != len(dataset.columns)-1:


            #enter into new dataframe
            name = str("[" + dataset.columns[n] + " - " +dataset.columns[n+distance] + "], "+str(instance))

            #if timestamp difference is not 0, calculate conduction velocity and store into dataframe.
            mama = 0
            meme= 0
            if ( dataset[dataset.columns[n]][0] - dataset[dataset.columns[n+distance]][0] ) !=0 :
                mama= inter_node * distance / -( dataset[dataset.columns[n]][0] - dataset[dataset.columns[n+distance]][0] )
            if ( dataset[dataset.columns[n]][4] - dataset[dataset.columns[n+distance]][4] ) !=0:
                meme = inter_node * distance / -( dataset[dataset.columns[n]][4] - dataset[dataset.columns[n+distance]][4] )
            velocities[name] = [mama,meme]

    velocities.rename(
        index={0: "Peak-Peak", 1: "Mean-Mean"}, inplace=True)

    new = velocities.transpose().copy()
    new.loc[str("Mean, "+ str(instance))] = [new["Peak-Peak"].mean(), new["Mean-Mean"].mean()]
    new.loc[str("Median, " + str(instance))] = [new["Peak-Peak"].median(), new["Mean-Mean"].median()]
    return new

def outputs(read_file: str,  keys = pd.DataFrame, finals = pd.DataFrame, ptp = pd.DataFrame, lat = pd.DataFrame, new_file = str):

    #open new folder for all files related to this
    try:
        os.mkdir(new_file)
    except:
        pass
    #open new or existing file and write metadata and minimum velocity, table of velocities.
    with open(new_file + '\\summary.txt', 'w') as f:
        f.write("Recording file: " + read_file)
        f.write("Timestamp file: " + str("Timestamp"+"\\"+read_file.replace('.csv','')+" ts.csv"))
        f.write("\nSignal format: Single differential" )

        f.write("\nCalculated conduction velocities:")
        f.write("\n" + str(finals))

        f.write("\nRaw Data")
        f.write("\n" + str(keys))

    finals.to_csv(new_file + '\\conduction velocity.csv')

    ptp.to_csv(new_file + '\\peak-peak amplitude.csv')

    lat.to_csv(new_file + '\\latency.csv')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    #folder to read files from:
    folder = "SD"

    #list the filenames in selected folder
    onlyfiles = [f for f in listdir(folder) if isfile(join(folder, f))]

    for n in onlyfiles:

        filename = n

        #timestamp files must follow this naming convension
        timestamps = str("Timestamp"+"\\"+filename.replace('.csv','')+" ts.csv")

        #check if it is mmax folder - checking for "Mmax"
        check = filename.find('Mmax')
        mmax = True
        if check < 0:
            mmax = False

        else:
            mmax = True



        data = data_extract(folder +"\\"+filename)
        times_clean = data_extract(timestamps)

        dataframes = mask_times(data, times_clean)

        count = 1

        #set empty dataframes for outputting
        all_keys = pd.DataFrame()
        all_finals = pd.DataFrame()
        all_ptp = pd.DataFrame()
        all_lat = pd.DataFrame()

        for dataframe in dataframes:

            if mmax == False:
                twenty = twenty_ms(dataframe)

            keys = find_keys(dataframe)
            all_keys = pd.concat([all_keys,keys])

            finals = find_velocity(keys,1,count)
            all_finals = pd.concat([all_finals,finals])

            all_ptp = pd.concat([all_ptp, keys.iloc[[7]]])
            all_ptp = all_ptp.rename(index = {"Peak-Peak Amp":str(count)})
            all_lat = pd.concat([all_lat,keys.iloc[[8]]])
            all_lat = all_lat.rename(index = {"Latency": str(count)})

            #iterate through
            count += 1


        #add mean and median for ptp and lat
        all_ptp.loc["Mean"] = [all_ptp['channel 1'].mean(),all_ptp['channel 2'].mean(),all_ptp['channel 3'].mean(),all_ptp['channel 4'].mean()]
        all_ptp.loc["Median"] = [all_ptp['channel 1'].median(),all_ptp['channel 2'].median(),all_ptp['channel 3'].median(),all_ptp['channel 4'].median()]

        all_lat.loc["Mean"] = [all_lat['channel 1'].mean(),all_lat['channel 2'].mean(),all_lat['channel 3'].mean(),all_lat['channel 4'].mean()]
        all_lat.loc["Median"] = [all_lat['channel 1'].median(),all_lat['channel 2'].median(),all_lat['channel 3'].median(),all_lat['channel 4'].mean()]



        #set name for file to be outputted
        name = "Analysis 2\\"+ filename

        #output
        outputs(filename,all_keys,all_finals,all_ptp, all_lat,name)

        column_names = ['timestamp', 'channel 1', 'channel 2', 'channel 3', 'channel 4', 'channel 5',
                        'channel 6', 'channel 7', 'channel 8', 'channel 9', 'channel 10', 'channel 11',
                        'channel 12', 'channel 13', 'channel 14', 'channel 15', 'channel 16', 'channel 17',
                        'channel 18', 'channel 19', 'channel 20', 'channel 21', 'channel 22', 'channel 23',
                        'channel 24', 'channel 25', 'channel 26', 'channel 27', 'channel 28', 'channel 29',
                        'channel 30', 'channel 31', 'channel 32', 'channel 33', 'channel 34', 'channel 35',
                        'channel 36', 'channel 37', 'channel 38', 'channel 39', 'channel 40', 'channel 41',
                        'channel 42', 'channel 43', 'channel 44', 'channel 45', 'channel 46', 'channel 47',
                        'channel 48', 'channel 49', 'channel 50', 'channel 51', 'channel 52', 'channel 53',
                        'channel 54', 'channel 55', 'channel 56', 'channel 57', 'channel 58', 'channel 59'
                        ]






