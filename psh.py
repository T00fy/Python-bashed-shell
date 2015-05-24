'''
Created on 31/07/2014

@author: mals426
'''


import os
import shlex
import collections
import signal


historyCounter = 1
positionOfNextPipe = -1
pipePosition = 0
doublePipeContinue = False
count = 0
counterList = []
idList = []


def getHistoryCounter():
    return historyCounter

def incrementHistoryCounter():
    global historyCounter 
    historyCounter = historyCounter + 1
    return historyCounter


def checkAmper(commandList):
    if(commandList[commandList.__len__()-1] == "&"):
            commandList.pop(commandList.__len__()-1)
            return True
    return False
         


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def checkHowManyPipes(commandList):
    counter = 0
    for i in range(0, commandList.__len__(), 1):
        if(commandList[i] == "|"):
            counter += 1
    return counter

def getNextPipePosition(commandList, pipePosition):
    for i in range(0, commandList.__len__(), 1):
        if(commandList[i] == "|"):
            return i     
        
def checkForDoublePipe(commandList):
    parameters = [False,0]
    try:
        for i in range(0, commandList.__len__(), 1):
            if(commandList[i] == "|" and commandList[i+1] == "|"):
                parameters[0] = True
                parameters[1] = i
                return parameters
        return parameters
    except IndexError:
        return parameters   
    
def checkProcessExists(pid):
    try:
        os.kill(pid, 0)
        return True
    except:
        return False

             
def runExternalProcess(commandList):
        global doublePipeContinue
        global inFirst
        global count
        global counterList
        global idList
        
        pipePosition = 0
        doublePipeParameters = checkForDoublePipe(commandList)
        doublePipeExists = doublePipeParameters[0]
        doublePipePosition = doublePipeParameters[1]
        doublePipeContinue = False
        inFirst = False
        ampersandExists = checkAmper(commandList)
        builtInCommand = checkSyntax(commandList)
        amountOfPipes = checkHowManyPipes(commandList)
        try:     
            child = os.fork()
            if(not builtInCommand):
                
                if(amountOfPipes == 0 and child == 0):
                        os.execvp(commandList[0], commandList)
                        
                elif(child == 0):          
                    
                    
                    if(doublePipeExists):
                        beforeDoublePipe = commandList[:doublePipePosition]
                        afterDoublePipe = commandList[doublePipePosition+2:]
                        runExternalProcess(beforeDoublePipe)
                        while(doublePipeContinue):
                            runExternalProcess(afterDoublePipe)
                            doublePipeContinue = False               
                        currentId = os.getpid()
                        os.kill(currentId, signal.SIGKILL)
                        
                    else:
                        pipePosition = getNextPipePosition(commandList, pipePosition)         
                        firstCommand = commandList[:pipePosition]
                        secondCommand = commandList[pipePosition+1:]
                        fd = os.pipe() #gives rd,wr
                        child2 = os.fork() #need to make child of child, otherwise can only talk to itself
                        if(child2 == 0): 
                            inFirst = True
                            os.close(fd[0])
                            os.close(1) 
                            os.dup(fd[1])
                            os.close(fd[1])      
                            os.execvp(firstCommand[0], firstCommand)
                        
                        os.close(fd[1])
                        os.close(0)
                        os.dup(fd[0])
                        os.close(fd[0]) 
                    inFirst = False 
                           
                    if(amountOfPipes > 1):     
                        runExternalProcess(secondCommand)
                        
                    if(not "|" in secondCommand): #if first command runs successfully     
                        
                        os.execvp(secondCommand[0], secondCommand)
                        
                    else:
                        currentId = os.getpid()
                        os.kill(currentId, signal.SIGKILL)
                
            
            if(not ampersandExists): #unless there's no ampersand
                os.wait()
            else:
                backgroundId = os.getpid()
                #need to get [jobcounter] + backgroundid string working. counter needs to be resizable
                count += 1
                
                counterList.append(count, backgroundId)
               # checkIfEarlierCountUsed()
                
                
                

                #continue with shit
        except FileNotFoundError:
            print("Command not found")
            doublePipeContinue = True
            if(inFirst):  
                currentId = os.getpid()
                os.kill(currentId, signal.SIGKILL)
            #currentId = os.getpid()
            #os.kill(currentId, signal.SIGKILL)
            
        except IOError:
            print("Command not found")
            
     
    
    
def doHistory(commandList):
    printableStack = stack
    if(commandList.__len__() > 1 and is_number(commandList[1])):
        historyPosition = str(commandList[1])
        
        indexOfElement = -1
        
        for i in range(0, printableStack.__len__(), 1):
            stringOfElement = str(printableStack[i])
            indexOfToken = stringOfElement.index(":") + 1
            historyNumber = stringOfElement[:indexOfToken]     
            if((historyPosition + ":") == historyNumber):
                indexOfElement = i
                
                
        if(indexOfElement > -1):        
            element = printableStack[indexOfElement]
            element = element.split(": ")
            element.pop(0)
            elementString = ' '.join(element)
            return elementString
        
        
        
        else:
            for i in range(0,printableStack.__len__(),1): 
                print(printableStack[i])
    else:    
        for i in range(0,printableStack.__len__(),1): 
            print(printableStack[i])
    

def changeDirectory(commandList):
    try:
        directory = os.getcwd()
        rootCheck = commandList[1]
        rootCheck = rootCheck[:1]
        if(rootCheck == "/"):
            os.chdir(commandList[1])
        else:
            directory = os.getcwd()
            directory += "/" + commandList[1]
            os.chdir(directory)
    except FileNotFoundError:
        print("No such directory")
    except NotADirectoryError:
        print("File is not a directory")
    except IndexError:
        os.chdir(directory)



def wordList(line):
    #this breaks the line into shell words.
    lexer = shlex.shlex(line, posix=True)
    lexer.whitespace_split = False
    lexer.wordchars += '#$+-,./?@^='
    args = list(lexer)
    return args



def checkSyntax(commandList):
    for i in range (0, commandList.__len__(), 1):
        if(commandList[i] == "|"):
            return False
    while(commandList[commandList.__len__()-1] == "|"):
        commandList.pop(commandList.__len__()-1) 
    while(commandList[0] == "|"):
        commandList.pop(0)
        
    if(commandList[0] == "cd"):
        return True  
    
    elif(commandList[0] == "exit") :
        passed = True
    elif(commandList[0] == "history" or commandList[0] == "h"):
        passed = True

    else :
        passed = False
        
    return passed 
    


def checkCommand(commandList):
    if(commandList[0] == "cd") :   
            changeDirectory(commandList)
            
            
    elif(commandList[0] == "history" or commandList[0] == "h"):
            historicCommand = doHistory(commandList)    
            if(historicCommand != None):
                newCommandList = wordList(historicCommand)
                if(checkSyntax(newCommandList)):
                    checkCommand(newCommandList)
                    stack.append(str(historyCounter) + ":" + " " + historicCommand)
                    incrementHistoryCounter()
                else:
                    runExternalProcess(newCommandList)
                
            
        
stack = collections.deque(maxlen=10)
signal.signal(signal.SIGPIPE, signal.SIG_DFL) #removes execvp errors

while(True) :
    rawUserInput = ""
    while(len(rawUserInput) == 0):
        rawUserInput = input("psh>")
    
    if(not rawUserInput[:2] == "h "):
        stack.append(str(historyCounter) + ":" + " " + rawUserInput)
        incrementHistoryCounter()
        
    try:   
        commandList = wordList(rawUserInput)
    except:
        print("Syntax error")
        rawUserInput = input("psh>")
        commandList = wordList(rawUserInput)
    
    passedSyntax = checkSyntax(commandList)   #check syntax if it is built-in command
    
    
    command = commandList[0]
    
    
    if(command == "exit" or command == "quit") :
            break     
    
    if(passedSyntax) : 
        checkCommand(commandList)

    else :
        runExternalProcess(commandList)
