import csv
import os
from datetime import datetime
from decimal import Decimal
from io import BytesIO, StringIO
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.platypus.flowables import HRFlowable
from .models import Donation, Campaign, DonorProfile


class ReportGenerator:
    """Utility class for generating donor contribution reports in CSV and PDF formats"""
    
    def __init__(self, user, campaign, date_from=None, date_to=None):
        self.user = user
        self.campaign = campaign
        self.date_from = date_from
        self.date_to = date_to
        self.donations = self._get_donations()
        
    def _get_donations(self):
        """Get filtered donations for the user and campaign"""
        queryset = Donation.objects.filter(
            donor=self.user,
            campaign=self.campaign,
            status='COMPLETED'
        ).select_related('campaign', 'donor').order_by('-donation_date')
        
        if self.date_from:
            queryset = queryset.filter(donation_date__date__gte=self.date_from)
        if self.date_to:
            queryset = queryset.filter(donation_date__date__lte=self.date_to)
            
        return queryset
    
    def get_report_stats(self):
        """Calculate report statistics"""
        total_donations = self.donations.count()
        total_amount = sum(donation.amount for donation in self.donations)
        
        return {
            'total_donations': total_donations,
            'total_amount': total_amount,
            'campaign_title': self.campaign.title,
            'donor_name': f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username,
            'date_from': self.date_from,
            'date_to': self.date_to,
        }
    
    def generate_csv(self):
        """Generate CSV report"""
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header information
        stats = self.get_report_stats()
        writer.writerow(['Donor Contribution Report'])
        writer.writerow(['Campaign:', stats['campaign_title']])
        writer.writerow(['Donor:', stats['donor_name']])
        writer.writerow(['Report Period:', f"{stats['date_from'] or 'All time'} to {stats['date_to'] or 'Present'}"])
        writer.writerow(['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow([])  # Empty row
        
        # Write summary
        writer.writerow(['Summary'])
        writer.writerow(['Total Donations:', stats['total_donations']])
        writer.writerow(['Total Amount:', f"₹{stats['total_amount']:.2f}"])
        writer.writerow([])  # Empty row
        
        # Write column headers
        writer.writerow([
            'Date',
            'Amount (₹)',
            'Payment Method',
            'Transaction ID',
            'Status',
            'Message'
        ])
        
        # Write donation data
        for donation in self.donations:
            writer.writerow([
                donation.donation_date.strftime('%Y-%m-%d %H:%M:%S'),
                f"{donation.amount:.2f}",
                donation.get_payment_method_display(),
                donation.transaction_id or 'N/A',
                donation.get_status_display(),
                donation.message or 'No message'
            ])
        
        return output.getvalue()
    
    def generate_pdf(self):
        """Generate PDF report"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1,  # Center alignment
            textColor=colors.HexColor('#2c3e50')
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#34495e')
        )
        
        normal_style = styles['Normal']
        
        # Get report statistics
        stats = self.get_report_stats()
        
        # Title
        title = Paragraph("Donor Contribution Report", title_style)
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # Report Information
        info_data = [
            ['Campaign:', stats['campaign_title']],
            ['Donor:', stats['donor_name']],
            ['Report Period:', f"{stats['date_from'] or 'All time'} to {stats['date_to'] or 'Present'}"],
            ['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 20))
        
        # Summary Section
        summary_heading = Paragraph("Summary", heading_style)
        elements.append(summary_heading)
        
        summary_data = [
            ['Total Donations:', str(stats['total_donations'])],
            ['Total Amount:', f"₹{stats['total_amount']:.2f}"],
        ]
        
        summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 20))
        
        # Donations Detail Section
        if self.donations.exists():
            details_heading = Paragraph("Donation Details", heading_style)
            elements.append(details_heading)
            
            # Table headers
            table_data = [
                ['Date', 'Amount (₹)', 'Payment Method', 'Transaction ID', 'Status']
            ]
            
            # Add donation rows
            for donation in self.donations:
                table_data.append([
                    donation.donation_date.strftime('%Y-%m-%d'),
                    f"₹{donation.amount:.2f}",
                    donation.get_payment_method_display(),
                    donation.transaction_id or 'N/A',
                    donation.get_status_display(),
                ])
            
            # Create table
            donations_table = Table(table_data, colWidths=[1.2*inch, 1*inch, 1.2*inch, 1.5*inch, 1*inch])
            donations_table.setStyle(TableStyle([
                # Header row styling
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                
                # Data rows styling
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                
                # Alternating row colors
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ]))
            elements.append(donations_table)
        else:
            no_data = Paragraph("No donations found for the selected criteria.", normal_style)
            elements.append(no_data)
        
        # Build PDF
        doc.build(elements)
        pdf_content = buffer.getvalue()
        buffer.close()
        
        return pdf_content
    
    def save_report_file(self, report_instance, content, file_extension):
        """Save report file to disk and update report instance"""
        # Create reports directory if it doesn't exist
        reports_dir = os.path.join(settings.MEDIA_ROOT, 'donor_reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"donor_report_{self.user.id}_{self.campaign.id}_{timestamp}.{file_extension}"
        file_path = os.path.join(reports_dir, filename)
        
        # Save file
        if file_extension == 'csv':
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                f.write(content)
        else:  # PDF
            with open(file_path, 'wb') as f:
                f.write(content)
        
        # Update report instance
        report_instance.file_path = f"donor_reports/{filename}"
        report_instance.file_size = os.path.getsize(file_path)
        report_instance.save()
        
        return file_path