import cv2
import face_recognition
import numpy as np
import pickle
import os
from datetime import datetime, timezone
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
# =========================================================
# SUPABASE CONFIGURATION
# =========================================================

SUPABASE_URL = "https://wwfraugezutgfefjvlwq.supabase.co"

# YAHAN APNI EXISTING SUPABASE KEY RAKHO
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

print("✅ Supabase client created")


# =========================================================
# LOAD ENCODINGS
# =========================================================

print("📦 Loading EncodeFile.p...")

try:
    with open("EncodeFile.p", "rb") as file:
        encodeListKnownWithIds = pickle.load(file)

    encodeListKnown = encodeListKnownWithIds[0]
    studentIds = encodeListKnownWithIds[1]

    print(f"✅ Loaded {len(encodeListKnown)} face encodings")
    print(f"✅ Student IDs: {studentIds}")

except Exception as e:
    print(f"❌ Could not load EncodeFile.p: {e}")
    exit()


# =========================================================
# CAMERA
# =========================================================

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Camera could not be opened")
    exit()

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print("📷 Camera started")
print("👉 Press Q to close")


# =========================================================
# VARIABLES
# =========================================================

modeType = 0
counter = 0
id = -1
imgStudent = None

lastRecognizedId = None
attendanceMarked = False


# =========================================================
# MAIN LOOP
# =========================================================

while True:

    success, img = cap.read()

    if not success:
        print("❌ Could not read camera frame")
        continue

    # Resize for faster processing
    imgS = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)

    # Convert BGR → RGB
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    # Detect faces
    faceCurFrame = face_recognition.face_locations(imgS)

    # Encode detected faces
    encodeCurFrame = face_recognition.face_encodings(
        imgS,
        faceCurFrame
    )


    # =====================================================
    # FACE RECOGNITION
    # =====================================================

    for encodeFace, faceLoc in zip(
        encodeCurFrame,
        faceCurFrame
    ):

        matches = face_recognition.compare_faces(
            encodeListKnown,
            encodeFace,
            tolerance=0.50
        )

        faceDis = face_recognition.face_distance(
            encodeListKnown,
            encodeFace
        )

        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:

            id = str(studentIds[matchIndex])

            print(f"✅ Recognized Student ID: {id}")

            # Face location coordinates
            y1, x2, y2, x1 = faceLoc

            # Convert back because image was scaled 1/4
            y1 *= 4
            x2 *= 4
            y2 *= 4
            x1 *= 4

            # Draw rectangle
            cv2.rectangle(
                img,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                3
            )

            # Student information
            try:

                print(f"🔎 Searching student: {id}")

                # IMPORTANT:
                # Your actual Supabase table is "Students"
                response = (
                    supabase
                    .table("Students")
                    .select("*")
                    .eq("student_id", id)
                    .execute()
                )

                # IMPORTANT:
                # Define data before using it
                data = response.data

                if not data:

                    print(
                        f"❌ Student ID {id} "
                        "database me nahi mila"
                    )

                    cv2.putText(
                        img,
                        f"ID: {id} - Not Found",
                        (x1, y1 - 20),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 0, 255),
                        2
                    )

                else:

                    student = data[0]

                    name = student.get(
                        "name",
                        "Unknown"
                    )

                    major = student.get(
                        "major",
                        ""
                    )

                    totalAttendance = student.get(
                        "total_attendance",
                        0
                    )

                    standing = student.get(
                        "standing",
                        ""
                    )

                    year = student.get(
                        "year",
                        ""
                    )

                    startingYear = student.get(
                        "starting_year",
                        ""
                    )

                    print(
                        f"✅ Student found: {name}"
                    )

                    print(
                        f"📚 Major: {major}"
                    )

                    print(
                        f"📊 Attendance: "
                        f"{totalAttendance}"
                    )


                    # =====================================
                    # DISPLAY STUDENT INFO
                    # =====================================

                    cv2.rectangle(
                        img,
                        (x1, y2),
                        (x2, y2 + 130),
                        (0, 0, 0),
                        -1
                    )

                    cv2.putText(
                        img,
                        name,
                        (x1 + 10, y2 + 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (255, 255, 255),
                        2
                    )

                    cv2.putText(
                        img,
                        f"ID: {id}",
                        (x1 + 10, y2 + 60),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (255, 255, 255),
                        2
                    )

                    cv2.putText(
                        img,
                        f"AIML: {major}",
                        (x1 + 10, y2 + 90),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (255, 255, 255),
                        2
                    )

                    cv2.putText(
                        img,
                        f"Attendance: {totalAttendance}",
                        (x1 + 10, y2 + 120),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (255, 255, 255),
                        2
                    )


                    # =====================================
                    # ATTENDANCE
                    # =====================================

                    if (
                        lastRecognizedId != id
                        or not attendanceMarked
                    ):

                        try:

                            currentTime = datetime.now(
                                timezone.utc
                            )

                            # Current attendance
                            newAttendance = (
                                int(totalAttendance) + 1
                            )

                            updateData = {
                                "total_attendance":
                                    newAttendance,

                                "last_attendance_time":
                                    currentTime.isoformat()
                            }

                            (
                                supabase
                                .table("Students")
                                .update(updateData)
                                .eq("student_id", id)
                                .execute()
                            )

                            print(
                                f"🎉 Attendance marked "
                                f"for {name}"
                            )

                            print(
                                f"📊 New attendance: "
                                f"{newAttendance}"
                            )

                            lastRecognizedId = id
                            attendanceMarked = True

                        except Exception as e:

                            print(
                                "❌ Attendance update error:",
                                e
                            )


            except Exception as e:

                print(
                    "❌ Supabase/attendance error:",
                    e
                )

                cv2.putText(
                    img,
                    "Database Error",
                    (x1, y1 - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2
                )


    # =====================================================
    # SHOW CAMERA
    # =====================================================

    cv2.imshow(
        "AI Face Recognition Attendance",
        img
    )

    # Q = Quit
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):

        print("👋 Camera closed")
        break


# =========================================================
# CLEANUP
# =========================================================

cap.release()
cv2.destroyAllWindows()

print("✅ Program finished")