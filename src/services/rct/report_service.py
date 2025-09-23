import os
import json
from fpdf import FPDF
from dataclasses import asdict
from src.utils.config import UserStoryDto

def generate_report_file(doc, stories, REPORT_DIR):
    """
    """
    data = [asdict(UserStoryDto(
      story_id=story.story_id,
        doc_id=story.doc_id,
        returnment_id=story.requirement_id,
        user_story_text=story.user_story_text,
        acceptance_criteria=story.acceptance_criteria,
        test_case=story.test_case,
        created_at=story.created_at.isoformat() if story.created_at else None
    )) for story in stories]
    file_path = f"{REPORT_DIR}/report_{doc.doc_id}.json"
    report_type = "json"
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)
    return file_path, report_type


def download_report_file(report, report_type):
    """
    """
    file_path = report.file_path
    with open(file_path, 'r', encoding='utf-8') as f:
        content = json.load(f)

    if os.path.exists(file_path):
        if report_type == "json":
            return file_path
        
        elif report_type == "csv":
            csv_path = file_path.replace('.json', '.csv')
            with open(csv_path, 'w', encoding='utf-8') as csv_file:
                headers = content[0].keys()
                csv_file.write(','.join(headers) + '\n')
                for entry in content:
                    csv_file.write(','.join(str(entry[h]) for h in headers) + '\n')
            return csv_path
        
        elif report_type == "pdf":
            pdf_path = file_path.replace('.json', '.pdf')
            
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            for entry in content:
                for key, value in entry.items():
                    pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)
                pdf.ln(10)
            pdf.output(pdf_path)
            return pdf_path
