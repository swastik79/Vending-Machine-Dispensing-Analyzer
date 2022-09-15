#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 28 20:01:48 2022

@author: swastikmishra
"""

#Importing the libraries
import os 
import csv
import pandas as pd
import matplotlib.pyplot as plt


def choice(prompt): #Checks whether the i/p we provided is Y or N
    ch =''
    while True:
        ch = input(prompt).upper().strip()
        if ch in ('Y','N'):
            break
        else:
            print("Invalid choice, try again!")
    return ch
    
        
def ip(prompt):     #Checks whether the i/p we provided is an int
    while True:
        try:
            n = int(input(prompt).strip())
            if isinstance(n,int):
                break
        except:
            print("Invalid choice, try again!")
    return n


#preparing function for userinput for graph
def productDailySalesAnalysis():
    while True:
        year = str(input("please enter the year you are looking at: ")) #asking for userinut/their requirement for the report
        if (newsales['YYYY'].eq(year)).any() == True:   # to continually ask for year input if user input is not found within the csv (i.e. no records for the year)
         #print('found')
             year = year
             break
         
        else:
            print('year not found, please input a valid year')
            continue 

    while True:
        month = str(input("please enter the month you are looking at (in number i.e. 7 for Jul):  ")).strip().upper()
        monthstr = ['','JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']
        monthno = ['','1','2','3','4','5','6','7','8','9','10','11','12']
        month2digit = ['','01','02','03','04','05','06','07','08','09','10','11','12']  #in case user inputs month in various format, even with prompts
        if month in monthstr:
            month = monthstr.index(month)  #looking out for the index
            break
            
        elif month in monthno :
            month = monthno.index(month)
            break
        
        elif month in month2digit:
            month = month2digit.index(month)
            break
        
        else:
            print('month that has been input is not valid')
            continue
        
            if (newsales['MM'].eq(month)).any() == True:
                #print('found')
                month= month
                break
            else:
                print('month not found, please input a valid month')
                continue
     
    while True:   
         productID = str(input("please enter the product ID you are looking at (e.g.S010): ")).upper().strip()
         if (newsales['Product_ID'].eq(productID)).any() == True: #similar to year input, to ask user continually if the input is not found within the csv
            #print('found')
            productID=productID
            break
         else:
            print('Product ID not found, please input a valid ProductID')
            continue
     

    report(year,month,productID)

#preparing function for printing of sales chart: 

def report(year,month,productID):
        reportyrmth = (f'{month}/{year}')
        #print(reportyrmth)
        selected = newsales.loc[(newsales['Date'].str.contains(reportyrmth)) & (newsales['Product_ID'].str.contains(productID))] #to sieve out records that satisfy user inputs
        #print(selected.info())
        
        if selected.shape[0]> 0:
            report = selected.groupby('Date')['Quantity'].sum()
            report1 = report.plot.bar(width = 0.3, label = 'Daily Sales Quantity',align='center',ec='black', color = 'teal')
            plt.xlabel('Date of Sales')
            plt.ylabel('Quantity per Day')
            plt.legend(loc='upper right')
            plt.title(f'Daily Product Sales for {productID} in {reportyrmth}')
            axes = plt.gca()
            axes.yaxis.grid()
            plt.xticks(rotation = 50)
            for i in report1.patches:
                report1.annotate(str(i.get_height()), xy=(i.get_x()+0.15, i.get_height()),  ha='center', va='bottom' ) #formatting the value label
            plt.ylim(0,(8+selected.groupby('Date')['Quantity'].sum().max()))
            plt.show(report1)
            
            
            
        
        else:
            print(f'No sales record of {productID} in {month}/{year} found')
        
           





#this function edits summarySales.csv file with data from dispensing reports 
#and transfers processed dispensing reports from pending to complete folder
def processDailySales(date):
        new_dir= os.getcwd()+os.sep+"complete" 
        if not os.path.exists(new_dir):     # create new folder within the existing folder
                  os.mkdir(new_dir)               # new folder is created when it does not exist before
                  
        df2 = preViewSales(date)
        if not df2:
            return
        date_list = []
        for i in range(len(df2["Machine_ID"])):
            date_list.append((date[-2:]+"/"+date[4:6]+"/"+date[:4]))
        df2.update({'Date' : date_list})
        
    
         # get the data from summary,csv, pop out the existing record of date
         # append new record from pending files, df2
         
        df3 = {'Date' : [], 'Machine_ID' : [] , 'Product_ID' : [],  'Slot_ID' : [], 'Quantity' : []}
        try:
            with open("summarySales.csv",'r') as data:
                next(data) #skips the header line
                for line in csv.reader(data):
                        df3["Date"].append(line[0])
                        df3["Machine_ID"].append(int(line[1]))
                        df3["Product_ID"].append(line[2])
                        df3["Quantity"].append(int(line[4]))
                        df3["Slot_ID"].append(line[3].split(';'))
                    
        except:
            print("The file does not exist")
            
        for i in range(len(df3["Slot_ID"])):
            for j in range(len(df3['Slot_ID'][i])):
                if df3["Slot_ID"][i][j] == '': #removing blank slot id from df3
                    df3['Slot_ID'][i].pop(j) 
                else:
                    df3["Slot_ID"][i][j] = int(df3["Slot_ID"][i][j])
        for i in range(len(df3['Date'])):
            if df3['Date'][i][4] == '/':
                df3['Date'][i] = df3['Date'][i][:3]+"0"+ df3['Date'][i][3:] #changing date from 28/7/2022 to 28/07/2022
                
                
        #this loop pops out those old data from summarySales.csv filewhose date matches to the date of dispensing report
        #because latest dispensing report data for that date will replace the old data in csv file
        while date[-2:]+"/"+date[4:6]+"/"+date[:4] in df3["Date"]:
            index = df3['Date'].index(date[-2:]+"/"+date[4:6]+"/"+date[:4])
            df3["Machine_ID"].pop(index)
            df3["Slot_ID"].pop(index)
            df3["Product_ID"].pop(index)
            df3["Quantity"].pop(index)
            df3["Date"].pop(index)
            
        df3['Date'].extend(df2['Date'])
        df3['Machine_ID'].extend(df2['Machine_ID'])
        df3['Product_ID'].extend(df2['Product_ID'])
        df3['Slot_ID'].extend(df2['Slot_ID'])
        df3['Quantity'].extend(df2['Quantity'])
        
        # format the slotid from int to string
        for i in range(len(df3["Slot_ID"])):
            for j in range(len(df3["Slot_ID"][i])):
                df3['Slot_ID'][i][j] = str(df3['Slot_ID'][i][j])
            
        for i in range(len(df3["Slot_ID"])):
            df3['Slot_ID'][i] = ';'.join(df3['Slot_ID'][i]) #joining the slots with ';' to write into csv file
            
        # output df3 into csv file
        with open("summarySales.csv", "w",newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(list(df3.keys()))
            writer.writerows(zip(*df3.values()))    
            
        
        # select the files fit with the input date               
        files = os.listdir('pending')
        files_list = []
        for i in files:
            if date in i:
                files_list.append(i)
            # transfer the files to complete folder
        for i in files_list:
            current_loc = os.getcwd()
            
            os.rename(f"{current_loc}/pending/{i}", f"{new_dir}/{i}")
      
       
#this function shows a table of dispensed products from different machines on a particular date
def preViewSales(date):
        files = os.listdir('pending')
        files_list = data = []
        df1 = {'Machine_ID' : [] , "Product_ID" : [], "Quantity" : [], "Slot_ID" : []}
        
    # select the pending files which have the input date
    # store the qualified ones in a list
        for i in files:
            if date in i:
                files_list.append(i)
        if files_list==[]:
                files_complete=os.listdir("complete")
                complete_list=[]
                for d in files_complete:
                    if date in d:
                        complete_list.append(d)
                if complete_list!=[]:
                    print("Files of the day have been processed")
                else:
                    print("Files not Found")
        else:
            #open the file in list by order, 
            for eachFile in files_list:
                try:
                    eachFile_path = os.getcwd()+os.sep+"pending"+os.sep+eachFile
    # within the file, read each line to extract machineid,slotid,quantity
    # store the extracted values in dictionary df1
                    with open(eachFile_path,"r") as file_pointer:
                        data = file_pointer.readlines()
                        data = data[1:] #jump the first line
                    
                        for each in data:
                            t, s, q = [x.strip() for x in each.split(",")]
                            index_ = eachFile.index('_')
                            df1["Machine_ID"].append(int(eachFile[1:index_]))
                            df1["Slot_ID"].append(int(s))
                            df1["Quantity"].append(int(q))
                except FileNotFoundError:
                    print(eachFile,"File is missing or it has already been processed!")
        
        # extract each productid from df by each pair of slotid, machineid in df1       
            for i in range(len(df1["Machine_ID"])):
                for j in range(len(df["Machine_ID"])):
                    if df["Machine_ID"][j] == df1["Machine_ID"][i] and df["Slot_ID"][j] == df1["Slot_ID"][i]:
                        df1["Product_ID"].append(df["Product_ID"][j])
                        
                    
        # the apir of machine_id and product_id which exists in dispensing reports is put in the dictionary            
            df2 = {'Machine_ID' : [] , "Product_ID" : [],  "Slot_ID" : [],"Quantity" : []}
            uniq_mac = list(set(df1["Machine_ID"]))
            uniq_prod = list(set(df1["Product_ID"]))  
            for i in range(len(uniq_mac)):
                for j in range(len(uniq_prod)):
                    for k in range(len(df1["Machine_ID"])):
                        if df1["Machine_ID"][k] == uniq_mac[i] and df1["Product_ID"][k] == uniq_prod[j]:
                            df2["Machine_ID"].append(df1["Machine_ID"][k])
                            df2["Product_ID"].append(df1["Product_ID"][k])
                            break
        # the pair of machine_id and product_id which is formed above is used to generate corresponding quantity and slot values 
            for i in range(len(df2["Machine_ID"])):
                sum_q =0
                slot_list = []
                for j in range(len(df1["Machine_ID"])):
                    if df2["Machine_ID"][i] == df1["Machine_ID"][j] and df2["Product_ID"][i] == df1["Product_ID"][j]:
                        sum_q += df1["Quantity"][j]
                        slot_list.append(df1["Slot_ID"][j])
                df2["Slot_ID"].append(list(set(slot_list)))
                df2["Quantity"].append(sum_q)
                
            return df2       
        

    

#this function allows user to edit existing slots,add new slot, add new machine and delete existing slots and machine 
def addEditMachineProfile(df):
    
    mac_id = ip("Please enter a machine ID ")
    
    if mac_id in df["Machine_ID"]: #if user enters existing Machine ID
        print("Slot_ID","Product_ID")
        for i in range(len(df["Machine_ID"])):
            if df["Machine_ID"][i] == mac_id:
                print(df["Slot_ID"][i],"     ",df["Product_ID"][i])
                
        ch1 = choice("Do you want to make amendments to existing slots or add new slot? [Y/N] ")
        if ch1 == 'Y':
            sl = ip(f"Enter the slot of Machine_ID {mac_id} you want to edit or add ")
            
            flag = False #used to check if you want to edit existing slot or add new slot
            for i in range(len(df["Machine_ID"])):
                if df["Machine_ID"][i] == mac_id and df["Slot_ID"][i] == sl:
                    prod_new = (input("Enter the Product_ID you want to add "))
                    df["Product_ID"][i] = prod_new
                    print(f"You have amended the existing Slot_ID {sl} in Machine_ID {mac_id}!")
                    flag = True
            if flag == False:
                    print(f"You are about to add a new slot {sl} in Machine_ID {mac_id}")
                    df["Machine_ID"].append(mac_id)
                    df["Slot_ID"].append(sl)
                    prod_new = (input("Enter the Product_ID you want to add "))
                    df["Product_ID"].append(prod_new)
                    print(f"You have added a new Slot_ID {sl} to Machine_ID {mac_id} ")
                    
        
        
    else: #if user enters a new Machine ID
        print("This is a new machine!")
        
        ch1 = choice("Do you want to add new slots? [Y/N]")
        if ch1 == 'Y':
            sl = ip(f"Enter the slot of Machine_ID {mac_id} you want to add ")
            df["Machine_ID"].append(mac_id)
            df["Slot_ID"].append(sl)
            prod_new = (input("Enter the Product_ID you want to add "))
            df["Product_ID"].append(prod_new)
            print(f"You have added a new Slot_ID {sl} to the new  Machine_ID {mac_id} ")
            
    #This section contains code for whether the user wants to delete existing slots    
    ch1 = choice("Do you want to delete any existing slots? [Y/N]")
    if ch1 == 'Y':
        n = ip("Enter the no of slots you want to delete ")
        for i in range(n):
            sl_del = ip(f"Enter the Slot_ID of Machine_ID {mac_id} that you want to delete ")
            
            flag = False
            for i in range(len(df["Machine_ID"])):
                if df["Machine_ID"][i] == mac_id and df["Slot_ID"][i] == sl_del:
                    df["Machine_ID"].pop(i)
                    df["Slot_ID"].pop(i)
                    df["Product_ID"].pop(i)
                    print(f"You have deleted the Slot_ID {sl_del} from Machine_ID {mac_id}")
                    flag = True
                    break
            if flag == False:
                print("This slot doesn't exist, try again!")
                i -= 1
            
    
    #This section contains code for whether the user wants to delete existing machine profile    
    ch1 = choice("Do you want to delete existing machine profile? [Y/N]")
    if ch1 == 'Y':
        n = ip("Enter the no of machines you want to delete ")
        for i in range(n):
            mac_del = ip("Enter the Machine_ID of the machine that you want to delete ")
            flag = False
            if mac_del in df["Machine_ID"]:
                while mac_del in df["Machine_ID"]:
                    index = df["Machine_ID"].index(mac_del)
                    df["Machine_ID"].pop(index)
                    df["Slot_ID"].pop(index)
                    df["Product_ID"].pop(index)
                    
                print(f"You have deleted the Machine_ID{mac_id}")
                        
            else:
                print("This machine doesn't exist, try again!")
                i -= 1
        
    
def menu():
    while True:
        menuItems = """
                ***** Vending Machine Manager *****
                    1. Add/Edit Machine Profile
                    2. Pre-view Sales
                    3. Process daily sales
                    4. Product Daily Sales Analysis
                    Q. Quit
                    """

        print(menuItems)
        choice = input("Please choose one of the above options...").upper().strip()
        try:
            if choice in ['1','2','3','4','Q']:
                return choice
            else:
                raise Exception
        except:
            print ("Invalid selection ....")



    
if __name__ == "__main__":
    
    while True:
    
        df = {"Machine_ID" : [], "Slot_ID" : [], "Product_ID" : []}
        try:
            with open("master.txt", "r") as file_pointer:
                for each in file_pointer:
                    m, s, p = [x.strip() for x in each.split(",")]
                    df["Machine_ID"].append(int(m))
                    df["Slot_ID"].append(int(s))
                    df["Product_ID"].append(p)
        except:
               print("The file does not exist!")
        
        
        
        ch = menu()
        if ch == '1': #this option should only be run after all the dispensing reports have been processed from pending to complete folder
            files = os.listdir('pending')
            files_list = []
            for i in files:
                files_list.append(i)
            if not files_list:  # if dispensing reports are in pending folder then cant run this option      
                addEditMachineProfile(df)
                with open('master.txt', 'w') as f:
                    for i in range(len(df["Machine_ID"])):
                        f.write(f"{df['Machine_ID'][i]},{df['Slot_ID'][i]},{df['Product_ID'][i]}\n")
            else:
                print("Please process all the daily dispensing reports first!")
                
            
        if ch == '2':
           while True:
               date = input("Please enter the date in [YYYY-MM-DD] format for which you want to see pre-sales report ")
               if "-" in date:
                   date = date.replace("-","")
               if "/" in date:
                   date = date.replace("/","")
               try:
                   if isinstance(int(date[:4]),int) and isinstance(int(date[4:6]),int) and isinstance(int(date[-2:]),int):
                        break
               except:
                   print("You have entered an invalid date!")
                   
           df2 = preViewSales(date)
           if df2: 
               print("Machine_ID","Product_ID","Quantity","Slot_ID")
               for i in range(len(df2["Machine_ID"])):
                   print(df2["Machine_ID"][i],'\t\t  ',df2["Product_ID"][i],'\t\t',df2["Quantity"][i],'\t\t',str(df2["Slot_ID"][i])[1:-1])
           
        
        if ch == '3':
            while True:
                date = input("Please enter the date in [YYYY-MM-DD] format for which you want to process pre-sales report ")
                if "-" in date:
                   date = date.replace("-","")
                if "/" in date:
                   date = date.replace("/","")
                try:
                    if isinstance(int(date[:4]),int) and isinstance(int(date[4:6]),int) and isinstance(int(date[-2:]),int):
                        break
                except:
                    print("You have entered an invalid date!")
            processDailySales(date)
            
            
        if ch == '4':
            
            cols = ['Date','Machine_ID','Product_ID','Slot_ID','Quantity']
            
            #reading in csv, preparing dataframe for ease of extraction based on user input
            in_data = pd.read_csv('summarySales.csv') #assuming the csv file from the previous option is named sumamry as in example file
            sales = pd.DataFrame(in_data)
            sales.columns = cols #Renaming the columns to make it similar to columns in other options
            #print(sales)
            
            sales['YYYY'] = sales['Date'].str.strip().str[-4:] #to get YYYY & MM for matching with user input later
            sales['MM'] = sales ['Date'].str.strip().str[3:4]
            newsales = sales
            #newsales.dtypes
            
            productDailySalesAnalysis()

            
            
        if ch == 'Q':
            print("Program ends now!")
            break
          
