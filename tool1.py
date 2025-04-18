import os
import easyocr
from superagi.tools.base_tool import BaseTool
from pydantic import BaseModel, Field
from typing import Type

class EasyOCRInput(BaseModel):
    file_name: str = Field(..., description="Path of the image file for OCR")

class EasyOCRTool(BaseTool):
    name: str = "EasyOCR Tool"
    description: str = "Performs OCR on an image using EasyOCR"
    
    args_schema: Type[BaseModel] = EasyOCRInput

    def _execute(self, file_name: str) -> str:
        final_path = ResourceHelper.get_agent_read_resource_path(file_name)

        if not os.path.exists(final_path):
            raise FileNotFoundError(f"File '{file_name}' not found at {final_path}.")
        
        output_folder = r"SuperAGI\superagi\tools\ocr_engine" 
        os.makedirs(output_folder, exist_ok=True)
        
        output_file = os.path.join(output_folder, "ocr_result.txt")
        
        reader = easyocr.Reader(['en'])
        result = reader.readtext(final_path)
        
        text = ' '.join([item[1] for item in result])
        
        with open(output_file, "w") as file:
            file.write(text)

        print(f"OCR result saved to: {output_file}")
        
        return text

file_name = "test_screenshot1.png"
ocr_tool = EasyOCRTool()
extracted_text = ocr_tool._execute(file_name=file_name)

print("Extracted Text:", extracted_text)
