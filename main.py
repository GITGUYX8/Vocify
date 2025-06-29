import torch
from TTS.api import TTS
import gradio as gr


#we are using cuda in this if cuda not there then it depends on cpu

device ="cuda" if torch.cuda.is_available() else "cpu"

#function for generating speech

def generate_audio(text="As the train rumbled across the vast countryside, "
"Maya sat by the window, watching the ever-changing landscape blur into "
"streaks of green, gold, and blue. Each passing village whispered stories "
"of lives she would never know—children running barefoot through fields, "
"elders resting under banyan trees, and smoke curling up from small clay stoves. "
"The wind carried the scent of damp earth and distant rain, and for a moment, "
"time seemed to pause. She thought about how strange it was that the world could be so "
"big and yet so intimately connected. The people she would never meet still felt familiar, "
"like echoes of memories from another life. She sipped her tea, now lukewarm, and leaned her head "
"against the glass, letting the rhythmic clatter of the tracks lull her into thought."
" Somewhere ahead was her destination, a city bustling with noise and lights, but for"
" now, in this quiet cocoon of movement and reflection, she allowed herself to simply be"
" — just a traveler, in transit, wrapped in the gentle hum of the journey."):
    # Init TTS with the target model name
    #model in english
    tts =TTS(model_name="tts_models/en/ljspeech/fast_pitch").to("cpu")
    # tts =TTS(model_name="tts_models/en/ljspeech/overflow").to(device)

    # Run TTS
    tts.tts_to_file(text=text,
                    file_text="outputs/output.wav" 
                    ,speed=1 ) 
    return "outputs/output.wav"#return actual path of audio file

print(generate_audio())

#to create an interface between the gradient and the tts

# demo = gr.Interface(
#     fn=generate_audio,
#     inputs=[gr.Text(label="Text"),],
#     outputs=[gr.Audio{label="Audio"},],
# )
# demo.launch()