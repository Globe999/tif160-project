import speech_recognition as sr
import pyttsx3
# for index, name in enumerate(sr.Microphone.list_microphone_names()):
#     print(f'{index}, {name}')


def get_text():
    
    r = sr.Recognizer()
    mic = sr.Microphone(device_index=1)

    with mic as source:
        print("Speak Anything!")
        audio = r.listen(source,timeout=2,phrase_time_limit=10)
    #load in audiofile

    #use googles text to speech to get text
    text = r.recognize_google(audio,show_all=True)['alternative'][0]
    words = text['transcript'].lower().split()
    print(words)
    return words

def get_mode(modes):
    
    
    engine = pyttsx3.init()
    # Define the text you want to convert to speech
    text = "What mode should i sort by"
    # Convert the text to speech
    engine.say(text)

    # # Run the speech engine
    engine.runAndWait()
    
    r = sr.Recognizer()
    mic = sr.Microphone(device_index=1)
    while True:
        with mic as source:
            print("Speak Anything!")
            audio = r.listen(source,timeout=2,phrase_time_limit=10)
        #load in audiofile

        #use googles text to speech to get text
        text = r.recognize_google(audio,show_all=True)['alternative'][0]
        words = text['transcript'].lower().split()
    
        for mode in modes:
            if mode in words:
                text = "Ok, i will sort by " + mode
        # Convert the text to speech
                engine.say(text)

                # # Run the speech engine
                engine.runAndWait()
                return mode
        
        text = "Please repeat what mode you want"
        # Convert the text to speech
        engine.say(text)

        # # Run the speech engine
        engine.runAndWait()


def get_command(mode):
    
    shapes = ["cube","star","hexagon"]
    colors = ["red","green","blue"]
    size = ["big","small"]
    instructions = []
    
    engine = pyttsx3.init()
    # Define the text you want to convert to speech
    text = "In what order shall i sort by " + mode
    # Convert the text to speech
    engine.say(text)

    # # Run the speech engine
    engine.runAndWait()
    
    r = sr.Recognizer()
    mic = sr.Microphone(device_index=1)
    while True:
        with mic as source:
            print("Speak Anything!")
            audio = r.listen(source,timeout=2,phrase_time_limit=10)
            
        text = r.recognize_google(audio,show_all=True)['alternative'][0]
        words = text['transcript'].lower().split()
        
        for word in words:
            if mode == "shape" and word in shapes:
                instructions.append(word)
            elif mode == "size" and word in size:
                instructions.append(word)
            elif mode == "color" and word in colors:
                instructions.append(word)
                
        if len(instructions):
            text = "Order set to "+ ", ".join(instructions) 
        
            engine.say(text)
            engine.runAndWait()
            return instructions
        
        text = "Please repeat what order you want"
        # Convert the text to speech
        engine.say(text)

        # # Run the speech engine
        engine.runAndWait()

    
def get_instructions():
    words = get_text()     
    mode, order = get_command(words)
    
    engine = pyttsx3.init()
    # Define the text you want to convert to speech
    text = "Ofcourse, i will sort by " + mode
    # Convert the text to speech
    engine.say(text)

    # # Run the speech engine
    engine.runAndWait()
    return mode, order


mode = get_mode(["shape","size","color"])
instructions = get_command(mode)
print(mode)
print(instructions)