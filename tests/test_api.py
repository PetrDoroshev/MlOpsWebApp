from fastapi.testclient import TestClient


def test_upload_youtube_url(test_client: TestClient):
    response = test_client.post(
        "/upload_yt_url/", data={"youtube_url": "https://rutube.ru/video/f8581fd9e0197d7d4ba9432bb35d75b2"}
    )

    assert response.status_code == 200
    assert "metal" in response.text.lower()


def test_main_page(test_client: TestClient):
    response = test_client.get("/")
    assert response.status_code == 200
    assert "<html" in response.text.lower()


def test_invalid_pages(test_client: TestClient):
    response = test_client.get("/nonexistent")
    assert response.status_code == 404

    response = test_client.post("/upload/")
    assert response.status_code == 422

    response = test_client.post("/upload_yt_url/", data={})
    assert response.status_code == 422

    non_audio_content = b"This is not an MP3 file"
    response = test_client.post(
        "/upload/",
        files={"file": ("./conftest.py", non_audio_content, "text/plain")},
    )
    assert response.status_code in (400, 422, 500)
