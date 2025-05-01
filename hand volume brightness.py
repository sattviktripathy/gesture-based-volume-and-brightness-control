import cv2
import numpy as np
import mediapipe as mp
import screen_brightness_control as sbc
from math import hypot
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import time
from collections import deque

def main():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volRange = volume.GetVolumeRange()
    minVol, maxVol, _ = volRange

    mpHands = mp.solutions.hands
    hands = mpHands.Hands(
        static_image_mode=False,
        model_complexity=1,
        min_detection_confidence=0.75,
        min_tracking_confidence=0.75,
        max_num_hands=2)
    
    draw = mp.solutions.drawing_utils
    cap = cv2.VideoCapture(0)

    brightness_buffer = deque(maxlen=5)
    volume_buffer = deque(maxlen=5)

    current_brightness = sbc.get_brightness()[0]
    brightness_buffer.extend([current_brightness] * 5)
    
    current_volume = volume.GetMasterVolumeLevelScalar() * 100
    volume_level = np.interp(current_volume, [0, 100], [minVol, maxVol])
    volume_buffer.extend([volume_level] * 5)

    min_distance = 30
    max_distance = 180

    distance_points = [30, 60, 90, 120, 150, 165, 180]
    value_points = [0, 30, 50, 70, 85, 90, 100]

    last_update_time = time.time()
    update_interval = 0.1
    
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            frame = cv2.flip(frame, 1)
            frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            processed = hands.process(frameRGB)

            cv2.putText(frame, f'Brightness: {int(current_brightness)}%', (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f'Volume: {int(np.interp(volume.GetMasterVolumeLevelScalar(), [0, 1], [0, 100]))}%', 
                        (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.putText(frame, f'Min: {min_distance}px | Max: {max_distance}px', (10, 110), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            left_landmark_list, right_landmark_list = get_left_right_landmarks(frame, processed, draw, mpHands)
            
            current_time = time.time()
            should_update = (current_time - last_update_time) >= update_interval

            if left_landmark_list and len(left_landmark_list) >= 2:
                left_distance = get_distance(frame, left_landmark_list)
                if left_distance:
                    left_distance = max(min_distance, min(left_distance, max_distance))
                    new_brightness = custom_mapping(left_distance, distance_points, value_points)
                    brightness_buffer.append(new_brightness)
                    current_brightness = sum(brightness_buffer) / len(brightness_buffer)
                    
                    if should_update:
                        sbc.set_brightness(int(current_brightness))

                    height, width, _ = frame.shape
                    cv2.rectangle(frame, (50, 150), (85, 400), (255, 0, 0), 3)
                    cv2.rectangle(frame, (50, int(400 - current_brightness * 2.5)), (85, 400), (255, 0, 0), cv2.FILLED)

            if right_landmark_list and len(right_landmark_list) >= 2:
                right_distance = get_distance(frame, right_landmark_list)
                if right_distance:
                    right_distance = max(min_distance, min(right_distance, max_distance))
                    vol_percentage = custom_mapping(right_distance, distance_points, value_points)
                    new_vol = np.interp(vol_percentage, [0, 100], [minVol, maxVol])
                    volume_buffer.append(new_vol)
                    vol_to_set = sum(volume_buffer) / len(volume_buffer)

                    if should_update:
                        volume.SetMasterVolumeLevel(vol_to_set, None)

                    vol_percentage = np.interp(vol_to_set, [minVol, maxVol], [0, 100])
                    height, width, _ = frame.shape
                    cv2.rectangle(frame, (width - 85, 150), (width - 50, 400), (0, 0, 255), 3)
                    cv2.rectangle(frame, (width - 85, int(400 - vol_percentage * 2.5)), (width - 50, 400), (0, 0, 255), cv2.FILLED)

            if should_update:
                last_update_time = current_time
            
            cv2.imshow('Gesture Control', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()

def custom_mapping(distance, distance_points, value_points):
    if distance <= distance_points[0]:
        return value_points[0]
    
    if distance >= distance_points[-1]:
        return value_points[-1]
    
    for i in range(len(distance_points) - 1):
        if distance_points[i] <= distance < distance_points[i + 1]:
            d1, d2 = distance_points[i], distance_points[i + 1]
            v1, v2 = value_points[i], value_points[i + 1]
            return v1 + (v2 - v1) * (distance - d1) / (d2 - d1)
    
    return 0

def get_left_right_landmarks(frame, processed, draw, mpHands):
    left_landmark_list = []
    right_landmark_list = []

    if processed.multi_hand_landmarks:
        hands_info = []
        for idx, handLms in enumerate(processed.multi_hand_landmarks):
            if idx < len(processed.multi_handedness):
                hand_type = processed.multi_handedness[idx].classification[0].label
                hands_info.append((handLms, hand_type))
            
            draw.draw_landmarks(frame, handLms, mpHands.HAND_CONNECTIONS)
        
        for handLms, hand_type in hands_info:
            landmarks = []
            for idx, found_landmark in enumerate(handLms.landmark):
                height, width, _ = frame.shape
                x, y = int(found_landmark.x * width), int(found_landmark.y * height)
                if idx == 4 or idx == 8:
                    landmarks.append([idx, x, y])
            
            if hand_type == "Left":
                right_landmark_list = landmarks
            elif hand_type == "Right":
                left_landmark_list = landmarks

    return left_landmark_list, right_landmark_list

def get_distance(frame, landmark_list):
    if len(landmark_list) < 2:
        return None
        
    (x1, y1), (x2, y2) = (landmark_list[0][1], landmark_list[0][2]), \
        (landmark_list[1][1], landmark_list[1][2])

    cv2.circle(frame, (x1, y1), 10, (0, 255, 0), cv2.FILLED)
    cv2.circle(frame, (x2, y2), 10, (0, 255, 0), cv2.FILLED)
    cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
    
    L = hypot(x2 - x1, y2 - y1)
    
    midpoint = ((x1 + x2) // 2, (y1 + y2) // 2)
    cv2.putText(frame, f'{int(L)}px', midpoint, 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                
    return L

if __name__ == '__main__':
    main()