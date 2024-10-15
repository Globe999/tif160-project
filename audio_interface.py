import speech_recognition as sr
import pyttsx3


class AudioInterface:
    def __init__(self) -> None:
        self.mic = sr.Microphone(device_index=0)
        self.r = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.mode = []
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
                for m in modes:
                    if m in words:
                        self.mode.append(m)
                t = 0
                for m in self.mode:
                    if t == 0:
                        self.output_audio("Ok, i will sort by " + m)
                        t = 1
                    else:
                        self.output_audio("and m")
                        
                return self.mode
            self.output_audio("Please repeat what mode you want")

    def get_sort_order(self, mode):

        shapes = ["cube", "star", "hexagon", "cylinder"]
        colors = ["red", "green", "blue", "white"]
        size = ["big", "small"]
        instructions = []
        # Define the text you want to convert to speech
        # Convert the text to speech
        text = "In what order shall i sort "
        self.output_audio(text)
        # if len(mode)==1:
        #     while True:
        #         words = self.take_audio_input()
        #         if words:
        #             for word in words:
        #                 if mode == "shape" and word in shapes:
        #                     instructions.append(word)
        #                 elif mode == "size" and word in size:
        #                     instructions.append(word)
        #                 elif mode == "color" and word in colors:
        #                     instructions.append(word)

        #         if len(instructions):
        #             text = "Order set to " + ", ".join(instructions)

        #             self.output_audio(text)
        #             return instructions

        #         self.output_audio("Please repeat what order you want")
        # elif len(mode)==2:
        while True:
            words = self.take_audio_input()
            if words:
                for m in mode:
                    temp_list = []
                    for word in words:
                        if m == "shape" and word in shapes:
                            temp_list.append(word)
                        elif m == "size" and word in size:
                            temp_list.append(word)
                        elif m == "color" and word in colors:
                            temp_list.append(word)
                    instructions.append(temp_list)
            if len(instructions)==1:
                text = "Order set to " + ", ".join(instructions[0])
                self.output_audio(text)
                return instructions
            elif len(instructions)==2:
                text = "Order set to " + ", ".join(instructions[0]) + "and then ".join(instructions[1])
                self.output_audio(text)
                return instructions

            self.output_audio("Please repeat what order you want")