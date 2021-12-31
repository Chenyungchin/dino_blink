import cv2
import dlib
import numpy as np
import time

# module to find face characteristics
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
# module to find faces
detector = dlib.get_frontal_face_detector()

# lists for eye characteristics
right = [36, 37, 38, 39, 40, 41]
left = [42, 43, 44, 45, 46, 47]

def shape_to_np(shape, dtype="int"):
	# initialize the list of (x, y)-coordinates
	coords = np.zeros((68, 2), dtype=dtype)
	# loop over the 68 facial landmarks and convert them
	# to a 2-tuple of (x, y)-coordinates
	for i in range(0, 68):
		coords[i] = (shape.part(i).x, shape.part(i).y)
	# return the list of (x, y)-coordinates
	return coords

def eye_aspect_ratio(shape, side, frame):
    eye_features = []
    for index in side:
        eye_features.append(shape[index])
        cv2.circle(frame, (shape[index][0], shape[index][1]), 3, (0, 255, 255), 1)
    height_left = np.linalg.norm(eye_features[1]-eye_features[5])
    height_right = np.linalg.norm(eye_features[2]-eye_features[4])
    width = np.linalg.norm(eye_features[0]-eye_features[3])
    EAR = (height_left+height_right) / 2*width
    return round(EAR)


def calibrate_wink(cap, interval):
	left_val = []
	right_val = []
	t_start = time.time()
	while(time.time() - t_start < interval):
		ret, frame = cap.read()
		# transfer to graystyle
		gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		faces = detector(gray_frame, 1)
		wink = "none"
		for face in faces:
			shape = predictor(gray_frame, face)
			shape = shape_to_np(shape)
			EAR_left = eye_aspect_ratio(shape, left, frame)
			EAR_right = eye_aspect_ratio(shape, right, frame)
			left_val.append(EAR_left)
			right_val.append(EAR_right)
			if EAR_left < 300 or EAR_right < 300:
				EAR_ratio = EAR_left / EAR_right
				if EAR_ratio < 0.9:
					wink = "left"
				elif EAR_ratio > 1/0.9:
					wink = "right"
				else:
					wink = "both"
			if wink != "none":
				print(wink, (EAR_left, EAR_right))
		cv2.imshow('frame', frame)
		cv2.waitKey(1)
		# if cv2.waitKey(1) & 0xFF == ord('q'):
		# 	break
	
	return left_val, right_val

def motion(window, standard):
	left = 0
	right = 0
	for val in window:
		left += val[0]
		right += val[1]
	left /= 3
	right /= 3
	# print(window)
	# print(left, right)
	open_delta = abs(standard[0][0] - left) + abs(standard[0][1] - right)
	close_delta = abs(standard[1][0] - left) + abs(standard[1][1] - right)
	left_ratio = standard[2][1] / standard[2][0]
	right_ratio = standard[3][0] / standard[3][1]
	if open_delta < close_delta:
		return 'both eyes opened'
	if right / left > pow(left_ratio, 0.5):
		return 'left eye closed'
	if left / right > pow(right_ratio, 0.5):
		return 'right eye closed'
	return 'both eyes closed'
        

def detect_wink(cap, standard):
	window = []
	while(1):
		ret, frame = cap.read()
		gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		faces = detector(gray_frame, 1)
		for face in faces:
			shape = predictor(gray_frame, face)
			shape = shape_to_np(shape)
			EAR_left = eye_aspect_ratio(shape, left, frame)
			EAR_right = eye_aspect_ratio(shape, right, frame)
			window.append((EAR_left, EAR_right))
			if len(window) > 3:
				window.pop(0)
			wink = motion(window, standard)
		cv2.putText(frame, wink, (10, 120), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 255), 1, cv2.LINE_AA)
		cv2.imshow('frame', frame)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break


def ave(left, right):
    if len(left) == 0:
        return 0
    return sum(left) / len(left), sum(right) / len(right)

def calibration(cap):
	standard = []
	# both opened
	input('Keep both your eyes opened for 5 sec. Press enter to start')
	left, right = calibrate_wink(cap, 5)
	print(left, right)
	standard.append(ave(left, right))
	# both closed
	input('Keep both your eyes closed for 5 sec. Press enter to start')
	left, right = calibrate_wink(cap, 5)
	print(left, right)
	standard.append(ave(left, right))
	# left closed
	input('Keep your left eye closed for 5 sec. Press enter to start')
	left, right = calibrate_wink(cap, 5)
	print(left, right)
	standard.append(ave(left, right))
	# right closed
	input('Keep your right eye closed for 5 sec. Press enter to start')
	left, right = calibrate_wink(cap, 5)
	print(left, right)
	standard.append(ave(left, right))
	
	return standard


if __name__ == "__main__":
	cap = cv2.VideoCapture(0)
	standard = calibration(cap)
	print(standard)
	# standard = [(492.03125, 469.5625), (269.8378378378378, 268.0), (210.94594594594594, 265.4054054054054), (302.6216216216216, 215.64864864864865)]
	detect_wink(cap, standard)
	cap.release()
	cv2.destroyAllWindows()
    