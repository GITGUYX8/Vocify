import torch
from TTS.api import TTS
import gradio as gr


#we are using cuda in this if cuda not there then it depends on cpu

device ="cuda" if torch.cuda.is_available() else "cpu"

#function for generating speech

def generate_audio(text="let the world follow the steps of the great leader"):
    # Init TTS with the target model name
    #model in english
    tts =TTS(model_name="tts_models/en/ljspeech/fast_pitch").to("cpu")
    # tts =TTS(model_name="tts_models/en/ljspeech/overflow").to(device)

    # Run TTS
    tts.tts_to_file(text=text,file_text="outputs/output.wav") 
    return "outputs/output.wav"#return actual path of audio file

print(generate_audio())

#to create an interface between the gradient and the tts

# demo = gr.Interface(
#     fn=generate_audio,
#     inputs=[gr.Text(label="Text"),],
#     outputs=[gr.Audio{label="Audio"},],
# )
# demo.launch()