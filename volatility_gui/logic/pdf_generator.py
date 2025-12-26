from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from typing import List, Dict, Any, Optional
import os


# Tokyo Night color scheme for PDF reports
class TokyoNightPDF:
    """Tokyo Night colors adapted for PDF generation."""
    BG_DARK = colors.HexColor('#1a1b26')
    BG = colors.HexColor('#24283b')
    BG_HIGHLIGHT = colors.HexColor('#292e42')
    FG = colors.HexColor('#c0caf5')
    FG_DARK = colors.HexColor('#a9b1d6')
    ACCENT = colors.HexColor('#7aa2f7')
    ACCENT_SECONDARY = colors.HexColor('#bb9af7')
    BORDER = colors.HexColor('#414868')
    CYAN = colors.HexColor('#7dcfff')


class PDFReportGenerator:
    """Generate professional PDF reports for forensic analysis."""
    
    def __init__(self, output_path: str, case_name: str = "Forensic Analysis"):
        """
        Initialize the PDF report generator.
        
        Args:
            output_path: Path where the PDF will be saved
            case_name: Name of the case/investigation
        """
        self.output_path = output_path
        self.case_name = case_name
        self.doc = SimpleDocTemplate(output_path, pagesize=letter)
        self.styles = getSampleStyleSheet()
        self.story = []
        
        # Custom Tokyo Night-inspired styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=TokyoNightPDF.ACCENT,
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=TokyoNightPDF.ACCENT_SECONDARY,
            spaceAfter=12,
            spaceBefore=12
        )
        
        self.subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=TokyoNightPDF.CYAN,
            spaceAfter=6
        )
        
    def add_title_page(self, dump_file: str, analyst: str = "", notes: str = ""):
        """Add a title page to the report."""
        # Title
        self.story.append(Spacer(1, 2*inch))
        self.story.append(Paragraph(self.case_name, self.title_style))
        self.story.append(Spacer(1, 0.5*inch))
        
        # Report info
        info_style = self.styles['Normal']
        self.story.append(Paragraph(f"<b>Memory Dump:</b> {os.path.basename(dump_file)}", info_style))
        self.story.append(Spacer(1, 0.1*inch))
        self.story.append(Paragraph(f"<b>Report Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", info_style))
        
        if analyst:
            self.story.append(Spacer(1, 0.1*inch))
            self.story.append(Paragraph(f"<b>Analyst:</b> {analyst}", info_style))
            
        if notes:
            self.story.append(Spacer(1, 0.3*inch))
            self.story.append(Paragraph("<b>Notes:</b>", info_style))
            self.story.append(Spacer(1, 0.1*inch))
            self.story.append(Paragraph(notes, info_style))
            
        self.story.append(PageBreak())
        
    def add_section(self, title: str, data: List[Dict[str, Any]], max_rows: int = 50):
        """
        Add a section with a table of data.
        
        Args:
            title: Section title
            data: List of dictionaries containing the data
            max_rows: Maximum number of rows to include (to prevent huge PDFs)
        """
        if not data:
            return
            
        # Section title
        self.story.append(Paragraph(title, self.heading_style))
        self.story.append(Spacer(1, 0.2*inch))
        
        # Get headers from first item
        headers = list(data[0].keys())
        
        # Limit data if too large
        display_data = data[:max_rows]
        if len(data) > max_rows:
            self.story.append(Paragraph(
                f"<i>Showing {max_rows} of {len(data)} entries</i>",
                self.styles['Normal']
            ))
            self.story.append(Spacer(1, 0.1*inch))
        
        # Create table data
        table_data = [headers]
        for item in display_data:
            row = [str(item.get(h, ''))[:50] for h in headers]  # Truncate long values
            table_data.append(row)
        
        # Calculate column widths dynamically
        available_width = 7.5 * inch
        col_width = available_width / len(headers)
        
        # Create table
        table = Table(table_data, colWidths=[col_width] * len(headers))
        table.setStyle(TableStyle([
            # Header style - Tokyo Night accent
            ('BACKGROUND', (0, 0), (-1, 0), TokyoNightPDF.ACCENT),
            ('TEXTCOLOR', (0, 0), (-1, 0), TokyoNightPDF.BG_DARK),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data style - Tokyo Night alternating rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TEXTCOLOR', (0, 1), (-1, -1), TokyoNightPDF.FG),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [TokyoNightPDF.BG_DARK, TokyoNightPDF.BG]),
            ('GRID', (0, 0), (-1, -1), 0.5, TokyoNightPDF.BORDER),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.3*inch))
        
    def add_summary(self, summary_data: Dict[str, Any]):
        """Add a summary section with key statistics."""
        self.story.append(Paragraph("Executive Summary", self.heading_style))
        self.story.append(Spacer(1, 0.2*inch))
        
        for key, value in summary_data.items():
            self.story.append(Paragraph(f"<b>{key}:</b> {value}", self.styles['Normal']))
            self.story.append(Spacer(1, 0.05*inch))
            
        self.story.append(Spacer(1, 0.3*inch))
        
    def add_custom_section(self, title: str, content: str):
        """Add a custom text section."""
        self.story.append(Paragraph(title, self.heading_style))
        self.story.append(Spacer(1, 0.1*inch))
        self.story.append(Paragraph(content, self.styles['Normal']))
        self.story.append(Spacer(1, 0.3*inch))
        
    def generate(self):
        """Generate the PDF file."""
        try:
            self.doc.build(self.story)
            return True
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return False
            
    @staticmethod
    def create_forensic_report(
        output_path: str,
        dump_file: str,
        system_info: Optional[Dict[str, Any]] = None,
        processes: Optional[List[Dict[str, Any]]] = None,
        network: Optional[List[Dict[str, Any]]] = None,
        registry: Optional[List[Dict[str, Any]]] = None,
        files: Optional[List[Dict[str, Any]]] = None,
        case_name: str = "Forensic Analysis Report",
        analyst: str = "",
        notes: str = ""
    ) -> bool:
        """
        Create a complete forensic report.
        
        Args:
            output_path: Path where PDF will be saved
            dump_file: Path to the memory dump file
            system_info: System information dictionary
            processes: List of process data
            network: List of network connection data
            registry: List of registry data
            files: List of file data
            case_name: Name of the investigation
            analyst: Name of the analyst
            notes: Additional notes
            
        Returns:
            True if successful, False otherwise
        """
        generator = PDFReportGenerator(output_path, case_name)
        
        # Title page
        generator.add_title_page(dump_file, analyst, notes)
        
        # Summary
        summary = {}
        if processes:
            summary["Total Processes"] = len(processes)
        if network:
            summary["Network Connections"] = len(network)
        if files:
            summary["Files Scanned"] = len(files)
        if registry:
            summary["Registry Hives"] = len(registry)
            
        if summary:
            generator.add_summary(summary)
            generator.story.append(PageBreak())
        
        # System Information
        if system_info:
            generator.add_custom_section(
                "System Information",
                "<br/>".join([f"<b>{k}:</b> {v}" for k, v in system_info.items()])
            )
            
        # Processes
        if processes:
            generator.add_section("Process List", processes)
            
        # Network
        if network:
            generator.add_section("Network Connections", network)
            
        # Registry
        if registry:
            generator.add_section("Registry Hives", registry)
            
        # Files
        if files:
            generator.add_section("File Scan Results", files, max_rows=100)
        
        return generator.generate()
