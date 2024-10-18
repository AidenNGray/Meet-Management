#
# by Aiden Gray
# Last modified 5/28/2024

import csv, random, string
from swimmer import Swimmer, Relay
from event import Event


class Meet:
    """
    I have no idea what this will do
    """

    def __init__(self, meetName : str, numLanes : int = 6, emptyLanes : bool = False) -> None:
        self.MEET_NAME = meetName
        self._MEDLEY = True
        self._FREE = True
        self._numLanes = numLanes
        self._emptyLanes = emptyLanes
        self._idToSwimmer = {}
        self._numToEvent = {}


    def __str__(self) -> str:
        pass


    def importFile(self, filename : str) -> None:
        """
        Takes a .csv file and generates a swimmer object for each entry
        """
        with open(filename, 'r') as file:
            csvReader = csv.reader(file)
            lineCount = 0
            for row in csvReader:
                if lineCount != 0:
                    swimmerTeam = row[4].lower().strip()
                    randomDigits = ""
                    for digit in range(10): # Random generation of SwimIDs. May be useful in the future for time tracking, etc.
                        random_letter = random.choice(string.ascii_letters)
                        randomDigits += random_letter
                    swimmerID = swimmerTeam + randomDigits
                    newSwimmer = Swimmer(swimmerID, row)
                    self._idToSwimmer.update({swimmerID:newSwimmer})
                lineCount += 1

        #print(f"There are {len(self._idToSwimmer)} swimmers imported")


    def generateEvents(self) -> None:
        """
        Generates event objects for each event based on parameters
        """
        orderOfEvents = ["free", "breast", "im", "back", "fly"]
        strokeNames = ["freestyle", "breaststroke", "individual medley", "backstroke", "butterfly"]
        self.ageGroups = ["6 & under", "7 & 8", "9 & 10", "11 & 12", "13 & up"]
        eventNumber = 1

        if self._MEDLEY:
            eventNumber = self._generateRelays(eventNumber, "medley")

        for strokeIndex in range(len(orderOfEvents)):
            numEvents = len(self.ageGroups) * 2
            ageIndex = -1
            for event in range(numEvents):
                if eventNumber % 2 == 1:
                    ageIndex += 1
                ageList = self.ageGroups[ageIndex].split()
                age = ageList[0]
                eventData = [eventNumber,age,orderOfEvents[strokeIndex]]
                # TODO: Determine which swimmer objects need to go in this event
                # Probably write a function for this for clarity
                newEvent = Event(eventData, self.MEET_NAME, False, numLanes= self._numLanes)
                newEvent.setAgeGroup(self.ageGroups[ageIndex])
                self._checkSwimmers(newEvent, orderOfEvents[strokeIndex], strokeNames[strokeIndex])
                self._numToEvent.update({eventNumber:newEvent})
                eventNumber += 1

        if self._FREE:
            eventNumber = self._generateRelays(eventNumber, "free")

        

    def _generateRelays(self, startNumber : int, stroke : str) -> int:
        # This will be hard coded to start with a medley relay and end with a free relay
        RELAY_TEAMS = ["Effingham", "Habersham", "Islands", "West Chatham", "Liberty"]
        TEAM_IDS = ['eff', 'hab', 'isl', 'wc', 'lib']
        relayObjects = []
        for team in range(len(RELAY_TEAMS)):
            newRelay = Relay(RELAY_TEAMS[team], TEAM_IDS[team])
            relayObjects.append(newRelay)
        self._relayAgeGroups = ["8 & under", "9 & 10", "11 & 12", "13 & up"]
        numEvents = len(self._relayAgeGroups) * 2
        eventNumber = startNumber
        ageIndex = -1
        for event in range(numEvents):
            if eventNumber % 2 == 1:
                ageIndex += 1
            ageList = self._relayAgeGroups[ageIndex].split()
            age = ageList[0]
            eventData = [eventNumber,age,f"{stroke} Relay"]
            newEvent = Event(eventData, self.MEET_NAME, True, relayObjects)
            newEvent.setAgeGroup(self._relayAgeGroups[ageIndex])
            self._numToEvent.update({eventNumber:newEvent})
            eventNumber += 1

        return eventNumber


    def _checkSwimmers(self, eventObject : object, stroke : str, strokeName : str) -> None:
        """
        returns list of swimmer objects that should be in a given event object
        eventData is returned as '[event number, gender, age, distance, stroke]'
        swimmer data is returned as '[full name, gender, age]'
        """
        eventData = eventObject.getEventData()
        #print("Event data: ", eventData)
        for key in self._idToSwimmer:
            swimmerObject = self._idToSwimmer[key]
            swimmerData = swimmerObject.getSwimmerData()
            if swimmerData[1] == 'm':
                gender = 'boys'
            else:
                gender = 'girls'

            age = int(swimmerData[2]) # This was a design oversight
            if age <= 6:         # Need to fix if changing age groups
                effectiveAge = 6
            elif age > 6 and age < 13:
                if age % 2 == 0:
                    effectiveAge = age - 1
                else:
                    effectiveAge = age
            else:
                effectiveAge = 13

            #print("Swimmer data:", swimmerData)
            if eventData[1] == gender and eventData[2] == str(effectiveAge):
                #print("Level 1")
                if swimmerObject.checkEvent(stroke, strokeName):
                    #print(swimmerObject)
                    eventObject.addSwimmer(swimmerObject)


    def generateTxtFiles(self) -> None:
        for key in self._numToEvent:
           #self._numToEvent[key].printEvent()
            self._numToEvent[key].exportEvent()


def testMeet():
    testMeet = Meet("Test Meet")
    testMeet.importFile("Data Files/Test File.csv")
    testMeet.generateEvents()
    testMeet.generateTxtFiles()


if __name__ == "__main__":
    testMeet()