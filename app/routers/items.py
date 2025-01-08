from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.models.items import YouTubeVideoURL
from pytubefix import YouTube
import os
import subprocess
import uuid

router = APIRouter()

DOWNLOAD_PATH = "./downloads"

os.makedirs(DOWNLOAD_PATH, exist_ok=True)

def download_youtube_video_and_audio(url: str, download_path: str):
    try:
        yt = YouTube(url)
        video_stream = yt.streams.filter(res="1080p", file_extension="mp4", only_video=True).first()
        audio_stream = yt.streams.filter(only_audio=True, file_extension="mp4").first()

        if video_stream and audio_stream:
            print(f"Downloading video: {yt.title}")
            
            video_filename = f"{uuid.uuid4()}-video.mp4"
            audio_filename = f"{uuid.uuid4()}-audio.mp4"
            output_filename = f"{uuid.uuid4()}-final.mp4"

            video_stream.download(output_path=download_path, filename=video_filename)
            audio_stream.download(output_path=download_path, filename=audio_filename)

            video_path = os.path.join(download_path, video_filename)
            audio_path = os.path.join(download_path, audio_filename)
            output_path = os.path.join(download_path, output_filename)

            print("Merging video and audio...")

            command = [
                "ffmpeg",
                "-i", video_path,
                "-i", audio_path,
                "-c:v", "copy",
                "-c:a", "aac",
                "-strict", "experimental",
                output_path
            ]

            subprocess.run(command, check=True)

            os.remove(video_path)
            os.remove(audio_path)

            print(f"Download complete! Merged file saved as: {output_path}")

            return output_path
        else:
            raise Exception("1080p video or audio stream not available.")
    except Exception as e:
        print(f"An error occurred: {e}")

        raise HTTPException(status_code=400, detail=f"Error downloading video: {str(e)}")

@router.post("/generate-youtube-video-download-url")
def generate_youtube_video_download_url(youtube_video_url: YouTubeVideoURL):
    try:
        final_video_path = download_youtube_video_and_audio(youtube_video_url.url, DOWNLOAD_PATH)
        filename = os.path.basename(final_video_path)

        return FileResponse(
            path=final_video_path,
            media_type="video/mp4",
            filename=filename
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list-downloaded-files")
def list_downloaded_files():
    try:
        downloaded_files = os.listdir(DOWNLOAD_PATH)

        return {"downloadedFiles": downloaded_files}
    except Exception as e:
        return {"error": str(e)}

@router.delete("/delete-downloaded-file/{filename}")
def delete_downloaded_file(filename: str):
    downloaded_file_path = os.path.join(DOWNLOAD_PATH, filename)

    if os.path.exists(downloaded_file_path):
        os.remove(downloaded_file_path)

        return {"message": f"File {filename} deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="File not found")