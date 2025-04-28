from superagi.tools.base_tool import BaseToolkit
from superagi.tools.external_tools.ocr_engine.tool1 import EasyOCRTool  # Keep import EasyOCRTool

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
        return [EasyOCRTool()]  # Return your original tool

    def get_env_keys(self):
        """
        This method defines environment keys needed by the toolkit.
        """
        return []
