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


    def load_from_db(self, db, meet_id: str) -> None:
        """
        Loads swimmers and relay entries directly from the database for a specific meet.
        """
        from models import Meet as DBMeet, Swimmer as DBSwimmer, Entry, RelayEntry
        
        db_meet = db.query(DBMeet).filter(DBMeet.id == meet_id).first()
        if not db_meet:
            raise ValueError(f"Meet {meet_id} not found in database.")
            
        # Get all swimmers associated with this meet's entries
        swimmers_query = db.query(DBSwimmer).join(Entry).filter(Entry.meet_id == meet_id).distinct().all()
        for db_swimmer in swimmers_query:
            newSwimmer = Swimmer(db_swimmer=db_swimmer)
            self._idToSwimmer[newSwimmer.getSwimID()] = newSwimmer

        # Get all relays associated with this meet
        relays_query = db.query(RelayEntry).filter(RelayEntry.meet_id == meet_id).all()
        for r in relays_query:
            team_id = r.team.short_id if r.team else r.team_id
            
            # Extract swimmers if relationships exist
            swimmers = []
            if r.swimmer1: swimmers.append(r.swimmer1.first_name + " " + r.swimmer1.last_name)
            if r.swimmer2: swimmers.append(r.swimmer2.first_name + " " + r.swimmer2.last_name)
            if r.swimmer3: swimmers.append(r.swimmer3.first_name + " " + r.swimmer3.last_name)
            if r.swimmer4: swimmers.append(r.swimmer4.first_name + " " + r.swimmer4.last_name)
            
            relay_data = {
                "team": r.team.name if r.team else team_id,
                "teamID": team_id,
                "age_group": r.age_group,
                "gender": r.gender,
                "stroke": r.stroke,
                "identifier": r.identifier,
                "swimmers": swimmers
            }
            self._importedRelays.append(relay_data)



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
                
        self._combineSmallEvents()

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

    def _combineSmallEvents(self) -> None:
        """
        Loops through events in pairs and combines them into a single heat
        if their total number of swimmers + 1 <= numLanes.
        """
        if not self._config.get("events", {}).get("combine_small_events", False):
            return
            
        maxEvent = max(self._numToEvent.keys()) if self._numToEvent else 0
        for i in range(1, maxEvent, 2):
            event1 = self._numToEvent.get(i)
            event2 = self._numToEvent.get(i + 1)
            if not event1 or not event2:
                continue
                
            swimmers1 = len(event1.getSwimmerIDs())
            swimmers2 = len(event2.getSwimmerIDs())
            
            if swimmers1 == 0 or swimmers2 == 0:
                continue
                
            if swimmers1 + swimmers2 <= self._numLanes - 1:
                total_lanes = swimmers1 + 1 + swimmers2
                middle_lane = self._numLanes // 2
                start_lane1 = middle_lane - (total_lanes - 1) // 2
                start_lane2 = start_lane1 + swimmers1 + 1
                
                event1.setCombinedLanes(start_lane1, i + 1)
                event2.setCombinedLanes(start_lane2, i)

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


    def generateTxtFiles(self, output_dir: str = "Event Outputs/") -> None:
        print_empty_events = self._config.get("events", {}).get("print_empty_events", False)
        for key in self._numToEvent:
            event = self._numToEvent[key]
            if not print_empty_events and len(event.getSwimmers()) == 0:
                continue
            event.exportEvent(output_dir=output_dir)


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