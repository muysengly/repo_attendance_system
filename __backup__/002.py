import cv2
import insightface
import numpy as np
from insightface.app import FaceAnalysis

# Initialize face analysis model
app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])  # Use 'CUDAExecutionProvider' for GPU
# app.prepare(ctx_id=0)  # ctx_id=-1 for CPU, 0 for GPU
app.prepare(ctx_id=-1)  # ctx_id=-1 for CPU, 0 for GPU

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


def compare_faces_l2_dist(emb1, emb2, threshold=0.65):
    """Compare two embeddings using L2 distance"""
    diff = np.subtract(emb1, emb2)
    dist = np.sum(np.square(diff))
    return dist, dist < threshold


emb1 = get_face_embedding("./data/face1.jpg")


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

            # Get face embedding
            emb = face.embedding

            # Compare faces
            # similarity_score, is_same_person = compare_faces_cosine(emb, emb1)
            similarity_score, is_same_person = compare_faces_l2_dist(emb, emb1)

            print(f"Similarity Score: {similarity_score:.4f}")
            print(f"Same person? {'YES' if is_same_person else 'NO'}")

    # Display output
    cv2.imshow("Face Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
