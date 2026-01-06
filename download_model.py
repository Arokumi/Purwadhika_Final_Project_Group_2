# import logging
# from livekit.plugins import silero

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# def download_models():
#     try:
#         logger.info("⬇️ Downloading Silero VAD model...")
#         silero.VAD.load()
#         logger.info("✅ Silero VAD model ready.")
        
#         logger.info("ℹ️ Turn Detector akan di-download otomatis saat agent pertama kali jalan.")
        
#     except Exception as e:
#         logger.error(f"❌ Failed to download models: {e}")
#         raise e

# if __name__ == "__main__":
#     download_models()

import logging
import torch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_models():
    try:
        logger.info("⬇️ Downloading Silero VAD model...")

        torch.hub.load(
            repo_or_dir="snakers4/silero-vad",
            model="silero_vad",
            force_reload=False
        )

        logger.info("✅ Silero VAD model ready.")
        logger.info("ℹ️ Turn Detector didownload via `download-files` (LiveKit CLI).")

    except Exception as e:
        logger.error(f"❌ Failed to download Silero VAD model: {e}")
        raise e

if __name__ == "__main__":
    download_models()
