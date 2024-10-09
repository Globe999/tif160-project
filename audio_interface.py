import speech_recognition as sr
import pyttsx3


class AudioInterface:
    def __init__(self) -> None:
        self.mic = sr.Microphone(device_index=0)
        self.r = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.mode = ""
        self.instructions = []

    def take_audio_input(self):

        with self.mic as source:
            print("Speak Anything!")
            audio = self.r.listen(source, timeout=2, phrase_time_limit=10)
        # load in audiofile

        # use googles text to speech to get text
        text = self.r.recognize_google(audio, show_all=True)["alternative"][0]
        if text:
            words = text["transcript"].lower().split()
            return words
        else:
            return 0

    def output_audio(self, string):
        self.engine.say(string)
        self.engine.runAndWait()

    def get_sort_mode(self, modes=["color", "size", "shape"]):
        self.output_audio("What mode should i sort by")
        while True:
            words = self.take_audio_input()
            if words:
                for mode in modes:
                    if mode in words:
                        self.output_audio("Ok, i will sort by " + mode)
                        return mode

            self.output_audio("Please repeat what mode you want")

    def get_sort_order(self, mode):

        shapes = ["cube", "star", "hexagon", "cylinder"]
        colors = ["red", "green", "blue", "white"]
        size = ["big", "small"]
        instructions = []
        # Define the text you want to convert to speech
        # Convert the text to speech
        text = "In what order shall i sort by " + mode
        self.output_audio(text)

        while True:
            words = self.take_audio_input()
            if words:
                for word in words:
                    if mode == "shape" and word in shapes:
                        instructions.append(word)
                    elif mode == "size" and word in size:
                        instructions.append(word)
                    elif mode == "color" and word in colors:
                        instructions.append(word)

            if len(instructions):
                text = "Order set to " + ", ".join(instructions)

                self.output_audio(text)
                return instructions

            self.output_audio("Please repeat what order you want")
