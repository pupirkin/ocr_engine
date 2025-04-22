from superagi.tools.base_tool import BaseToolkit
from superagi.tools.external_tools.ocr_engine.tool1 import EasyOCRTool  # Путь к инструменту
from .tool1 import ScanDocumentTool  # Import the OCR tool you created (ScanDocumentTool)


class EasyOCRToolkit(BaseToolkit):
    name: str = "EasyOCR Toolkit"
    description: str = "Toolkit for performing OCR using EasyOCR"

    def get_tools(self):
        return [EasyOCRTool()]

    def get_env_keys(self):
        return []
