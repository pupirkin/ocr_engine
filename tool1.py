from superagi.tools.base_tool import BaseTool
from pydantic import BaseModel, Field
import easyocr

class EasyOCRInput(BaseModel):
    image_path: str = Field(..., description="Path to the image file for OCR")

class EasyOCRTool(BaseTool):
    name: str = "EasyOCR Tool"
    description: str = "Performs OCR on an image using EasyOCR"
    args_schema: EasyOCRInput

    def _execute(self, image_path: str) -> str:
        reader = easyocr.Reader(['en'])  # Specify the language(s)
        result = reader.readtext(image_path)
        text = ' '.join([item[1] for item in result])  # Extract text from OCR result
        return text
