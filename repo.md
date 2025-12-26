# Seminar Gemini OCR Engine Repository Information

## Project Structure

```
- .idea/
- .zencoder/
- .zenflow/
- .gitignore
- LICENSE
- main.py
- README.md
- requirements.txt
```

## File Contents

### README.md

```markdown
# Seminar Gemini OCR Engine

```shell
python3 -m venv .venv
```

```shell
source .venv/bin/activate
```

```shell
pip freeze > requirements.txt
```
```

### requirements.txt

```text
annotated-types==0.7.0
anyio==4.12.0
cachetools==6.2.4
certifi==2025.11.12
charset-normalizer==3.4.4
distro==1.9.0
google-auth==2.45.0
google-genai==1.56.0
h11==0.16.0
httpcore==1.0.9
httpx==0.28.1
idna==3.11
pyasn1==0.6.1
pyasn1_modules==0.4.2
pydantic==2.12.5
pydantic_core==2.41.5
requests==2.32.5
rsa==4.9.1
sniffio==1.3.1
tenacity==9.1.2
typing-inspection==0.4.2
typing_extensions==4.15.0
urllib3==2.6.2
websockets==15.0.1
```

### main.py

```python
from google import genai
from google.genai import types
import PIL.Image
import json

# 1. Khởi tạo Client với API Key của bạn
# Lấy key tại: https://aistudio.google.com/
client = genai.Client(api_key="YOUR_GEMINI_API_KEY")


def extract_card_info(image_path):
    # 2. Load ảnh từ thư mục
    img = PIL.Image.open(image_path)

    # 3. Định nghĩa cấu trúc JSON mong muốn (Schema)
    # Việc định nghĩa schema giúp AI trả về kết quả chuẩn xác 100% để code parse được
    prompt_text = """
    Phân tích ảnh Card Visit này và trích xuất thông tin theo định dạng JSON.
    Hãy phân biệt rõ ràng:
    - 'company_name': Tên tổ chức/công ty.
    - 'person_name': Tên cá nhân trên card.
    - 'position': Chức danh.
    - 'contact': Các thông tin số điện thoại, email, website.
    - 'address': Địa chỉ ghi trên card.

    Nếu thông tin nào không có, hãy để là null.
    """

    # 4. Gửi yêu cầu đến model Gemini 1.5 Flash
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=[prompt_text, img],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",  # Ép kiểu trả về là JSON
            temperature=0.1  # Giảm độ sáng tạo để dữ liệu chính xác hơn
        )
    )

    # 5. Parse kết quả
    try:
        data = json.loads(response.text)
        return data
    except Exception as e:
        print(f"Lỗi parse JSON: {e}")
        return response.text


# Chạy thử
if __name__ == "__main__":
    result = extract_card_info("path_to_your_card.jpg")
    print(json.dumps(result, indent=4, ensure_ascii=False))
```

## Summary

This project is a Python-based OCR engine leveraging Google's Gemini 1.5 Flash model to extract information from business cards (Card Visit).

**Key Components:**
- **`main.py`**: The core script.
    - Initializes the Google GenAI client.
    - Defines a function `extract_card_info(image_path)` that:
        - Loads an image using `PIL`.
        - Constructs a prompt instructing Gemini to extract specific fields (company name, person name, position, contact, address) in JSON format.
        - Configures the model to output JSON (`response_mime_type="application/json"`).
        - Parses and returns the JSON data.
    - Includes a main block to test the function with a placeholder image path.
- **`requirements.txt`**: Lists dependencies, notably `google-genai` for the API client.
