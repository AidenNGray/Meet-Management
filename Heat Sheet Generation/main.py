# Primary executable to bring together Meet, Event, Swimmer, Relay, and pdfGen objects
# by Aiden Gray
# Last modified 6/3/2024

import json
from pdfGen import generateHeatSheet
from meet import Meet
from os import listdir

LINE_WIDTH = 100


def main():
    """
    Main execution loop for the Meet Management program.
    """
    inputsAndGeneration()
    pause = input("Enter 1 to create a new heat sheet or any other input to exit: ")
    if pause == '1':
        main()


def title():
    """
    Prints the title and instructions for the program.
    """
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


def generate_meet_pdf(
    meetName: str,
    numLanes: int,
    emptyLanes: bool,
    swimmer_files: list[str],
    relay_files: list[str],
    temp_dir: str = "Event Outputs/",
    pdf_out_dir: str = "pdf Outputs/"
) -> str:
    """
    Programmatic entry point for generating a meet pdf.
    Returns the absolute path to the generated PDF.
    """
    import os
    with open("config.json", "r") as f:
        config = json.load(f)
        
    meetObject = Meet(meetName, config, numLanes, emptyLanes)

    for filename in relay_files:
        meetObject.importRelays(filename)
        print(f"{filename} (Relays) imported")
        
    for filename in swimmer_files:
        meetObject.importFile(filename)
        print(f"{filename} (Swimmers) imported")

    print(f"Generating events for {meetName}...")
    meetObject.generateEvents()
    meetObject.generateTxtFiles(output_dir=temp_dir)
    
    pdf_path = generateHeatSheet(meetName, input_dir=temp_dir, output_dir=pdf_out_dir)
    return pdf_path

def inputsAndGeneration():
    """
    Collects inputs from the user, imports data, and generates the heat sheet.
    """
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
        
    swimmer_files = []
    relay_files = []
    
    pause = input("Confirm all entry files are in 'Data Files' directory by clicking enter.")
    for filename in listdir('./Data Files'):
        if "template" in filename.lower():
            continue
        filepath = f"Data Files/{filename}"
        if "relay" in filename.lower() and filename.endswith(".csv"):
            relay_files.append(filepath)
        elif filename.endswith(".csv"):
            swimmer_files.append(filepath)
            
    print()
    pause = input("Press enter to generate.")
    print()
    print("Generating .....".center(LINE_WIDTH))
    print()
    
    pdf_path = generate_meet_pdf(meetName, numLanes, emptyLanes, swimmer_files, relay_files)
    print(f"{meetName}.pdf successfully generated in 'pdf Outputs' directory", end= '\n\n')
    
    with open("config.json", "r") as f:
        config = json.load(f)
    if config.get("output", {}).get("cleanup_text_files", False):
        import os
        try:
            for filename in os.listdir("Event Outputs"):
                if filename.startswith(meetName) and filename.endswith(".txt"):
                    os.remove(os.path.join("Event Outputs", filename))
            print("Temporary text files have been cleaned up.\n")
        except Exception as e:
            print(f"Failed to clean up text files: {e}\n")
    

if __name__ == "__main__":
    title()
    main()