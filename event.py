# Event class to be filled with swimmer objects and stored in meet object
# by Aiden Gray
# Last modified 5/26/2024

import test, random, sys
import swimmer as swmr


class Event:
    """
    Stores event data and swimmer objects registered for event
    Organizes heats and randomizes order of swimmers
    Data input formatted as shown in setEventData docstring
    """

    def __init__(self, dataList : list, meetName : str, relayEvent : bool, swimmerList : list = [], numLanes : int = 6, emptyLanes : bool = False) -> None:
        """
        _summary_

        Args:
            dataList (list): To be formatted as '[event number, age, stroke]'
            swimmerList (list): List of swimmer objects registered for event or relay teams if relay event
            meetName (str): Used for filename purposes
            relayEvent (bool): Indicates a relay event
            numLanes (int): Number of lanes to be used for seeding
            emptyLanes (bool): Indicates whether unused lanes should be displayed (True) or left off (False)
        """
        self._NUM_LANES = numLanes
        self._MEET_NAME = meetName
        self._RELAY = relayEvent
        self._EMPTY_LANES = emptyLanes
        self.setEventData(dataList)
        self._eventSwimmers = {}

        if not relayEvent:
            self.addSwimmers(swimmerList)
        else:
            index = 0
            for entry in swimmerList:
                self._eventSwimmers.update({index:entry})
                index += 1
            
        
    def __str__(self) -> str:
        numSwimmers = len(self._eventSwimmers)
        return f"Event {self._number}, {self._gender.capitalize()} {self._distance} {self._stroke}, has {numSwimmers} swimmers registered."


    def getEventData(self) -> list:
        """
        Used for retrieving event data

        Returns:
            list: Formatted as '[Event number, gender, age, distance, stroke]'
        """
        outputList = [self._number, self._gender, self._age, self._distance, self._stroke]
        return outputList


    def setEventData(self, data : list) -> None:
        """
        Sets event parameters. Input listed formatted as below:
        '[event number, age, stroke]'
        """
        print(data)
        print(data[1])
        self._number = data[0]
        self._age = data[1]
        self._stroke = data[2]

        # Determines gender based on event number
        GIRLS_START = True
        if GIRLS_START and int(self._number) % 2 == 1:
            self._gender = "girls"
        elif not GIRLS_START and int(self._number) % 2 == 0:
            self._gender = "girls"
        else:
            self._gender = "boys"
            

        # This is hard coded for YMCA summer league format
        if not self._RELAY:
            if int(self._age) >= 9 and self._stroke.lower().strip() != "im":
                self._distance = "50"
            elif self._stroke.lower().strip() == "im":
                self._distance = "100"
            else:
                self._distance = "25"
        else:
            print(int(self._age))
            if int(self._age) < 9:
                self._distance = "100"
            else:
                self._distance = "200"


    def addSwimmer(self, swimmer : object) -> bool:
        """
        Adds swimmer to event dictionary
        Returns True if successful and False if already in event
        """
        newID = swimmer.getSwimID()
        if newID not in self._eventSwimmers:
            self._eventSwimmers.update({newID:swimmer})
            return True
        return False
    

    def addSwimmers(self, swimmerList : list) -> None:
        """
        Takes a list of swimmer objects and adds each to the event
        """
        for swimmer in swimmerList:
            self.addSwimmer(swimmer)


    def setAgeGroup(self, ageGroup : str) -> None:
        self._ageGroup = ageGroup

    
    def getSwimmerIDs(self) -> list:
        """
        Returns list of swimmerIDS registered for event
        """
        idList = []
        for swimmer in self._eventSwimmers:
            idList.append(swimmer)
        return idList


    def _organizeHeats(self) -> list:
        """
        Randomizes order of swimmers and returns 2D array of heats with swimmer objects
        """
        numSwimmers = len(self._eventSwimmers)
        numHeats = ((numSwimmers-1) // self._NUM_LANES) + 1 #Hacky way of avoiding a full heat making an extra one

        if numSwimmers > self._NUM_LANES:
            overflowSwimmers = numSwimmers % self._NUM_LANES
            if overflowSwimmers == 0:
                heat1Entries = self._NUM_LANES
                heat2Entries = self._NUM_LANES
            elif overflowSwimmers < 3:
                heat1Entries = 3
                heat2Entries = self._NUM_LANES - (heat1Entries - overflowSwimmers)
            else:
                heat1Entries = overflowSwimmers
                heat2Entries = self._NUM_LANES
        else:
            heat1Entries = numSwimmers

        keyList = list(self._eventSwimmers.keys())
        if not self._RELAY:
            random.shuffle(keyList)

        eventHeats = []
        for heatNum in range(numHeats):
            heat = []
            if heatNum == 0:
                numInHeat = heat1Entries
            elif heatNum == 1:
                numInHeat = heat2Entries
            else:
                numInHeat = self._NUM_LANES

            if numInHeat >= 1:
                for i in range(numInHeat):
                    key = keyList.pop()
                    heat.append(self._eventSwimmers[key])


            '''for i in range(numInHeat):
                try:
                    key = keyList.pop(random.randint(0,len(keyList)-1))
                    heat.append(self._eventSwimmers[key])
                except:
                    print("This is the error")'''

            eventHeats.append(heat)

        return eventHeats


    def printEvent(self):
        """
        Prints a clean view of the event
        """
        CELL_WIDTH = 49
        self._heatArray = self._organizeHeats()

        eventDescription = f"<b>Event {self._number} - {self._gender.capitalize()} {self._ageGroup.title()} {self._distance} Yard {self._stroke.title()}</b>"
        print(eventDescription)
        print("-" * CELL_WIDTH)
        HEADER = f'<b>{"Lane":4} {"Name":20} {"Age":3} {"Team":8} {"Seed Time":9}</b>'
        print(HEADER)
        print("-" * CELL_WIDTH)

        heatNum = 1
        for heat in self._heatArray:
            print(f"<b>Heat {heatNum} of {len(self._heatArray)}</b>")
            middleLane = self._NUM_LANES // 2
            laneModifier = (len(heat) - 1) // 2
            startLane = middleLane - laneModifier
            currentLane = 1
            if self._EMPTY_LANES:
                while currentLane != startLane:
                    print(f"{currentLane:4}")
                    currentLane += 1
            else:
                currentLane = startLane
            for swimmer in heat:
                name = swimmer.getName()
                age = swimmer.getAge()
                team = swimmer.getTeam().upper()
                if len(name) > 20:
                    name = f"{name[:19]}-"
                ln = f"{currentLane:4} {name:20} {age:3} {team:8} {'NT':9}"
                currentLane += 1
                print(ln)
            if self._EMPTY_LANES:
                while currentLane != self._NUM_LANES:
                    print(f"{currentLane:4}")
                    currentLane += 1
            heatNum += 1

    
    def exportEvent(self):
        """
        Generates a .txt file with the event in heat sheet format
        """
        filename = f"{self._MEET_NAME} - Event #{self._number}"
        fileExt = ".txt"
        filePath = "Event Outputs/"

        temp = sys.stdout
        sys.stdout = open(f'{filePath}{filename}{fileExt}','w')
        self.printEvent()
        sys.stdout = temp
        print(f"Event #{self._number} has been exported")      


def testEvent():
    testInput1 = ["John","Doe","8","f","hab","fly","back ","Free","True","False"]
    testInput2 = ["Jane","Roe","7","f","eff","breast","back ","Free","False","False"]
    testInput3 = ["Steve","Deve","8","f","wc","fly","breast ","free","True","True"]
    swimmerBoi1 = swmr.Swimmer("hab123",testInput1)
    swimmerBoi2 = swmr.Swimmer("eff123",testInput2)
    swimmerBoi3 = swmr.Swimmer("wc123",testInput3)
    swimmerBoi4 = swmr.Swimmer("wc124",testInput3)
    swimmerBoi5 = swmr.Swimmer("wc125",testInput3)
    swimmerBoi6 = swmr.Swimmer("wc126",testInput3)
    swimmerBoi7 = swmr.Swimmer("wc127",testInput3)
    swimmerBoi8 = swmr.Swimmer("wc128",testInput3)
    #print(swimmerBoi1,swimmerBoi2,swimmerBoi3)

    eventData = ["3", "11", "free"]
    swimmers = [swimmerBoi1, swimmerBoi2, swimmerBoi3, swimmerBoi4, swimmerBoi5, swimmerBoi6, swimmerBoi7, swimmerBoi8]
    event3 = Event(eventData, "Test Meet", False, swimmers)
    print(event3.getEventData())
    #print(event3)
    #event3.addSwimmers(swimmers)
    #print(event3)
    #print(event3.getSwimmerIDs())
    #print(event3.organizeHeats())
    event3.setAgeGroup("11 & 12")
    event3.printEvent()
    event3.exportEvent()


if __name__ == "__main__":
    testEvent()
