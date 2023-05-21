from matplotlib import pyplot as plt
import numpy as np
import math
import statistics
import webbrowser
import time
import os
from PIL import Image
import glob

### Program graphs histogram of move times for rapid, blitz and bullet as well as animated slideshow for rapid if there are enough games.
### Clk required for full functionality. Emt will still produce something.
### If emt is desired, before running, load pgn into chessbase to automatically convert to emt.
### In the code below, look for a message on a block of code to indicated what to add / remove it you want to load a file the old way (emt)

### Steps before running:

### 1)  Manually enter user name(s) into the list immediatly below these notes. Case sensitive so it's best to copy and paste username off user's profile page.
### 2)  Set starting and ending dates. (Last month not opened. Last month for indexing purposes only.)
### 3)  Set whether you need to download the files (True / False).

###   Use "True" as the default option for hyperbullet. Use "False" as the default for everything else

### 4   Optional. set "notHyperBullet" to True if most bullet games are 1+0 or slower. Hyperbullet graphs are better with a shorter x axis.
### 5)  Optional. longBlitzOnly was for discarding 3+0 players in an attempt to find more cheaters. When set True if the most common blitz TC is 3+0 then the data is discarded (the blitz graph may have 1 game, but will oftne be empty)
### 6)  Optional. timeControlFilter will only graph the time control you set.
### 7)  Optional. rating filter must be set true before lowest/highest has an effect. When opponent's rating is lower than lowest the game is discarded. Same for higher than highest.
### 8)  Optional. If onlyWin or onlyLoss is set true, then all games that are not that result are ignored.

name_list = [
    
'Silveira23574894'

]


u_intYearStart = 2023
u_intMonthStart = 3

u_intYearEnd = 2023
u_intMonthEnd = 6 #end month not opened. For indexing only

download = False

notHyperBullet = True # default is true (when graphing 1+0 for example)

longBlitzOnly = False # default false. Discards ALL games of 3+0 players

timeControlFilter = False # default false
filterBTC = 600 # will only graph games with this Base Time Control (in seconds)
filterTI = 0 # will only graph games with this Time Increment (in seconds)

ratingFilter = False # default false
lowestRating = 0 #default 0
highestRating = 10000 #default 10k

# default false
onlyWin = False # when set true all games that are not a win are ignored
onlyLoss = False # when set true all games that are not a loss are ignored



###############################################################################################################
# code you shouldn't touch before running begins
###############################################################################################################

bulletDetail = False
animated = True

for z in range (len(name_list)):

    print("\n**************************\n***** " + name_list[z] + " *****\n**************************")
    print("Name number " + str(z + 1) + "\n")

    user_name = name_list[z]

    intYearStart = u_intYearStart
    intMonthStart = u_intMonthStart

    intYearEnd = u_intYearEnd
    intMonthEnd = u_intMonthEnd


    ########       #########
    ###### Functions  ######
    ########        ########

    def getColor(stringCopy):
        colorIndexBegin = stringCopy.find(user_name)#
        gameColor = stringCopy[colorIndexBegin - 7 : colorIndexBegin - 2]

        #if gameColor != "White" and gameColor != "Black":
        #    print("Error:  unexpected game color.")
        #    print("Game color is:  " + str(gameColor))
        #    print(stringCopy[0:1000])
        #    exit()
        return(gameColor)

    def getTimeControl(stringCopy):
        increment = 0
        
        timeControlIndex = stringCopy.find("TimeControl")
        timeControlIndex = stringCopy.find('"', timeControlIndex)
        timeControlIndexEnd = stringCopy.find('"', timeControlIndex + 1)
        timeControl = stringCopy[timeControlIndex + 1 : timeControlIndexEnd]

        nonIntIndex = -1
        for i in range(len(timeControl)):
            if not (timeControl[i].isdigit()):
                nonIntIndex = i
                break

        if timeControl.isdigit():
            return(timeControl, increment)

        elif timeControl[nonIntIndex] == '+':
            return(timeControl[:nonIntIndex], timeControl[nonIntIndex + 1:])

        elif timeControl[nonIntIndex] == '/':
            return("daily", "daily")

        else:
            return("non-standard", "non-standard")
            

    def getGameResult(stringCopy):
        resultIndexBegin = stringCopy.find('Result')
        resultIndexEnd = stringCopy.find(']' , resultIndexBegin)
        gameResult = stringCopy[resultIndexBegin + 8 : resultIndexEnd - 1]

        endOfGameIndex = stringCopy.find(gameResult, resultIndexEnd)

        if stringCopy.find("Termination", endOfGameIndex - 30, endOfGameIndex) != -1:
            endOfGameIndex = stringCopy.find(gameResult, endOfGameIndex + 1)

        return(gameResult, endOfGameIndex)


    def populateTimeListBlack(oneGameCopy, bD):
        timeList = []
        gameIncrement = 0
        bulletDetail = bD

        
        timeControlIndex = oneGameCopy.find("TimeControl")
        timeControlString = oneGameCopy[timeControlIndex : timeControlIndex + 20]

        if timeControlString.find('+') != -1:
            incIndexBegin = oneGameCopy.find('+')
            incIndexEnd = oneGameCopy.find('"' , incIndexBegin)
            gameIncrement = oneGameCopy[incIndexBegin + 1 : incIndexEnd]
            gameIncrement = int(gameIncrement)

        #
        timeIndexBegin = oneGameCopy.find('%')
        timeIndexEnd = oneGameCopy.find(']', timeIndexBegin)
        oneGameCopy = oneGameCopy[timeIndexEnd:]
        #

        while "emt" in oneGameCopy:
            timeIndexBegin = oneGameCopy.find('%')
            timeIndexBegin = oneGameCopy.find('%' , timeIndexBegin+1)
            timeIndexEnd = oneGameCopy.find(']', timeIndexBegin)
            clockTime = oneGameCopy[timeIndexBegin + 7 : timeIndexEnd]

            timeList.append(clockTime)

            oneGameCopy = oneGameCopy[timeIndexEnd:]

        while "clk" in oneGameCopy:
            
            timeIndexBegin = oneGameCopy.find('%')
            timeIndexEnd = oneGameCopy.find(']', timeIndexBegin)
            timeIndexBegin = oneGameCopy.find(':', timeIndexBegin)
            clockTime = oneGameCopy[timeIndexBegin + 1 : timeIndexEnd]

            timeList.append(clockTime)

            timeIndexOpponentBegin = oneGameCopy.find('%' , timeIndexBegin+1)
            timeIndexOpponentEnd = oneGameCopy.find(']' , timeIndexOpponentBegin)
            
            oneGameCopy = oneGameCopy[timeIndexOpponentEnd:]    

        while True:
            if len(timeList) == 0:
                return(timeList, gameIncrement)
            
            if timeList[len(timeList) - 1].find('emt') == -1 and timeList[len(timeList) - 1].find(user_name) == -1 and timeList[len(timeList) - 1].find('clk') == -1:
                break
            else:
                timeList = timeList[:-1]
        ### normal (non-bullet detail) code begin

        if bulletDetail == False:
            for i in range(len(timeList)):
                timeList[i] = timeList[i][0:5]
        ### normal (non-bullet detail) code end

        ### begin of bullet detail
        if bulletDetail == True:
            
            for i in range(len(timeList)):
                    if timeList[i].find('.') != -1:
                        seconds = int(timeList[i][3:5])*10 + int(timeList[i][6:7])
                        minute = seconds // 60
                        second = seconds % 60
                        if minute < 10:
                            s_minute = '0' + str(minute)
                        else:
                            s_minute = str(minute)
                        if second < 10:
                            s_second = '0' + str(second)
                        else:
                            s_second = str(second)

            
                        timeList[i] = s_minute + ':' + s_second

                    elif timeList[i].find('.') == -1:
                        seconds = int(timeList[i][3:5])*10
                        minute = seconds // 60
                        second = seconds % 60
                        if minute < 10:
                            s_minute = '0' + str(minute)
                        else:
                            s_minute = str(minute)
                        if second < 10:
                            s_second = '0' + str(second)
                        else:
                            s_second = str(second)
                        
                        timeList[i] = s_minute + ':' + s_second
                    
        ### end of bullet detail




            
        return(timeList, gameIncrement)

    def populateTimeListWhite(oneGameCopy, bD):
        timeList = []
        gameIncrement = 0
        bulletDetail = bD

        timeControlIndex = oneGameCopy.find("TimeControl")
        timeControlString = oneGameCopy[timeControlIndex : timeControlIndex + 20]

        if timeControlString.find('+') != -1:
            incIndexBegin = oneGameCopy.find('+')
            incIndexEnd = oneGameCopy.find('"' , incIndexBegin)
            gameIncrement = oneGameCopy[incIndexBegin + 1 : incIndexEnd]
            gameIncrement = int(gameIncrement)
        
        while "emt" in oneGameCopy:
            timeIndexBegin = oneGameCopy.find('%')
            timeIndexEnd = oneGameCopy.find(']', timeIndexBegin)
            clockTime = oneGameCopy[timeIndexBegin + 7 : timeIndexEnd]

            timeList.append(clockTime)

            timeIndexOpponentBegin = oneGameCopy.find('%' , timeIndexBegin+1)
            timeIndexOpponentEnd = oneGameCopy.find(']' , timeIndexOpponentBegin)
            
            oneGameCopy = oneGameCopy[timeIndexOpponentEnd:]

        while "clk" in oneGameCopy:
            
            timeIndexBegin = oneGameCopy.find('%')
            timeIndexEnd = oneGameCopy.find(']', timeIndexBegin)
            timeIndexBegin = oneGameCopy.find(':', timeIndexBegin)
            clockTime = oneGameCopy[timeIndexBegin + 1 : timeIndexEnd]

            timeList.append(clockTime)

            timeIndexOpponentBegin = oneGameCopy.find('%' , timeIndexBegin+1)
            timeIndexOpponentEnd = oneGameCopy.find(']' , timeIndexOpponentBegin)
            
            oneGameCopy = oneGameCopy[timeIndexOpponentEnd:]

        while True:
            if len(timeList) == 0:
                return(timeList, gameIncrement)
            
            if timeList[len(timeList) - 1].find('emt') == -1 and timeList[len(timeList) - 1].find(user_name) == -1 and timeList[len(timeList) - 1].find('clk') == -1:
                break
            
            else:
                timeList = timeList[:-1]

        ### normal (non-bullet detail) code begin

        if bulletDetail == False:
            for i in range(len(timeList)):
                timeList[i] = timeList[i][0:5]
        ### normal (non-bullet detail) code end

        ### begin of bullet detail
        if bulletDetail == True:

            
            for i in range(len(timeList)):

                    seconds = 0

                    if int(timeList[i][1:2]) > 0:
                        seconds += int(timeList[i][1:2])*600


                
                    if timeList[i].find('.') != -1:
                        
                        seconds += int(timeList[i][3:5])*10 + int(timeList[i][6:7])
                        minute = seconds // 60
                        second = seconds % 60
                        '''
                        if minute < 10:
                            s_minute = '0' + str(minute)
                        else:
                            s_minute = str(minute)
                        if second < 10:
                            s_second = '0' + str(second)
                        else:
                            s_second = str(second)
                        '''
                        s_minute = str(minute)
                        s_second = str(second)                 

            
                        timeList[i] = s_minute + ':' + s_second

                    elif timeList[i].find('.') == -1:

                        seconds += int(timeList[i][3:5])*10
                        minute = seconds // 60
                        second = seconds % 60
                        '''
                        if minute < 10:
                            s_minute = '0' + str(minute)
                        else:
                            s_minute = str(minute)
                        if second < 10:
                            s_second = '0' + str(second)
                        else:
                            s_second = str(second)
                        '''
                        s_minute = str(minute)
                        s_second = str(second)
                        
                        timeList[i] = s_minute + ':' + s_second

                    try:
                        tempVar = int(timeList[i][0:2])
                    except:
                        timeList[i] = "0" + timeList[i]
        ### end of bullet detail
            
        return(timeList, gameIncrement)

    def getTimeDifference(timeList, gameIncrement, bD):
        secondsList = []
        differenceList = []
        bulletDetail = bD

        for i in range(len(timeList)):
            moveMinute = int(timeList[i][0:2])
            moveSecond = int(timeList[i][3:5])
            secondsList.append((moveMinute * 60) + moveSecond)
                 
        if sum(secondsList[0:6]) > 150 and bulletDetail == False:
            secondsList.insert(0, secondsList[0] - gameIncrement)
            
            for i in range(len(secondsList)):
                secondsList[len(secondsList) - 1 - i] = secondsList[len(secondsList) - 2 - i] - (secondsList[len(secondsList) - 1 - i]) + gameIncrement
            
            secondsList = secondsList[1:]

        if sum(secondsList[0:6]) > 150 and bulletDetail == True:
            secondsList.insert(0, secondsList[0] - (gameIncrement * 10))

            for i in range(len(secondsList)):
                secondsList[len(secondsList) - 1 - i] = secondsList[len(secondsList) - 2 - i] - (secondsList[len(secondsList) - 1 - i]) + (gameIncrement * 10)
            
            secondsList = secondsList[1:]
            
        
        if len(secondsList) > 1 and bulletDetail == True and secondsList[1] < 0:
            while secondsList[1] < 0:
                secondsList[1] += 600

        
        return(secondsList) #rest of code refers to secondsList as timeDifference

    def parseOneGame(filterBTC, filterTI):

        timeList = []
        gameIncrement = 0
        filterBTC = str(filterBTC)
        filterTI = str(filterTI)

        #get color6
        gameColor = getColor(myString)

        if gameColor != "White" and gameColor != "Black":
            #print("Discarding:  unexpected game color.")
            gameResult, endOfGameIndex = getGameResult(myString)
    
            baseTimeControl = "non-standard"
            gameRating = -1
            return([], endOfGameIndex, baseTimeControl, gameRating)

        #get rating
        ratingIndexBegin = myString.find(str(gameColor) + 'Elo')
        gameRating = myString[ratingIndexBegin + 10 : ratingIndexBegin + 14]

        if '"' in gameRating:
            gameRating = gameRating[:-1]


        if gameRating.isdigit() == False:
            #print("Discarding:  unexpected game color.")
            gameResult, endOfGameIndex = getGameResult(myString)
            baseTimeControl = "non-standard"
            gameRating = -1
            return([], endOfGameIndex, baseTimeControl, gameRating)
            

        #get result and set end of game index
        gameResult, endOfGameIndex = getGameResult(myString)

        if (gameColor == "White" and gameResult == "1-0") or (gameColor == "Black" and gameResult == "0-1"):
            winOrLoss = "win"

        elif (gameColor == "Black" and gameResult == "1-0") or (gameColor == "White" and gameResult == "0-1"):
            winOrLoss = "loss"

        else:
            winOrLoss = "draw"

        #separate a single game
        oneGame = myString[0 : endOfGameIndex]
        oneGame = oneGame.replace("\n", "")

        if oneGame.find("Variant") != -1:
            #print("Discarding: Variant")
            baseTimeControl = 0
            return([], endOfGameIndex, baseTimeControl, gameRating)

        #get time control
        baseTimeControl, timeIncrement = getTimeControl(myString)

        baseTimeControl = str(baseTimeControl)
        timeIncrement = str(timeIncrement)

        #get opponent's rating and filter
        
        if gameColor == "White":
            opponentColor = "Black"
        else:
            opponentColor = "White"

        ratingIndexBegin = oneGame.find(str(opponentColor) + 'Elo')
        opponentRating = oneGame[ratingIndexBegin + 10 : ratingIndexBegin + 14]

        if '"' in opponentRating:
            opponentRating = opponentRating[:-1]

        if ratingFilter == True:
            if int(opponentRating) < lowestRating or int(opponentRating) > highestRating:
                return([], endOfGameIndex, baseTimeControl, gameRating)
        

        # time control filter

        if timeControlFilter == True:
            if baseTimeControl != filterBTC:
                return([], endOfGameIndex, baseTimeControl, gameRating)

            if timeIncrement != filterTI:
                return([], endOfGameIndex, baseTimeControl, gameRating)
                
        if not baseTimeControl.isdigit():
            #print("Discarding: " + baseTimeControl)
            baseTimeControl = 0 if baseTimeControl == "non-standard" else baseTimeControl
            return([], endOfGameIndex, baseTimeControl, gameRating)

        if oneGame.find('clk') == -1 and oneGame.find('emt') == -1:
            return([], endOfGameIndex, baseTimeControl, gameRating)

        baseTimeControl = int(baseTimeControl)
        timeIncrement = int(timeIncrement)

        # win / loss / draw filter

        if onlyWin == True:
            if winOrLoss != "win":
                return([], endOfGameIndex, baseTimeControl, gameRating)
                
        if onlyLoss == True:
            if winOrLoss != "loss":
                return([], endOfGameIndex, baseTimeControl, gameRating)

        #categorize games by time control

        if baseTimeControl + timeIncrement * 40 < 180:
            timeFormat = "Bullet"
            bulletTimeControlList.append(str(int(baseTimeControl / 60)) + " + " +str(timeIncrement))
            bulletDetail = True
            
        elif baseTimeControl + timeIncrement * 40 >= 180 and baseTimeControl + timeIncrement * 40 < 600:
            timeFormat = "Blitz"
            blitzTimeControlList.append(str(int(baseTimeControl / 60)) + " + " +str(timeIncrement))
            bulletDetail = False

        elif baseTimeControl + timeIncrement * 40 >= 600 and baseTimeControl + timeIncrement * 40 <= 1800:
            timeFormat = "Rapid"
            rapidTimeControlList.append(str(int(baseTimeControl / 60)) + " + " +str(timeIncrement))
            bulletDetail = False
            
        elif baseTimeControl + timeIncrement * 40 > 1800:

                

            return([], endOfGameIndex, baseTimeControl, gameRating)

        #populate time list ##################### WHITE TO BLACK  #######################
        if(gameColor == "White"):
            timeList, gameIncrement = populateTimeListWhite(oneGame, bulletDetail)

        if(gameColor == "Black"):
            timeList, gameIncrement = populateTimeListBlack(oneGame, bulletDetail)
        
        #populate difference list
        secondsList = getTimeDifference(timeList, gameIncrement, bulletDetail)

        return(secondsList, endOfGameIndex, timeFormat, gameRating) #rest of code refers to secondsList as timeDifference

    def mostFrequent(myListCopy):
        myDict = {}
        count = 0
        item = ''
        
        for i in reversed(myListCopy):
            myDict[i] = myDict.get(i, 0) + 1 #entry i = search for i, if it doesn't exist then return zero and then the + 1 means one more than that -- IOW this is keeping a running total. It seraches for an entry and sets it one higher
            if myDict[i] >= count :
                count, item = myDict[i], i

        #print(myDict)

        return(item)


    ########                 #########
    ###### raw data to myString ######
    ########                  ########


    ### Look for matching row. Add/remove three ' around this block depending on how you want to access files (download or manual)
    myString = ""
    bulletTimeControlList = []
    blitzTimeControlList = []
    rapidTimeControlList = []

    monthCounter = (((intYearEnd - intYearStart)*12) + (intMonthEnd - intMonthStart))

    monthCounter22 = 0
    while intYearStart != intYearEnd or intMonthStart != intMonthEnd:
        monthCounter22 += 1

        monthStart = "0" + str(intMonthStart) if intMonthStart < 10 else str(intMonthStart)
        yearStart = str(intYearStart)
        
        if download == True:
            url = 'https://api.chess.com/pub/player/' + user_name + '/games/' + str(intYearStart) + '/' + str(intMonthStart) + '/pgn'
            webbrowser.register('chrome',
                None,
                webbrowser.BackgroundBrowser("C://Program Files (x86)//Google//Chrome//Application//chrome.exe"))
            webbrowser.get('chrome').open(url)
            
            time.sleep(1.5)
            downloadStatus = "waiting"

            while downloadStatus == "waiting":
                try:
                    rawData = open('C:\\Users\\User\\Downloads\\ChessCom_' + user_name + '_' + yearStart + monthStart + '.pgn','r')
                    downloadStatus = "finished"
                except:
                    print("Waiting 5 more seconds")
                    time.sleep(5)
         
        rawData = open('C:\\Users\\User\\Downloads\\ChessCom_' + user_name + '_' + yearStart + monthStart + '.pgn','r')
        try:
            tempString = rawData.read()
            myString = myString + tempString
            print("Month number " + str(monthCounter22) + " -> " + "File size: " + str(len(tempString)))
        except:
            print("Warning: Bad data, discarding file " + user_name + yearStart + monthStart)
            pass

        rawData.close()
        
        intYearStart = intYearStart + 1 if intMonthStart == 12 else intYearStart
        intMonthStart = intMonthStart + 1 if intMonthStart < 12 else 1
        

    ### Look for matching row. Add/remove three ' around this block depending on how you want to access files (download or manual)
    '''
    rawData = open('C:\\Users\\User\\Downloads\\' + user_name + '.pgn','r')# use to open individual file
    myString = rawData.read()
    rawData.close()
    print("The original length is " + str(len(myString)))
    '''
    ### Look for matching row. Add/remove three ' around this block depending on how you want to access files (download or manual)
    clockList = []
    graphMe = []
    gameCounter = 0
    graphMeRapid = []
    graphMeBlitz = []
    graphMeBullet = []
    rapidCounter = 0
    blitzCounter = 0
    bulletCounter = 0

    rapidRatingList = []
    blitzRatingList = []
    bulletRatingList = []

    ########                                       #########
    ###### populating graphMe variables with myString ######
    ########                                       #########
    print("\nSorting games. This may take some time.\n")

    while len(myString) > 100:

        if longBlitzOnly == True:
            if mostFrequent(blitzTimeControlList) == '3 + 0':
                print("3+0 blitz was most common, discarding player")
                myString = []
                timeDifference = []
                break

        timeDifference, endOfGameIndex, timeFormat, gameRating = parseOneGame(filterBTC, filterTI)


        while len(timeDifference) == 0:

            myString = myString[endOfGameIndex:]
            timeDifference, endOfGameIndex, timeFormat, gameRating = parseOneGame(filterBTC, filterTI)
            
            
            if len(myString) <= 100:
                break

        try: # try block in case empty time list appears at end of string, needs to fall through the next while statement as well but can't take min of empty list
            
            while min(timeDifference) < 0:

                myString = myString[endOfGameIndex:]
                timeDifference, endOfGameIndex, timeFormat, gameRating = parseOneGame(filterBTC, filterTI)

                if len(myString) <= 100:
                    break

                #print("Warning: game discarded for neg values. Likely the player took more than 2 minutes for their first 4 moves triggering subtraction process in getTimeDifference function.")
        except:
            pass

        if timeFormat == 'Rapid':
            rapidCounter += 1
            for i in range(len(timeDifference)):
                graphMeRapid.append(timeDifference[i])
                rapidRatingList.append(gameRating)

        elif timeFormat == 'Blitz':
            blitzCounter += 1
            for i in range(len(timeDifference)):
                graphMeBlitz.append(timeDifference[i])
                blitzRatingList.append(gameRating)

        elif timeFormat == 'Bullet':
            bulletCounter += 1
            for i in range(len(timeDifference)):
                graphMeBullet.append(timeDifference[i])
                bulletRatingList.append(gameRating)

        elif timeFormat == "daily":
            pass

        else:
            #print("Warning: time Format (rapid/blitz/bullet) not recognized.")
            pass

        #make game list 1 game smaller
        myString = myString[endOfGameIndex:]


    ########                          #########
    ###### 3 graphs and some output data ######
    ########                           ########


    
    minRating = 10000
    maxRating = -1

    for i in range(len(rapidRatingList)):
        if int(rapidRatingList[i]) < minRating:
            minRating = int(rapidRatingList[i])

        if int(rapidRatingList[i]) > maxRating:
            maxRating = int(rapidRatingList[i])
        

    for k in range(3): # one loop for each graph type

        if k == 0:
            graphMe = graphMeRapid
            gameType = "Rapid"
            gameCounter = rapidCounter
            bulletDetail = False
            print("\n" + str(name_list[z]) + "'s rapid report:")

        if k == 1:
            graphMe = graphMeBlitz
            gameType = "Blitz"
            gameCounter = blitzCounter
            bulletDetail = False
            print("\n" + str(name_list[z]) + "'s blitz report:")
            
        if k == 2:
            graphMe = graphMeBullet
            gameType = "Bullet"
            gameCounter = bulletCounter
            bulletDetail = True
            print("\n" + str(name_list[z]) + "'s bullet report:")

        if len(graphMe) == 0:
            #print("Warning: no " + gameType + " graph")
            graphMe = [0, 1, 2, 3]

        print("Total games: " + str(gameCounter))
        print("Total moves: " + str(len(graphMe)))
        
        if k == 0 and len(rapidTimeControlList) != 0:
            print(mostFrequent(rapidTimeControlList) + " was the most common time control accounting for " + str(round(rapidTimeControlList.count(mostFrequent(rapidTimeControlList)) / len(rapidTimeControlList) * 100, 1)) + " percent.")
        elif k == 1 and len(blitzTimeControlList) != 0:
            print(mostFrequent(blitzTimeControlList) + " was the most common time control accounting for " + str(round(blitzTimeControlList.count(mostFrequent(blitzTimeControlList)) / len(blitzTimeControlList) * 100, 1)) + " percent.")
        elif k == 2 and len(bulletTimeControlList) != 0:
            print(mostFrequent(bulletTimeControlList) + " was the most common time control accounting for " + str(round(bulletTimeControlList.count(mostFrequent(bulletTimeControlList)) / len(bulletTimeControlList) * 100, 1)) + " percent.")
            

        meanValue = sum(graphMe) / len(graphMe)
        topValue = 0
        bottomValue = len(graphMe)

        for i in range(len(graphMe)):
            topValue += ((graphMe[i] - meanValue) ** 2)

        standardDeviation = (topValue / bottomValue) ** 0.5

        seventyPercent = 0
        sp = 0

        while seventyPercent < 0.65:
            seventyPercent += (graphMe.count(sp) / len(graphMe))
            sp +=1
        print(str(round(100 * seventyPercent,1)) + "% of moves lie within a " + str(sp) + " second window.")

        highest_bin = 1
        try:
            mode = statistics.mode(graphMe)
        except:
            #print('Warning: no mode, so mode is set = 2')
            mode = 2

        for i in range(len(graphMe)):
            if graphMe[i] == mode:
                highest_bin += 1

        if k == 0:
            rapidLambda = highest_bin / len(graphMe)

        for j in range (2): # once with pdf and once without
            pdf = False if j == 0 else True
            
            if pdf == True:

                Lambda = highest_bin / len(graphMe)
                start = -1
                stop = 60
                number = ((stop - start) * 10)
                mu = mode
                b = 1/(2 * highest_bin / len(graphMe))
                sigma = standardDeviation / 2

                pdf_x_axis = np.linspace(start, stop, number)
                pdf_y_axis = []

                for i in range(number):
                    pdf_y_axis.append(Lambda * math.exp(-Lambda * pdf_x_axis[i])) # definition of exponential pdf with lambda
                    #pdf_y_axis.append(  (1/(2*b))*(math.exp((abs(pdf_x_axis[i] - mu)/(-b))))  ) # definition of laplase function with b and mu
                    #pdf_y_axis.append(   (1/(sigma * math.sqrt(2*math.pi)))*(math.exp( -0.5 * ((pdf_x_axis[i] - mu)/(sigma)) ** 2  ))   ) #definition of standard normal pdf with mu and sigma
                    
                if bulletDetail == False:
                    plt.plot(pdf_x_axis, pdf_y_axis, color = 'r', linewidth = 3, label = "Exponential")
                
            if gameType == "Rapid":
                xLimit = 60
                binWidth = 1
            elif gameType == "Blitz":
                xLimit = 30
                binWidth = 1
            else:
                xLimit = 15
                binWidth = 1

                if bulletDetail == True:
                    xLimit = 30
                    if notHyperBullet == True:
                        xLimit = 60
                        
                

            redLine = "-red" if pdf == True else ""

            '''
            # trying some rayleigh

            rayAvg = statistics.mean(graphMe)
            raySigma = rayAvg / (math.pi/2)**0.5
            raySigma /= 10
            raySigma *= 1.2

            start = -1
            stop = 60
            number = ((stop - start) * 10)
            rayXAxis = np.linspace(start, stop, number)
            rayYAxis = []

            for i in range(number):
                rayYAxis.append((rayXAxis[i]/10)/10 * raySigma**2 * math.exp( -(rayXAxis[i]/10)**2 / 2*raySigma**2 ))

            if k == 2:
                plt.plot(rayXAxis, rayYAxis, color = 'r', linewidth = 3, label = "Rayleigh")
            '''
            
            
            plt.hist(graphMe, max(graphMe), width=binWidth, label = str(gameCounter) + ' Games \n' + str(len(graphMe)) + ' Moves', density = True)
            #plt.xscale('log')########################################
            plt.title(user_name + "'s " + gameType + " Games")
            plt.xlabel('Seconds')
            plt.ylabel('Frequency')
            plt.xlim(0, xLimit)
            

            if bulletDetail == True and pdf == True:
                plt.xlim(2, xLimit)
                plt.ylim(0,0.1)
            
            if pdf == True and bulletDetail == False:
                plt.ylim(0,1.1 * Lambda)
            plt.legend()

            if bulletDetail == True:
                plt.xlabel('Tenths of a Second')

            try:
                os.makedirs('C:/Users/User/Documents/Chess rating slideshow/' + str(user_name) + '/graphs')#
            except:
                pass

            plt.savefig('C:/Users/User/Documents/Chess rating slideshow/' + str(user_name) + '/graphs/' + gameType + redLine + '.png')#
            plt.close()
            print(gameType + " Figure saved.")

    ########                          #########
    ###### animated graph of rapid data  ######
    ########                           ########


    if animated == True:

        tempRatingGraph = []
        tempGraphMe = []
        picNumber = 100
        print("\nBuilding gif. Estimated time " + str(int(len(graphMeRapid) / 10000 * 7)) + " seconds.")
        
        try:
            os.makedirs("C:/Users/User/Documents/Chess rating slideshow/" + str(user_name) + '/pngs/')#
        except:
            pass


        rapidCounter = 1 if rapidCounter == 0 else rapidCounter
        movePerGame = len(graphMeRapid) / rapidCounter
        windowSize = int(movePerGame * 50) #window size of 50 games
        
        windowStep = int( windowSize / 5)  #moves forward 10 games per frame, data presists for 5 frames

        #windowSize = int(movePerGame * 1) #window size of 1 games
        #windowStep = int( windowSize / 1)  #moves forward 1 games per frame, data presists for 1 frames

        passOverKey = False
        try:
            graphMeRapid[1 + windowSize * 2]
        except:
            print("\nError. Not enough moves for animated graph.\n")
            graphMeRapid = [1]
            passOverKey = True
            
        if passOverKey == False: # when not enough moves to graph this section of code is ignored

            while len(graphMeRapid) > windowSize * 2:
                for i in range(windowSize):
                    tempGraphMe.append(graphMeRapid[i])
                    tempRatingGraph.append(int(rapidRatingList[i]))

                ratingGraphMe = sum(tempRatingGraph) / len(tempRatingGraph)
                
                fig, axs = plt.subplots(1, 2, gridspec_kw={'width_ratios': [6, 1]})

                axs[0].hist(tempGraphMe, max(tempGraphMe), width=1, color = 'g', density = True)
                axs[0].set_title('Histogram of Move Time')
                axs[0].set_xlabel('Seconds')
                axs[0].set_ylabel('Frequency')
                axs[0].set_xlim(0, 60)
                axs[0].set_ylim([0,1.25 * rapidLambda])

                axs[1].bar(1, ratingGraphMe)
                axs[1].set_ylim([minRating,maxRating])
                axs[1].set_title('Rating')
                axs[1].xaxis.set_visible(False)
                axs[1].yaxis.tick_right()

                plt.savefig("C:/Users/User/Documents/Chess rating slideshow/" + str(user_name) + '/pngs/' + str(picNumber) + '.png')#
                plt.close()

                #print(len(graphMeRapid)) # checking that these 2 are equal
                #print(len(rapidRatingList))
                graphMeRapid = graphMeRapid[windowStep:]
                rapidRatingList = rapidRatingList[windowStep:]
                picNumber += 1
                tempGraphMe = []
                tempRatingGraph = []
                ratingGraphMe = 0

        

            path = 'C:/Users/User/Documents/Chess rating slideshow/' + str(user_name) + '/pngs/'
            frames = []
            images = glob.glob(path + "*.png")
            for i in images:
                new_frame = Image.open(i)
                frames.append(new_frame)

            frames[0].save('C:/Users/User/Documents/Chess rating slideshow/' + str(user_name) + '/graphs/' + user_name + '.gif',
                           format = 'GIF',
                           append_images = frames[1:],
                           save_all = True,
                           duration = 200, #lower numbers are faster, default is 200
                           loop = 0)

            print("Gif saved")


