from superagi.tools.base_tool import BaseToolkit
from superagi.tools.ocr_engine.tool1 import EasyOCRTool

class EasyOCRToolkit(BaseToolkit):
    name: str = "EasyOCR Toolkit"
    description: str = "Toolkit for performing OCR using EasyOCR"

    def get_tools(self):
        return [EasyOCRTool()]
