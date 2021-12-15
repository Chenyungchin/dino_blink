import cv2
import dlib
import numpy as np

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

def eye_aspect_ratio(shape, side):
    eye_features = []
    for index in side:
        eye_features.append(shape[index])
    height_left = np.linalg.norm(eye_features[1]-eye_features[5])
    height_right = np.linalg.norm(eye_features[2]-eye_features[4])
    width = np.linalg.norm(eye_features[0]-eye_features[3])
    EAR = (height_left+height_right) / 2*width
    return round(EAR)


def detect_wink():
	cap = cv2.VideoCapture(0)

	while(True):
		ret, frame = cap.read()
		cv2.imshow('frame', frame)
		# transfer to graystyle
		gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		faces = detector(gray_frame, 1)
		wink = "none"
		for face in faces:
			shape = predictor(gray_frame, face)
			shape = shape_to_np(shape)
			EAR_left = eye_aspect_ratio(shape, left)
			EAR_right = eye_aspect_ratio(shape, right)
			if EAR_left < 300 or EAR_right < 300:
				EAR_ratio = EAR_left / EAR_right
				if EAR_ratio < 0.9:
					wink = "left"
				elif EAR_ratio > 1/0.9:
					wink = "right"
				else:
					wink = "both"
			if wink != "none":
				print(wink)
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break

	cap.release()
	cv2.destroyAllWindows()
 
if __name__ == "__main__":
    detect_wink()