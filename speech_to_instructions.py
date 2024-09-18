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



def get_command(words):
    
    shapes = ["cube","star","hexagon"]
    colors = ["red","green","blue"]
    size = ["big","small"]
    modes = ["shape","size","color"]
    
    instructions = []
    mode = "NONE"
    for word in words:
        
        # if(word in colors):
        #     instruction = []
        #     instruction.append(word)
        # elif(word in shapes):
        #     instruction.append(word)
        #     instructions.append(instruction)
        if word in modes:
            mode = word
        if mode == "shape" and word in shapes:
            instructions.append(word)
        elif mode == "size" and word in size:
            instructions.append(word)
        elif mode == "color" and word in colors:
            instructions.append(word)
            
    if len(instructions) < 2 or mode =="NONE":
        print("Please repeat your instructions")
        return 0,[]
    else:
        print("mode is set to: " + mode.upper())
        print("Order to sort in: ")
        for instruction in instructions:
            print(instruction.upper())
                
        return mode, instructions
    
    
words = get_text()     
mode, order = get_command(words)

engine = pyttsx3.init()

# Define the text you want to convert to speech
text = "Ofcourse, i will sort by " + mode
print(text)
# Convert the text to speech
engine.say(text)

# # Run the speech engine
engine.runAndWait()
