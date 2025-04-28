from superagi.tools.base_tool import BaseToolkit
from superagi.tools.external_tools.ocr_engine.tool1 import ScanDocumentTool  # Импорт правильного класса

class EasyOCRToolkit(BaseToolkit):
    """
    Toolkit for performing OCR using EasyOCR.
    """
    name: str = "EasyOCR Toolkit"
    description: str = "Toolkit for scanning documents using EasyOCR"

    def get_tools(self):
        """
        This method returns the list of tools included in this toolkit.
        """
        return [ScanDocumentTool()]  # Тоже поменяли на ScanDocumentTool

    def get_env_keys(self):
        """
        This method defines environment keys needed by the toolkit.
        """
        return []
