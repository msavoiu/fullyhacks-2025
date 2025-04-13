import os
from cerebras.cloud.sdk import Cerebras

def cerebrasRequest(head_bad, shoulders_bad, face_bad, head_drop, shoulder_hunch, face_closeness):
    client = Cerebras(
        api_key = "csk-49jf3vxhyjfhjyvj5n62nxdt6mhv48k2rrhh65ww5vc4nmtk"
    )

    if head_bad:
        head_desc = f"Their head has dropped {head_drop} pixels below their healthy sitting posture's position on the webcam"
    else:
        head_desc = None

    if shoulders_bad:
        shoulder_desc = f"Their shoulders are hunched up {shoulder_hunch} pixels closer to their head than their healthy sitting posture's position on the webcam"
    else:
        shoulder_desc = None

    if face_bad:
        face_desc = f"Their face is too close to the camera, {face_closeness} pixels more than a healthy viewing distance from the screen"
    else:
        face_desc = None

    prompt = f"Assume the role of mission control speaking to an astronaut in a spaceship. The astronaut is on a mission (doing work on their computer), and their main goal for the mission is to maintain good posture, which our Python backend is monitoring with computer vision. Currently, {head_desc}. {shoulder_desc}. {face_desc}. Can you give them a quick message telling them how the can correct their posture based on this information? Give specified suggestions based on which body parts are in suboptimal positions, and include a bit of explanation on what the specific aspects of their bad posture is doing to their body. Do not ask for any response or status update. Your message should read similar to a pop-up or reminder, have mission control-like language and not be longer than 2 or 3 sentences. Don't use excessive medical jargon in your status update, keep it to something most people can understand. Also, don't include the specific pixel information in your response. That data has only been provided to better your understanding of how severe their bad posture is."

    response = client.chat.completions.create(
        messages = [
            {
                "role": "user",
                "content": prompt,
            }
    ],
        model="llama-4-scout-17b-16e-instruct",
    )

    response_content = response.choices[0].message.content.strip().replace("\"", "")
    
    return response_content
