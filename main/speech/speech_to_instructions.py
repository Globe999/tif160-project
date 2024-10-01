import speech_recognition as sr
import pyttsx3
# for index, name in enumerate(sr.Microphone.list_microphone_names()):
#     print(f'{index}, {name}')

class AudioInterface():
    def __init__(self) -> None:
        self.mic = sr.Microphone(device_index=1)
        self.r = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.mode = ""
        self.instructions = []
        
    def take_audio_input(self):
        
        with self.mic as source:
            print("Speak Anything!")
            audio = self.r.listen(source,timeout=2,phrase_time_limit=10)
        #load in audiofile

        #use googles text to speech to get text
        text = self.r.recognize_google(audio,show_all=True)['alternative'][0]
        words = text['transcript'].lower().split()
        return words
    
    def output_audio(self,string):
        self.engine.say(string)
        self.engine.runAndWait()
        
    def get_mode(self,modes):
        
        self.output_audio("What mode should i sort by")
        
        while True:
            words = self.take_audio_input()
        
            for mode in modes:
                if mode in words:
                    self.output_audio("Ok, i will sort by " + mode)
                    return mode
                
            self.output_audio("Please repeat what mode you want")


    def get_command(self,mode):
        
        shapes = ["cube","star","hexagon"]
        colors = ["red","green","blue"]
        size = ["big","small"]
        instructions = []
        
        
        # Define the text you want to convert to speech
        # Convert the text to speech
        self.output_audio("In what order shall i sort by " + mode)
        
        
        while True:
            words = self.take_audio_input()
            
            for word in words:
                if mode == "shape" and word in shapes:
                    instructions.append(word)
                elif mode == "size" and word in size:
                    instructions.append(word)
                elif mode == "color" and word in colors:
                    instructions.append(word)
                    
            if len(instructions):
                text = "Order set to "+ ", ".join(instructions) 
            
                self.output_audio(text)
                return instructions
            
            self.output_audio("Please repeat what order you want")

        
    def get_instructions(self):
        words = self.take_audio_input()     
        mode, order = self.get_command(words)
        
        
        # Define the text you want to convert to speech
        text = "Ofcourse, i will sort by " + mode
        # Convert the text to speech
        self.output_audio(text)
        return mode, order


# mode = get_mode(["shape","size","color"])
# instructions = get_command(mode)
# print(mode)
# print(instructions)