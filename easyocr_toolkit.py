from superagi.tools.base_tool import BaseToolkit
from superagi.tools.external_tools.ocr_engine.tool1 import ScanDocumentTool  # Correct import path
# Ensure the right import from the tool1 file

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
        return [ScanDocumentTool()]  # Correct tool name from tool1

    def get_env_keys(self):
        """
        This method defines environment keys needed by the toolkit.
        """
        return []
