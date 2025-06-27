# Swimmer class for use in meet management & heat sheet generation
# by Aiden Gray
# Last modified 5/27/2024

import test
import random


class Swimmer:
    """
    Object for each swimmer in meet
    Stores name, age, team, events, and relay status
    Meant to be generated from .csv file formated as below:
    "first name,last name,gender,age,team,event 1,event 2,event 3,medley relay,free relay" 
    """

    def __init__(self, swimID : str, infoLine : list):
        self.userID_ = swimID
        
        self.firstName_ = infoLine[0].title()
        self.lastName_ = infoLine[1].title()
        self.age_ = infoLine[2]
        self.gender_ = infoLine[3][0].lower()
        self.team_ = infoLine[4]
        self.event1_ = infoLine[5].lower().strip()
        self.event2_ = infoLine[6].lower().strip()
        self.event3_ = infoLine[7].lower().strip()
        self.medley_ = infoLine[8]
        self.free_ = infoLine[9]


    def __str__(self) -> str:
        return f"{self.firstName_} {self.lastName_} is registered for {self.event1_}, {self.event2_}, and {self.event3_}."
    

    def getSwimID(self):
        """
        Returns swimmer's ID as a string
        """
        return self.userID_
    

    def getName(self):
        """
        Returns swimmer's full name, first then last, as a string
        """
        fullName = self.firstName_ + " " + self.lastName_
        return fullName
    

    def getAge(self):
        """
        Returns swimmer's age as a string
        """
        return self.age_
    

    def getTeam(self):
        """
        Returns swimmer's team as a two or three character string
        """
        return self.team_
    

    def getEvents(self):
        """
        Returns list of registered events
        """
        eventList = [self.event1_.lower(), self.event2_, self.event3_]
        for entry in range(len(eventList)):
            eventList[entry] = eventList[entry].lower().strip()
        return eventList
    

    def getSwimmerData(self) -> list:
        """
        Returns categorical swimmer data

        Returns:
            list: In format '[full name, gender, age]'
        """
        outputList = [self.firstName_ + " " + self.lastName_, self.gender_, self.age_]
        return outputList


    def checkEvent(self, event : str, strokeName : str):
        """
        Returns 'True' if registered for given event, else returns 'False'
        """
        #cleanEvent = event.lower().strip() # Irrelevant due to source being hard coded list

        if self.event1_ == event or self.event1_ == strokeName:
            return True
        elif self.event2_ == event or self.event2_ == strokeName:
            return True
        elif self.event3_ == event or self.event3_ == strokeName:
            return True
        return False



    def checkMedleyRelay(self):
        """
        Returns 'True' if registered for medley relay, else returns 'False'
        """
        if self.medley_.lower().strip() == "true" or self.medley_.lower().strip() == "yes":
            return True
        return False


    def checkFreeRelay(self):
        """
        Returns 'True' if registered for free relay, else returns 'False'
        """
        if self.free_.lower().strip() == "true" or self.free_.lower().strip() == "yes":
            return True
        return False


class Relay:
    def __init__(self, relayTeam : str, teamID : str) -> None:
        self._team = relayTeam
        self._teamID = teamID


    def __str__(self) -> str:
        return f"{self._team} relay team"

    
    def getSwimID(self) -> str:
        return self._teamID
    

    def getTeam(self) -> str:
        return self._teamID.upper()
    

    def getName(self) -> str:
        return self._team
    

    def getAge(self) -> str:
        return ""
    

def testSwimmer():
    testInput = ["John","Doe","8","m","hab","fly","back ","Free","True","False"]
    swimmerBoi = Swimmer("hab123", testInput)
    print(swimmerBoi)

    # Test checking event
    test.testEqual(swimmerBoi.checkEvent("fly"),True)
    test.testEqual(swimmerBoi.checkEvent("FlY"),True)
    test.testEqual(swimmerBoi.checkEvent("fly "),True)
    test.testEqual(swimmerBoi.checkEvent("breast"),False)

    # Test getting event list
    test.testEqual(swimmerBoi.getEvents(),["fly","back","free"])

    # Test relay booleans
    test.testEqual(swimmerBoi.checkMedleyRelay(),True)
    test.testEqual(swimmerBoi.checkFreeRelay(),False)


if __name__ == "__main__":
    testSwimmer()