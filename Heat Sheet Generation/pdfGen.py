# Generates heat sheet report from directory of txt files
# by Aiden Gray
# Last modified 5/29/2024

import os
import re
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph, Frame, PageTemplate, BaseDocTemplate, XPreformatted, Spacer, KeepTogether

def readTextFile(input_dir: str, filename : str) -> list:
    """
    Takes output from Event object and returns list of lines

    Args:
        input_dir (str): Directory containing the text files
        filename (str): Name of file in Event Output directory with file extension

    Returns:
        list: Each entry is a line of the file ending with '\n' character
    """
    file_path = os.path.join(input_dir, filename)
    with open(file_path, 'r') as file:
        lines = [line for line in file]
    return lines


class standardHeatSheet(BaseDocTemplate):

    def __init__(self, filename, meetName="Test Meet", **kw):
        super().__init__(
            filename, 
            leftMargin=0.3*inch, 
            rightMargin=0.3*inch, 
            topMargin=0.5*inch, 
            bottomMargin=0.5*inch, 
            **kw
        )
        self.meetName = meetName
    
        # Perfectly center two 3.8-inch columns on an 8.5-inch page (0.3" margins, 0.3" gap)
        self.leftFrame = Frame(0.3*inch, .5*inch, 3.8*inch, 10*inch, showBoundary=0, id='left', leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        self.rightFrame = Frame(4.4*inch, .5*inch, 3.8*inch, 10*inch, showBoundary=0, id='right', leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)

        # Define page templates
        self.addPageTemplates([
            PageTemplate(
                id='TwoColumn',
                pagesize=letter,
                frames=[self.leftFrame, self.rightFrame],
                onPage=self._header_footer,
            )
        ])

    def _header_footer(self, canvas, doc):
        """
        Draws the header and footer on each page using the canvas.
        """
        canvas.saveState()
        
        # Header: Centered meet name at the top
        canvas.setFont('Helvetica-Bold', 12)
        canvas.drawCentredString(letter[0] / 2.0, 10.5 * inch, self.meetName)
        
        # Footer: Centered page number at the bottom
        canvas.setFont('Helvetica', 10)
        canvas.drawCentredString(letter[0] / 2.0, 0.25 * inch, f"Page {doc.page}")
        
        canvas.restoreState()


def generateHeatSheet(meetName : str = 'Test Meet', input_dir: str = 'Event Outputs/', output_dir: str = 'pdf Outputs/'):
    """
    Generates a PDF heat sheet from the text files in the input directory.
    """
    styles = getSampleStyleSheet()
    styleN = styles['Code']
    # Explicitly set font to Courier and reduce size so long event titles fit in the frames
    # without overflowing and spilling off the page
    styleN.fontName = 'Courier'
    styleN.fontSize = 7.5
    styleN.leading = 9
    meetData = []

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Get all event files for this meet and sort them by event number
    try:
        files = [f for f in os.listdir(input_dir) if f.startswith(meetName) and f.endswith(".txt")]
    except FileNotFoundError:
        print(f"Directory {input_dir} not found.")
        return

    def get_event_num(filename):
        match = re.search(r'Event #(\d+)', filename)
        return int(match.group(1)) if match else 0

    files.sort(key=get_event_num)

    for filename in files:
        eventInfo = readTextFile(input_dir, filename)
        
        current_block = []
        blocks = []
        
        # Group lines into heats so we can keep them together on page breaks
        for line in eventInfo:
            # If we see a new heat, check if we already have a heat in the current block
            if "<b>Heat " in line and current_block:
                has_heat = any("<b>Heat " in l for l in current_block)
                # If the current block already contains a heat, start a new block
                if has_heat:
                    blocks.append(current_block)
                    current_block = []
            current_block.append(line)
            
        if current_block:
            blocks.append(current_block)
            
        # Add blocks to document as KeepTogether flowables
        for block in blocks:
            text = "".join(block)
            meetData.append(KeepTogether([XPreformatted(text, styleN)]))
            
        meetData.append(Spacer(1, 10))

    pdf_path = os.path.join(output_dir, f"{meetName}.pdf")
    pdf_doc = standardHeatSheet(pdf_path, meetName=meetName)
    pdf_doc.build(meetData)
    print(f"Successfully generated PDF: {pdf_path}")


if __name__ == "__main__":
    generateHeatSheet()
