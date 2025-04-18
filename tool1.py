import os
from superagi.tools.base_tool import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import easyocr

class EasyOCRInput(BaseModel):
    image_path: str = Field(..., description="Path to the image file for OCR")

class EasyOCRTool(BaseTool):
    name: str = "EasyOCR Tool"
    description: str = "Performs OCR on an image using EasyOCR"
    
    args_schema: Type[BaseModel] = EasyOCRInput

    def _execute(self, image_path: str = None) -> str:
        output_folder = r"D:\Ofound\OCR_Results"
        os.makedirs(output_folder, exist_ok=True)  
        
        output_file = os.path.join(output_folder, "ocr_result.txt")
        
        reader = easyocr.Reader(['en'])  # Specify the language(s)
        result = reader.readtext(image_path)
        text = ' '.join([item[1] for item in result])  # Extract text from OCR result
        
        with open(output_file, "w") as file:
            file.write(text)
        
        print(f"Results saved to: {output_file}")
        return text

image_path = r"D:\Ofound\test_screenshot1.png"

ocr_tool = EasyOCRTool()
text = ocr_tool._execute(image_path=image_path)

print("Extracted text:", text)
