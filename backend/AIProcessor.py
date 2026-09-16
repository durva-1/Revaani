class AIProcessor:

    def __init__(self):
        self.language = "Gujarati"

    def generate_response(self, user_message):
        if "કેમ છો" in user_message:
            return "હું સારું છું. તમે કેમ છો?"
        elif "નમસ્તે" in user_message:
            return "નમસ્તે! હું ReVaani છું."
        else:
            return "તમારો સંદેશ સમજાયો. હું તમને કેવી રીતે મદદ કરી શકું?"
