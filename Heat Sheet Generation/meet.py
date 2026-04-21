#
# by Aiden Gray
# Last modified 5/28/2024

import csv, random, string
from swimmer import Swimmer, Relay
from event import Event


class Meet:
    """
    Main organizational class for a swim meet.
    Aggregates swimmers, organizes events, and handles the creation of output files.
    """

    def __init__(self, meetName : str, config : dict, numLanes : int = 6, emptyLanes : bool = False) -> None:
        """
        Initializes a Meet object.

        Args:
            meetName (str): Name of the meet.
            config (dict): The configuration dictionary loaded from config.json.
            numLanes (int): The number of lanes available for the meet.
            emptyLanes (bool): Whether to include empty lanes in the output.
        """
        self.MEET_NAME = meetName
        self._config = config
        self._idToSwimmer = {} # dictionary of swimmers mapped to ID
        self._numToEvent = {} # dictionary of event numbers to event objects
        self._numLanes = numLanes
        self._emptyLanes = emptyLanes
        self._importedRelays = [] # List of parsed relay dicts


    def __str__(self) -> str:
        pass


    def importFile(self, filename : str) -> None:
        """
        Takes a .csv file and generates a swimmer object for each entry
        """
        with open(filename, 'r') as file:
            csvReader = csv.reader(file)
            next(csvReader) # skips header
            for row in csvReader:
                if row:
                    swimmerID = "".join(random.choices(string.ascii_letters, k=5))
                    newSwimmer = Swimmer(swimmerID, row)
                    self._idToSwimmer.update({swimmerID:newSwimmer})

    def importRelays(self, filename: str) -> None:
        """
        Takes a .csv file and imports relay entries.
        Format: Team,Age Group,Gender,Stroke,Relay Identifier,Swimmer 1,Swimmer 2,Swimmer 3,Swimmer 4
        """
        with open(filename, 'r') as file:
            csvReader = csv.reader(file)
            next(csvReader) # Skip header
            for row in csvReader:
                if not row or not row[0]: continue
                team_name = row[0].strip()
                age_group = row[1].strip()
                gender = row[2].strip()
                stroke = row[3].strip()
                identifier = row[4].strip()
                swimmers = [s.strip() for s in row[5:] if s.strip()]
                
                # Look up teamID from config
                team_id = "unknown"
                for t in self._config.get("teams", []):
                    if t["name"].lower() == team_name.lower():
                        team_id = t["id"]
                        break
                
                relay_data = {
                    "team": team_name,
                    "teamID": team_id,
                    "age_group": age_group,
                    "gender": gender,
                    "stroke": stroke,
                    "identifier": identifier,
                    "swimmers": swimmers
                }
                self._importedRelays.append(relay_data)

        #print(f"There are {len(self._idToSwimmer)} swimmers imported")


    def generateEvents(self) -> None:
        """
        Generates event objects for each event based on parameters
        """
        orderOfEvents = self._config["events"]["order"]
        strokeNames = self._config["events"]["stroke_names"]
        self.ageGroups = self._config["age_groups"]["individual"]
        eventNumber = 1

        relays = self._config["events"].get("relays", [])

        for relay in relays:
            if relay.get("position") == "start":
                eventNumber = self._generateRelays(eventNumber, relay.get("stroke"))

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
                newEvent = Event(eventData, self.MEET_NAME, False, self._config, numLanes=self._numLanes, emptyLanes=self._emptyLanes)
                newEvent.setAgeGroup(self.ageGroups[ageIndex])
                self._checkSwimmers(newEvent, orderOfEvents[strokeIndex], strokeNames[strokeIndex])
                self._numToEvent.update({eventNumber:newEvent})
                eventNumber += 1

        for relay in relays:
            if relay.get("position") == "end":
                eventNumber = self._generateRelays(eventNumber, relay.get("stroke"))

    def _generateRelays(self, startNumber : int, stroke : str) -> int:
        """
        Generates relay events based on teams in config.
        """
        self._relayAgeGroups = self._config["age_groups"]["relay"]
        numEvents = len(self._relayAgeGroups) * 2
        eventNumber = startNumber
        ageIndex = -1
        
        girls_start_odd = self._config["events"].get("girls_start_odd", True)
        
        for event in range(numEvents):
            if eventNumber % 2 == 1:
                ageIndex += 1
            ageList = self._relayAgeGroups[ageIndex].split()
            age = ageList[0]
            
            if girls_start_odd:
                gender_str = "Girls" if eventNumber % 2 == 1 else "Boys"
            else:
                gender_str = "Boys" if eventNumber % 2 == 1 else "Girls"
                
            relayObjects = []
            for r in self._importedRelays:
                if (r["age_group"].lower() == self._relayAgeGroups[ageIndex].lower() and 
                    r["gender"].lower() == gender_str.lower() and 
                    r["stroke"].lower() == stroke.lower()):
                    
                    newRelay = Relay(r["team"], r["teamID"], r["identifier"], r["swimmers"])
                    relayObjects.append(newRelay)
                    
            eventData = [eventNumber,age,f"{stroke} Relay"]
            newEvent = Event(eventData, self.MEET_NAME, True, self._config, relayObjects, numLanes=self._numLanes, emptyLanes=self._emptyLanes)
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
            min_age = self._config["age_groups"]["effective_age"]["min_age"]
            max_age = self._config["age_groups"]["effective_age"]["max_age"]
            group_by = self._config["age_groups"]["effective_age"].get("group_by", 2)
            
            if age <= min_age:
                effectiveAge = min_age
            elif min_age < age < max_age:
                if age % group_by == 0:
                    effectiveAge = age - 1
                else:
                    effectiveAge = age
            else:
                effectiveAge = max_age

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
    import json
    with open("config.json", "r") as f:
        config = json.load(f)
    testMeet = Meet("Test Meet", config)
    testMeet.importFile("Data Files/Test File.csv")
    testMeet.generateEvents()
    testMeet.generateTxtFiles()


if __name__ == "__main__":
    testMeet()