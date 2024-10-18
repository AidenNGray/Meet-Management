# Primary executable to bring together Meet, Event, Swimmer, Relay, and pdfGen objects
# by Aiden Gray
# Last modified 6/3/2024

from pdfGen import generateHeatSheet
from meet import Meet
from os import listdir

LINE_WIDTH = 100


def main():
    inputsAndGeneration()
    pause = input("Enter 1 to create a new heat sheet or any other input to exit: ")
    if pause == '1':
        main()


def title():
    # Title (make pretty at some point)
    print('-' * LINE_WIDTH,end='\n\n')
    print("Summer League Heat Sheet Generator".center(LINE_WIDTH), end='\n\n')
    print('-' * LINE_WIDTH, end = '\n\n')

    # General instruction
    print("Written by Aiden Gray in 2024".center(LINE_WIDTH))
    print("Please read instructions, excuse bugs, and contact at 912.323.1761 with questions".center(LINE_WIDTH), end='\n\n')
    print("All entries must be in .csv format following the provided template (see 'Data Files' directory)".center(LINE_WIDTH))
    print("Inputs can not be modified once entered. New heat sheet must be generated".center(LINE_WIDTH))
    print("Review each .csv file to ensure compliance with required formatting (see 'READ Me.txt')".center(LINE_WIDTH), end= '\n\n')


def inputsAndGeneration():
    # User input
    meetName = input("Enter the meet name: ")
    numLanes = int(input("How many lanes are available? "))
    emptyLanesNumber = -1
    while True:
        emptyLanesNumber = input("Leave empty lanes? (Enter 1 for yes, 0 for no): ")
        if emptyLanesNumber == '1':
            emptyLanes = True
            break
        elif emptyLanesNumber == '0':
            emptyLanes = False
            break
        print("Invalid input. Please enter '1' or '0'")
    meetObject = Meet(meetName, numLanes, emptyLanes)

    pause = input("Confirm all entry files are in 'Data Files' directory by clicking enter.")
    for filename in listdir('./Data Files'):
        if filename != "Entry Template.csv":
            meetObject.importFile(f"Data Files/{filename}")
            print(f"{filename} imported")
    print()

    pause = input("Press enter to generate.")
    print()
    print("Generating .....".center(LINE_WIDTH))
    print()
    meetObject.generateEvents()
    meetObject.generateTxtFiles()
    generateHeatSheet(meetName)
    print(f"{meetName}.pdf successfully generated in 'pdf Outputs' directory", end= '\n\n')
    

if __name__ == "__main__":
    title()
    main()