import re
import pandas as pd
from typing import List
import os
import PyPDF2
import argparse
from dataclasses import dataclass

@dataclass
class Project:
    name: str
    generator_type: str
    capacity: str
    location: str = ""
    in_service_date: str = ""
    cost: str = ""
    owner: str = ""

class UtilityProjectParser:
    def __init__(self):
        self.projects = []
        
    def parse_document(self, text: str) -> List[Project]:
        """Parse the document text to extract project information."""
        self.projects = []
        
        # Look for NGCC projects
        ngcc_matches = re.finditer(r'(?:construction of|construct) (?:an?|two)? ?(?:approximately)? ?(\d+) (?:MW|megawatt).*?(?:natural gas combined cycle|NGCC).*?(?:at|facility|unit) ([\w\s.]+?) (?:in|Generating|Station)', text, re.IGNORECASE)
        for match in ngcc_matches:
            capacity = match.group(1)
            location_info = match.group(2).strip()
            
            # Extract the project name
            project_name_match = re.search(fr'{location_info}.*?(?:\(([^)]+)\)|[""]([^""]+)[""])', text[match.start():], re.IGNORECASE)
            project_name = "NGCC Unit"
            if project_name_match:
                project_name = project_name_match.group(1) or project_name_match.group(2)
                
            # Extract in-service date
            service_date_match = re.search(fr'{project_name}.*?(?:in service|operational) (?:by|in) (\d{{4}})', text[match.start():], re.IGNORECASE)
            in_service_date = ""
            if service_date_match:
                in_service_date = service_date_match.group(1)
                
            # Extract cost
            cost_match = re.search(fr'{project_name}.*?(?:cost|approximately) \$([\d.]+) (?:billion|million)', text[match.start():], re.IGNORECASE)
            cost = ""
            if cost_match:
                cost_value = float(cost_match.group(1))
                if "billion" in text[cost_match.start():cost_match.end()].lower():
                    cost = f"${cost_value} billion"
                else:
                    cost = f"${cost_value} million"
            
            self.projects.append(Project(
                name=project_name,
                generator_type="Natural Gas Combined Cycle",
                capacity=f"{capacity} MW",
                location=location_info,
                in_service_date=in_service_date,
                cost=cost
            ))
            
        # Look for battery storage projects
        battery_matches = re.finditer(r'(?:construction of|construct) (?:an?|two)? ?(\d+) (?:MW|megawatt),? (\d+)[-\s]hour.*?(?:battery|BESS).*?(?:at|facility) ([\w\s.]+?)(?:in|Generating|Station)', text, re.IGNORECASE)
        for match in battery_matches:
            capacity = match.group(1)
            duration = match.group(2)
            location_info = match.group(3).strip()
            
            # Extract the project name
            project_name_match = re.search(fr'{location_info}.*?(?:\(([^)]+)\)|[""]([^""]+)[""])', text[match.start():], re.IGNORECASE)
            project_name = "Battery Storage"
            if project_name_match:
                project_name = project_name_match.group(1) or project_name_match.group(2)
                
            # Extract in-service date
            service_date_match = re.search(fr'{project_name}.*?(?:in service|operational) (?:by|in) (\d{{4}})', text[match.start():], re.IGNORECASE)
            in_service_date = ""
            if service_date_match:
                in_service_date = service_date_match.group(1)
                
            # Extract cost
            cost_match = re.search(fr'{project_name}.*?(?:cost|approximately) \$([\d.]+) (?:billion|million)', text[match.start():], re.IGNORECASE)
            cost = ""
            if cost_match:
                cost_value = float(cost_match.group(1))
                if "billion" in text[cost_match.start():cost_match.end()].lower():
                    cost = f"${cost_value} billion"
                else:
                    cost = f"${cost_value} million"
            
            self.projects.append(Project(
                name=project_name,
                generator_type=f"Battery Energy Storage ({duration}-hour)",
                capacity=f"{capacity} MW",
                location=location_info,
                in_service_date=in_service_date,
                cost=cost
            ))
            
        # Look for environmental upgrade projects like SCR
        env_matches = re.finditer(r'(?:construction of|construct) (?:an?|two)? ?(?:selective catalytic reduction|SCR).*?(?:at|facility) ([\w\s.]+?) (?:in|Generating|Station).*?(?:for|unit) ([\w\s\d.]+)', text, re.IGNORECASE)
        for match in env_matches:
            location_info = match.group(1).strip()
            unit_info = match.group(2).strip()
            
            # Extract in-service date
            service_date_match = re.search(r'SCR.*?(?:operational|in service) (?:by|in) (\d{{4}})', text[match.start():], re.IGNORECASE)
            in_service_date = ""
            if service_date_match:
                in_service_date = service_date_match.group(1)
                
            # Extract cost
            cost_match = re.search(r'SCR.*?(?:cost|approximately) \$([\d.]+) (?:billion|million)', text[match.start():], re.IGNORECASE)
            cost = ""
            if cost_match:
                cost_value = float(cost_match.group(1))
                if "billion" in text[cost_match.start():cost_match.end()].lower():
                    cost = f"${cost_value} billion"
                else:
                    cost = f"${cost_value} million"
            
            self.projects.append(Project(
                name=f"SCR for {unit_info}",
                generator_type="Environmental Control (SCR)",
                capacity="N/A",
                location=location_info,
                in_service_date=in_service_date,
                cost=cost
            ))
            
        return self.projects
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert projects to a pandas DataFrame."""
        if not self.projects:
            return pd.DataFrame(columns=["Project Name", "Generator Type", "Capacity", "Location", "In-Service Date", "Estimated Cost"])
        
        data = {
            "Project Name": [],
            "Generator Type": [],
            "Capacity": [],
            "Location": [],
            "In-Service Date": [],
            "Estimated Cost": []
        }
        
        for project in self.projects:
            data["Project Name"].append(project.name)
            data["Generator Type"].append(project.generator_type)
            data["Capacity"].append(project.capacity)
            data["Location"].append(project.location)
            data["In-Service Date"].append(project.in_service_date)
            data["Estimated Cost"].append(project.cost)
            
        return pd.DataFrame(data)
    
    def read_file(self, file_path: str) -> str:
        """Read the content of a file based on its extension."""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        # elif ext == '.docx':
        #     doc = docx.Document(file_path)
        #     return '\n'.join([para.text for para in doc.paragraphs])
        elif ext == '.pdf':
            text = ""
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page_num in range(len(pdf_reader.pages)):
                    text += pdf_reader.pages[page_num].extract_text()
            return text
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    
    def process_file(self, file_path: str) -> pd.DataFrame:
        """Process a file and return a DataFrame of projects."""
        text = self.read_file(file_path)
        self.parse_document(text)
        return self.to_dataframe()

def main():
    parser = argparse.ArgumentParser(description='Extract utility project details from documents')
    parser.add_argument('file_path', help='Path to the document file (.txt, .docx, or .pdf)')
    parser.add_argument('--output', help='Output file path (.csv or .xlsx)')
    
    args = parser.parse_args()
    
    processor = UtilityProjectParser()
    
    try:
        df = processor.process_file(args.file_path)
        
        if df.empty:
            print("No projects found in the document.")
            return
        
        print("\nProject Proposals Found:")
        print(df.to_string(index=False))
        
        if args.output:
            ext = os.path.splitext(args.output)[1].lower()
            if ext == '.csv':
                df.to_csv(args.output, index=False)
            elif ext == '.xlsx':
                df.to_excel(args.output, index=False)
            else:
                df.to_csv(args.output + '.csv', index=False)
            print(f"\nOutput saved to {args.output}")
            
    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    main()
