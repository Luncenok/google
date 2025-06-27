import os
from urllib import request
import textwrap

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, black, gray, royalblue
from reportlab.platypus import Paragraph, Spacer, Frame, PageTemplate, BaseDocTemplate, Flowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# --- Configuration ---

PDF_FILE_NAME = "Mateusz_Idziejczak_Optimized_CV.pdf"
PLACEHOLDER_IMAGE_FILE = "placeholder_image.jpg"

# --- Colors & Fonts ---
# A slightly more modern and professional color palette
PRIMARY_COLOR = HexColor("#1E3A8A") # Dark Blue
SECONDARY_COLOR = HexColor("#374151") # Cool Gray
TEXT_COLOR = HexColor("#111827")    # Almost Black
SKILL_BG_COLOR = HexColor("#E5E7EB") # Light Gray for skill tags

# Using built-in fonts for portability
FONT_NAME = 'Helvetica'
FONT_NAME_BOLD = 'Helvetica-Bold'
FONT_NAME_ITALIC = 'Helvetica-Oblique'


# --- Optimized CV Data ---
# This dictionary contains the updated content based on resume best practices.
# Areas marked with [ ] are placeholders for you to fill in with specific data.

    # // REASON: Rewritten to be a direct, high-impact pitch. It starts with the target role,
    # // highlights key specializations (LLMs, AI Safety), and immediately showcases a major
    # // achievement (publication) to grab the recruiter's attention.
                # // REASON: Rephrased using the STAR method (Situation, Task, Action, Result).
                # // Focuses on impact and quantifies achievements where possible.
                # // REASON: Removed vague phrasing and focused on concrete technical contributions.
                # // REASON: Connects the project directly to the publication, creating a strong narrative.
                # // REASON: Translated from Polish and structured into clear, impactful bullet points.
                # // Highlights specific technologies and the quantifiable outcome.
                 # // REASON: Clarifies the project's goal and highlights the cutting-edge technology used.
        # // REASON: Added standardized CEFR levels for clarity.
        # // REASON: Grouped skills into categories. This helps recruiters quickly scan for relevant expertise.
        # // Added new keywords relevant to AI/ML Engineer roles.
CV_DATA = {
    "name": "",
    "title": "",
    "contact": {
        "Email": "",
        "LinkedIn": "",
        "Location": "",
    },
    "summary": "",
    "publications": [
        {
            "title": "",
            "journal": "",
            "date": "",
            "doi": ""
        }
    ],
    "experience": [
        {
            "title": "",
            "company": "",
            "date": "",
            "location": "",
            "description": [
                "",
                "",
                "",
                ""
            ]
        },
        {
            "title": "",
            "company": "",
            "date": "",
            "location": "",
            "description": [
                "",
                "",
                ""
            ]
        }
    ],
     "projects": [
        {
            "name": "",
            "date": "",
            "description": [
                "",
                "",
                ""
            ]
        },
        {
            "name": "",
            "date": "",
            "description": [
                "",
                ""
            ]
        },
        {
            "name": "",
            "date": "",
            "description": [
                "",
                ""
            ]
        },
    ],
    "education": [
        {"degree": "", "institution": "", "date": ""},
        {"degree": "", "institution": "", "date": ""},
        {"degree": "", "institution": "", "date": ""}
    ],
    "languages": [
        {"name": "", "label": ""},
        {"name": "", "label": ""},
        {"name": "", "label": ""},
    ],
    "skills": {
        "": ["", "", "", "", "", "", ""],
        "": ["", "", ""],
        "": ["", "", "", "", "", "", "", ""],
        "": ["", "", ""],
    },
    "awards": [
        ""
    ]
}


# --- Custom Flowable for Skills ---

class SkillsFlowable(Flowable):
    """A custom flowable to draw categorized or simple skills."""
    def __init__(self, skills_data):
        Flowable.__init__(self)
        self.skills = skills_data
        self.width = 0
        self.height = 0

    def wrap(self, availWidth, availHeight):
        self.width = availWidth
        x_cursor = 0
        y_cursor = 0
        line_height = 0.8 * cm

        if isinstance(self.skills, dict):
            for category, skills in self.skills.items():
                y_cursor += line_height
                for skill in skills:
                    if x_cursor + len(skill) * 4 > self.width:
                        x_cursor = 0
                        y_cursor += line_height * 0.75
                y_cursor += line_height * 0.25
        elif isinstance(self.skills, list):
            y_cursor += line_height
            for skill in self.skills:
                if x_cursor + len(skill) * 4 > self.width:
                    x_cursor = 0
                    y_cursor += line_height * 0.75
        
        self.height = y_cursor
        return self.width, self.height

    def draw(self):
        c = self.canv
        x_padding = 6
        y_padding = 4
        radius = 3
        h_spacing = 8
        line_height = 0.7 * cm
        y_cursor = self.height - (0.6 * cm)

        def draw_skill_tags(skills_list):
            nonlocal y_cursor
            x_cursor = 0
            c.setFont(FONT_NAME, 9)
            for skill in skills_list:
                text_width = c.stringWidth(skill, FONT_NAME, 9)
                item_width = text_width + 2 * x_padding
                if x_cursor + item_width > self.width:
                    x_cursor = 0
                    y_cursor -= line_height
                c.setFillColor(SKILL_BG_COLOR)
                c.roundRect(x_cursor, y_cursor, item_width, line_height * 0.8, radius, stroke=0, fill=1)
                c.setFillColor(TEXT_COLOR)
                c.drawString(x_cursor + x_padding, y_cursor + y_padding, skill)
                x_cursor += item_width + h_spacing

        if isinstance(self.skills, dict):
            for category, skills in self.skills.items():
                c.setFont(FONT_NAME_BOLD, 10)
                c.setFillColor(TEXT_COLOR)
                c.drawString(0, y_cursor + y_padding, category)
                y_cursor -= line_height
                draw_skill_tags(skills)
                y_cursor -= (line_height * 1.25)
        elif isinstance(self.skills, list):
            draw_skill_tags(self.skills)

            
# --- Helper Functions & PDF Generation ---

def download_placeholder_image(url="https://via.placeholder.com/150", filename=PLACEHOLDER_IMAGE_FILE):
    if not os.path.exists(filename):
        print(f"Downloading placeholder image to {filename}...")
        try:
            # Set a user-agent to avoid 403 errors from some servers
            headers = {'User-Agent': 'Mozilla/5.0'}
            req = request.Request(url, headers=headers)
            with request.urlopen(req) as response, open(filename, 'wb') as out_file:
                data = response.read()
                out_file.write(data)
        except Exception as e:
            print(f"Error downloading image: {e}, using a blank space instead.")
            return None
    return filename

def draw_header(c, doc):
    """Draws the top header section of the CV."""
    c.saveState()
    
    page_width = doc.width + doc.leftMargin * 2
    page_height = doc.height + doc.topMargin + doc.bottomMargin
    data = CV_DATA

    # --- Profile Image ---
    img_path = download_placeholder_image()
    if img_path:
        img = ImageReader(img_path)
        img_size = 3 * cm
        img_x = page_width - 2.5*cm - img_size/2
        img_y = page_height - 2.5*cm - img_size/2
        
        # Draw a white background circle for the image
        c.setFillColor('white')
        c.circle(page_width - 2.5*cm, page_height - 2.5*cm, img_size/2 + 2, fill=1, stroke=0)
        
        c.saveState()
        path = c.beginPath()
        path.circle(page_width - 2.5*cm, page_height - 2.5*cm, img_size / 2)
        c.clipPath(path, stroke=0, fill=0)
        c.drawImage(img, img_x, img_y, width=img_size, height=img_size, preserveAspectRatio=True, anchor='c')
        c.restoreState()

    # --- Name and Title ---
    c.setFillColor(PRIMARY_COLOR)
    c.setFont(FONT_NAME_BOLD, 24)  # Slightly smaller font for name
    c.drawString(doc.leftMargin, page_height - 1.8 * cm, data["name"])
    c.setFillColor(SECONDARY_COLOR)
    c.setFont(FONT_NAME, 12)  # Slightly smaller font for title
    c.drawString(doc.leftMargin, page_height - 2.6 * cm, data["title"])

    # --- Contact Info ---
    # Adjust contact info to be more compact and avoid image
    c.setFont(FONT_NAME, 8)  # Smaller font for contact info
    
    # Calculate available width for contact info (avoiding image area)
    available_width = page_width - img_size - 4*cm
    
    # Create contact items with line breaks if needed
    contact_lines = []
    current_line = []
    current_line_width = 0
    
    for key, value in data["contact"].items():
        item = f"<b>{key}:</b> {value}"
        item_width = c.stringWidth(f"{key}: {value}", FONT_NAME, 8) + 10  # Add some padding
        
        if key == "Location":  # Force location to be on a new line
            if current_line:
                contact_lines.append("  •  ".join(current_line))
                current_line = []
            contact_lines.append(item)
        else:
            if current_line_width + item_width > available_width and current_line:
                contact_lines.append("  •  ".join(current_line))
                current_line = [item]
                current_line_width = item_width
            else:
                current_line.append(item)
                current_line_width += item_width
    
    if current_line:
        contact_lines.append("  •  ".join(current_line))
    
    contact_info = "<br/>".join(contact_lines)
    
    contact_style = ParagraphStyle('contact', fontName=FONT_NAME, fontSize=8, textColor=SECONDARY_COLOR, leading=10)
    p = Paragraph(contact_info, contact_style)
    p.wrapOn(c, available_width, doc.topMargin)
    p.drawOn(c, doc.leftMargin, page_height - 3.8 * cm)  # Positioned lower to avoid title

    c.restoreState()

def draw_section_title(story, title):
    """Adds a formatted section title to the story."""
    style = ParagraphStyle(
        name='SectionTitle', fontName=FONT_NAME_BOLD, fontSize=12,
        textColor=PRIMARY_COLOR, spaceBefore=0.4*cm, spaceAfter=0.2*cm,
        borderBottomWidth=1.5, borderBottomColor=PRIMARY_COLOR, borderBottomPadding=2,
    )
    story.append(Paragraph(title.upper(), style))

def create_cv_story(data):
    """Creates the main 'story' list of flowables for the document."""
    story = []
    
    # Add header content directly to the story
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Image, Table, TableStyle
    from reportlab.lib import colors
    
    # Create a table for the header with two columns
    img_path = download_placeholder_image()
    img = Image(img_path, width=2.5*cm, height=2.5*cm) if img_path else None
    
    # Create name and title section
    name_style = ParagraphStyle('NameStyle', fontName=FONT_NAME_BOLD, fontSize=24, textColor=PRIMARY_COLOR, leading=28)
    title_style = ParagraphStyle('TitleStyle', fontName=FONT_NAME, fontSize=14, textColor=SECONDARY_COLOR, leading=18)
    
    name_title = [
        [Paragraph(data.get("name", ""), name_style)],
        [Paragraph(data.get("title", ""), title_style)],
    ]
    
    # Add contact information
    contact_items = []
    for key, value in data.get("contact", {}).items():
        contact_items.append(f"<b>{key}:</b> {value}")
    contact_info = "  •  ".join(contact_items)
    contact_style = ParagraphStyle('contact', fontName=FONT_NAME, fontSize=8, textColor=SECONDARY_COLOR, leading=10)
    
    name_title.append([Paragraph(contact_info, contact_style)])
    
    # Create header table with no padding
    header_table = Table([
        [
            Table(name_title, colWidths=['*'], style=[
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
            ]),
            img
        ]
    ], colWidths=['*', 3*cm])
    
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    story.append(header_table)
    
    # Add a line separator with minimal spacing
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("<hr/>", getSampleStyleSheet()['Normal']))
    story.append(Spacer(1, 0.1 * cm))
    
    # --- STYLES ---
    body_style = ParagraphStyle('Body', fontName=FONT_NAME, fontSize=10, textColor=TEXT_COLOR, leading=14, spaceAfter=6)
    job_title_style = ParagraphStyle('JobTitle', fontName=FONT_NAME_BOLD, fontSize=11, textColor=TEXT_COLOR, spaceAfter=0)
    company_style = ParagraphStyle('Company', fontName=FONT_NAME, fontSize=10, textColor=SECONDARY_COLOR, spaceAfter=2)
    date_style = ParagraphStyle('Date', fontName=FONT_NAME_ITALIC, fontSize=9, textColor=SECONDARY_COLOR, spaceAfter=4)
    bullet_style = ParagraphStyle('Bullet', parent=body_style, leftIndent=0.5*cm, firstLineIndent=-0.2*cm, spaceAfter=2)
    lang_style = ParagraphStyle('Lang', fontName=FONT_NAME, fontSize=10, textColor=TEXT_COLOR, spaceAfter=2)

    # --- SUMMARY ---
    if "summary" in data and data["summary"]:
        draw_section_title(story, "Summary")
        story.append(Paragraph(textwrap.dedent(data["summary"]), body_style))
        story.append(Spacer(1, 0.2 * cm))

    # --- PUBLICATIONS ---
    if "publications" in data and data["publications"]:
        draw_section_title(story, "Publications & Research")
        for pub in data["publications"]:
            story.append(Paragraph(f"<b>{pub.get('title', '')}</b>", body_style))
            story.append(Paragraph(f"<i>{pub.get('journal', '')}</i>", body_style))
            story.append(Paragraph(f"DOI: <link href='{pub.get('doi', '')}' color='blue'>{pub.get('doi', '')}</link>", body_style))
            story.append(Spacer(1, 0.2 * cm))

    # --- EXPERIENCE ---
    if "experience" in data and data["experience"]:
        draw_section_title(story, "Experience")
        for job in data["experience"]:
            story.append(Paragraph(job.get("title", ""), job_title_style))
            story.append(Paragraph(job.get("company", ""), company_style))
            story.append(Paragraph(job.get("date", ""), date_style))
            for point in job.get("description", []):
                story.append(Paragraph(f"• {point}", bullet_style))
            story.append(Spacer(1, 0.2 * cm))

    # --- PROJECTS ---
    if "projects" in data and data["projects"]:
        draw_section_title(story, "Projects")
        for proj in data["projects"]:
            story.append(Paragraph(proj.get("name", ""), job_title_style))
            story.append(Paragraph(proj.get("date", ""), date_style))
            for point in proj.get("description", []):
                story.append(Paragraph(f"• {point}", bullet_style))
            story.append(Spacer(1, 0.2 * cm))

    # --- SKILLS ---
    if "skills" in data and data["skills"]:
        draw_section_title(story, "Technical Skills")
        story.append(SkillsFlowable(data["skills"]))
        story.append(Spacer(1, 4 * cm))

    # --- EDUCATION, AWARDS, LANGUAGES ---
    if "education" in data and data["education"]:
        draw_section_title(story, "Education & Qualifications")
        for edu in data["education"]:
            story.append(Paragraph(f"<b>{edu.get('degree', '')}</b>, <i>{edu.get('institution', '')}</i> - {edu.get('date', '')}", body_style))

    if "awards" in data and data["awards"]:
        story.append(Spacer(1, 0.2 * cm))
        story.append(Paragraph("<b>Awards</b>", company_style))
        for award in data["awards"]:
            story.append(Paragraph(f" • {award}", body_style))
    
    if "languages" in data and data["languages"]:
        story.append(Spacer(1, 0.2 * cm))
        story.append(Paragraph("<b>Languages</b>", company_style))
        for lang in data["languages"]:
             story.append(Paragraph(f"• <b>{lang.get('name', '')}:</b> {lang.get('label', '')}", lang_style))
    
    return story

def build_pdf(filename, cv_data):
    """Builds the final PDF document."""
    doc = BaseDocTemplate(
        filename, 
        pagesize=A4, 
        leftMargin=2*cm, 
        rightMargin=2*cm, 
        topMargin=2*cm,  # Reduced since header is now part of the story
        bottomMargin=2*cm
    )
    
    # Create a simple frame that uses the full page
    main_frame = Frame(
        doc.leftMargin,
        doc.bottomMargin,
        doc.width,
        doc.height,
        leftPadding=0,
        bottomPadding=0,
        rightPadding=0,
        topPadding=0,
        id='main_frame'
    )
    
    template = PageTemplate(id='main_template', frames=[main_frame])
    doc.addPageTemplates([template])

    # Create the story (which now includes the header)
    story = create_cv_story(cv_data)
    
    print(f"Generating optimized CV: {filename}...")
    doc.build(story)
    print("✅ CV successfully generated!")

# --- Main Execution ---
if __name__ == "__main__":
    build_pdf(PDF_FILE_NAME, CV_DATA)