class DialectDetector:

    def __init__(self):
        self.accent = "Unknown"

    def detect_accent(self, region):
        if region == "Ahmedabad":
            self.accent = "Ahmedabad Gujarati"
        elif region == "Surat":
            self.accent = "Surti Gujarati"
        elif region == "Saurashtra":
            self.accent = "Kathiawadi Gujarati"
        else:
            self.accent = "Gujarati"

        return self.accent
