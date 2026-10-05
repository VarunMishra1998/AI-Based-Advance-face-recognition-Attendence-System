import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = "https://wwfraugezutgfefjvlwq.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("✅ Supabase connected successfully (EncodeGenerator)")

# =========================
# Images Folder
# =========================
folderPath = "Images"

pathList = os.listdir(folderPath)

print(f"📁 Found {len(pathList)} images: {pathList}")


imgList = []
studentIds = []


# =========================
# Load Images
# =========================
for file_name in pathList:

    file_path = os.path.join(folderPath, file_name)

    # Read image
    img = cv2.imread(file_path)

    if img is None:
        print(f"⚠️ Could not read image: {file_name}")
        continue

    # Get student ID from filename
    # Example:
    # 6003.jpeg   -> 6003
    # 6003_2.jpeg -> 6003
    # 6004.jpeg   -> 6004
    # 6004_2.jpeg -> 6004

    file_without_extension = os.path.splitext(file_name)[0]

    student_id = file_without_extension.split("_")[0]

    imgList.append(img)
    studentIds.append(student_id)

    print(f"✅ Loaded: {file_name} → Student ID: {student_id}")


print(f"✅ Loaded {len(imgList)} images for encoding.")


# =========================
# Find Face Encodings
# =========================
def findEncodings(imagesList):

    encodeList = []

    validStudentIds = []

    for idx, img in enumerate(imagesList):

        try:

            # Convert BGR → RGB
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Find face encoding
            encodes = face_recognition.face_encodings(img_rgb)

            if len(encodes) == 0:

                print(
                    f"⚠️ No face found in image for student "
                    f"{studentIds[idx]}"
                )

                continue

            # Save first detected face
            encodeList.append(encodes[0])

            # Save corresponding student ID
            validStudentIds.append(studentIds[idx])

            print(
                f"✅ Encoded: Student ID {studentIds[idx]}"
            )

        except Exception as e:

            print(
                f"❌ Error encoding Student ID "
                f"{studentIds[idx]}: {e}"
            )


    return encodeList, validStudentIds


# =========================
# Start Encoding
# =========================
print("⚙️ Encoding Started...")


encodeListKnown, validStudentIds = findEncodings(imgList)


print(
    f"✅ Encoding Complete. "
    f"Total encodings: {len(encodeListKnown)}"
)


# =========================
# Save Encodings
# =========================
encodeListKnownWithIds = [
    encodeListKnown,
    validStudentIds
]


with open("EncodeFile.p", "wb") as file:

    pickle.dump(
        encodeListKnownWithIds,
        file
    )


print("💾 Encode file saved as EncodeFile.p")


# =========================
# Upload Images to Supabase
# =========================
print("☁️ Uploading images to Supabase...")


for file_name in pathList:

    file_path = os.path.join(
        folderPath,
        file_name
    )

    try:

        with open(file_path, "rb") as f:

            res = supabase.storage \
            .from_("student-images") \
            .upload(file_name, f)

            print(
                f"📤 Uploaded: {file_name}"
            )

    except Exception as e:

        print(
            f"❌ Upload failed for "
            f"{file_name}: {e}"
        )


print("🎉 EncodeGenerator completed successfully!")