# Generates heat sheet report from directory of txt files
# by Aiden Gray
# Last modified 5/29/2024

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph, Frame, PageTemplate, BaseDocTemplate, XPreformatted, Spacer

FILE_PATH = "Event Outputs/"

def readTextFile(filename : str) -> str:
    """
    Takes output from Event object and returns list of lines

    Args:
        filename (str): Name of file in Event Output directory with file extension

    Returns:
        str: Each entry is a line of the file ending with '\n' character
    """
    file = open(f"{FILE_PATH}{filename}",'r')
    lines = []
    for line in file:
        #cleanLine = line.split("\n")
        #lines.append(cleanLine[0])
        lines.append(line)
    file.close()
    return lines


class standardHeatSheet(BaseDocTemplate):

    def __init__(self, filename, **kw):
        super().__init__(filename, **kw)
    
        # Define frames
        self.leftFrame = Frame(.5*inch, .5*inch, 3.5*inch, 10*inch, showBoundary=0, id='left')
        self.rightFrame = Frame(4.5*inch, .5*inch, 3.5*inch, 10*inch, showBoundary=0, id='right')

        # Define styles
        styles = getSampleStyleSheet()
        self.styleN = styles['Code']
        self.styleH = styles['Italic']
        self.styleF = styles['Normal']

        # Define header and footer frames
        self.header_frame = Frame(.25*inch, 10.5*inch, 8*inch, .5*inch, showBoundary=0, id='header')
        self.footer_frame = Frame(.25*inch, .05*inch, 8*inch, .5*inch, showBoundary=0, id='footer')

        # Define page templates
        self.addPageTemplates([
            PageTemplate(
                id='TwoColumn',
                pagesize=letter,
                frames=[self.leftFrame, self.rightFrame], #TODO: Make header and footer work
                #onPage=self._header,
                #onPageEnd=self._footer
            )
        ])

    
    def _header(self, canvas, doc):
        self.styleH.alignment = 1 # centers header
        header_text = Paragraph('Test Meet', self.styleH)
        header_text.wrapOn(canvas, self.header_frame.width, self.header_frame.height)
        header_text.drawOn(canvas, self.header_frame.x1, self.header_frame.y1)


    def _footer(self, canvas, doc):

        self.styleF.alignment = 1  # center align the footer text
        footer_text = Paragraph("Page <seq id='PageNumber'/> of <seq id='TotalPages'/>", self.styleF)
        footer_text.wrapOn(canvas, self.footer_frame.width, self.footer_frame.height)
        footer_text.drawOn(canvas, self.footer_frame.x1, self.footer_frame.y1)


def generateHeatSheet(meetName : str = 'Test Meet'):
    styles = getSampleStyleSheet()
    styleN = styles['Code']
    meetData = []

    NUM_EVENTS = 66 #TODO: Make this auto change to num of files in folder
    for fileNumber in range(1, NUM_EVENTS+1):
        filename = f"{meetName} - Event #{fileNumber}.txt" # TODO: Add functionality to input meet name
        eventInfo = readTextFile(filename)
        for line in eventInfo:
            meetData.append(XPreformatted(line,styleN))
        meetData.append(Spacer(1,10)) # TODO: Replace with new line in txt generation

    # TODO: Count number lines to make better column breaks
    # May be better to handle in meet generation

    pdf_doc = standardHeatSheet(f"pdf Outputs/{meetName}.pdf")
    pdf_doc.build(meetData)


if __name__ == "__main__":
    generateHeatSheet()
