import pyttsx3

def text_to_speech(text):
    # Initialize the text-to-speech engine
    engine = pyttsx3.init()

    # Set the voice to a female voice
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[2].id)

    # Set the rate of speech
    engine.setProperty('rate', 150)

    # Set the volume between 0 and 1
    engine.setProperty('volume', 1.0)

    # Convert text to speech
    engine.say(text)
    engine.save_to_file(text=text, filename="speech.mp3")

    # Wait for the speech to finish
    engine.runAndWait()
    engine.stop()
    print("Text to speech complete")

# Reference:
# https://gist.github.com/blacksmithop/e290db0e2308a0d76cefdda29295b662
class TextToSpeech:
    def __init__(self):
        # Initialize the text-to-speech engine
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 125)

        # Set the voice to a female voice (1)
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[2].id)

    def convert(self, text:str, filename: str="hello.mp3"):
        self.engine.save_to_file(text, filename)
        self.engine.runAndWait()

    def speak(self, text:str):
        self.engine.say(text)
        self.engine.runAndWait()
        print(f"Spoke: {text}")

if __name__ == "__main__":
    tts = TextToSpeech()
    tts.convert(text='The quick brown fox jumps over the lazy dog.', filename='hello.mp3')
    tts.speak(text='The quick brown fox jumps over the lazy dog.')