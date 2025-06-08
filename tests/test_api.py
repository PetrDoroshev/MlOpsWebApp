from fastapi.testclient import TestClient

def test_upload_youtube_url(test_client: TestClient):
    response = test_client.post(
        "/upload_yt_url/",
        data={"youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}
    )

    assert response.status_code == 200
    assert "Jazz" in response.text
