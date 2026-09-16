from User import User
from VoiceInput import VoiceInput
from SpeechToText import SpeechToText
from DialectDetector import DialectDetector
from AIProcessor import AIProcessor
from TextToSpeech import TextToSpeech
from Conversation import Conversation


user = User(
    "asmi@example.com",
    "Asmi Jain",
    "Ahmedabad",
    "18-24",
    "Female"
)

print("USER DETAILS")
user.display_user()

print("\nVOICE INPUT")
voice = VoiceInput("user_voice.wav", 5)
voice.start_recording()
voice.stop_recording()

print("\nSPEECH TO TEXT")
speech = SpeechToText()
text = speech.transcribe(voice.get_audio())
print("Transcribed Text:", text)

print("\nDIALECT DETECTION")
dialect = DialectDetector()
accent = dialect.detect_accent(user.region)
print("Detected Accent:", accent)

print("\nAI PROCESSOR")
ai = AIProcessor()
response = ai.generate_response(text)
print("AI Response:", response)

print("\nTEXT TO SPEECH")
tts = TextToSpeech()
audio = tts.convert_to_speech(response)
print("Audio File:", audio)

print("\nCONVERSATION")
conversation = Conversation("conv001", user)
conversation.add_message("User", text)
conversation.add_message("Assistant", response)
conversation.display_conversation()
