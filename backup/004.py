import os
import re
import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis


# app = FaceAnalysis(name="buffalo_l")
# app = FaceAnalysis(name="buffalo_s")
app = FaceAnalysis(name="buffalo_sc")
app.prepare(ctx_id=-1)  # CPU

# app = FaceAnalysis(name="buffalo_l")
# app.prepare(ctx_id=0)  # GPU


cap = cv2.VideoCapture(0)


def get_face_embedding(image_path):
    """Extract face embedding from an image"""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")

    faces = app.get(img)

    if len(faces) < 1:
        raise ValueError("No faces detected in the image")
    if len(faces) > 1:
        print("Warning: Multiple faces detected. Using first detected face")

    return faces[0].embedding


def compare_faces_cosine(emb1, emb2, threshold=0.65):
    """Compare two embeddings using cosine similarity"""
    similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
    return similarity, similarity > threshold


def list_folders(directory, pattern=None):
    if pattern is not None:
        return [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f)) and re.search(pattern, f)]
    else:
        return [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]


dirs = list_folders("./data")
print(f"names : {dirs}")


def list_files(directory, pattern=None):
    if pattern is None:
        return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    else:
        return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and re.search(pattern, f)]


for dir in dirs:
    files = list_files(f"./data/{dir}/")
    print(f"files : {files}")


emb_muysengly_1 = get_face_embedding("./data/MUY Sengly/001.jpg")
emb_muysengly_1 = get_face_embedding("./data/MUY Sengly/001.jpg")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_cvt = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    faces = app.get(frame_cvt)

    if len(faces) > 0:
        for face in faces:
            box = face.bbox.astype(np.int64)
            cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)

            # Compare faces
            similarity_score, is_same_person = compare_faces_cosine(face.embedding, emb_muysengly_1)

            print(f"Similarity Score: {similarity_score:.4f}")

            if similarity_score > 0.65:
                cv2.putText(
                    img=frame,
                    text="MUY Sengly",
                    org=(box[0], box[1] - 10),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.8,
                    color=(0, 255, 0),
                    thickness=2,
                )

    # Display output
    cv2.imshow("Face Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
