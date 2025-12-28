"""
Video processing utilities using Whisper for speech-to-text
"""
import os
import json
from typing import Dict, Any, Optional, List
from pathlib import Path

from app.core.vector_store import get_vector_store
from app.core.document_processor import get_document_processor
from app.config import settings


class VideoProcessor:
    """Video processing with Whisper transcription"""

    def __init__(self):
        self.vector_store = get_vector_store()
        self.document_processor = get_document_processor()

    async def process_video(self, video_path: str, file_id: int, metadata: Dict[str, Any]):
        """Process a video file: transcribe and index"""

        # Generate transcription file path
        video_name = Path(video_path).stem
        transcription_path = os.path.join(settings.UPLOAD_DIR, f"{video_name}_transcription.json")

        # Transcribe video
        transcription_data = await self._transcribe_video(video_path)

        if not transcription_data:
            return False

        # Save transcription
        with open(transcription_path, 'w', encoding='utf-8') as f:
            json.dump(transcription_data, f, indent=2, ensure_ascii=False)

        # Extract text with timestamps
        full_text = transcription_data.get('text', '')
        segments = transcription_data.get('segments', [])

        # Process full transcription text
        text_metadata = {
            **metadata,
            "transcription_path": transcription_path,
            "video_duration": transcription_data.get('duration', 0),
            "language": transcription_data.get('language', 'unknown')
        }

        # Add full transcription to vector store
        await self.document_processor.process_file(
            transcription_path,
            file_id,
            {**text_metadata, "content_type": "transcription"}
        )

        # Add timestamped segments for precise Q&A
        await self._index_segments(segments, file_id, metadata)

        # Update file record with transcription path
        return transcription_path

    async def _transcribe_video(self, video_path: str) -> Optional[Dict[str, Any]]:
        """Transcribe video using Whisper"""

        try:
            import whisper

            # Load model (using base model for speed, can be upgraded)
            model = whisper.load_model("base")

            # Transcribe
            result = model.transcribe(video_path)

            return {
                "text": result["text"],
                "segments": result["segments"],
                "language": result.get("language", "unknown"),
                "duration": result.get("duration", 0)
            }

        except ImportError:
            print("Whisper not installed, skipping transcription")
            return None
        except Exception as e:
            print(f"Error transcribing video {video_path}: {str(e)}")
            return None

    async def _index_segments(self, segments: List[Dict[str, Any]], file_id: int, metadata: Dict[str, Any]):
        """Index individual segments with timestamps"""

        documents = []
        metadatas = []
        ids = []

        for i, segment in enumerate(segments):
            text = segment.get('text', '').strip()
            if not text:
                continue

            start_time = segment.get('start', 0)
            end_time = segment.get('end', 0)

            # Format timestamp
            start_formatted = self._format_timestamp(start_time)
            end_formatted = self._format_timestamp(end_time)

            documents.append(text)
            metadatas.append({
                **metadata,
                "segment_id": i,
                "start_time": start_time,
                "end_time": end_time,
                "timestamp_range": f"{start_formatted} - {end_formatted}",
                "content_type": "video_segment"
            })
            ids.append(f"{file_id}_segment_{i}")

        if documents:
            await self.vector_store.add_documents(documents, metadatas, ids)

    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds into MM:SS or HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"

    async def search_video_content(self, query: str, file_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search for content in video transcriptions"""

        where_clause = {"content_type": "video_segment"}
        if file_id:
            where_clause["file_id"] = file_id

        results = await self.vector_store.search_documents(query, n_results=5, where=where_clause)

        # Enhance results with timestamp information
        enhanced_results = []

        if results.get("documents") and results.get("metadatas"):
            for doc, metadata in zip(results["documents"][0], results["metadatas"][0]):
                enhanced_results.append({
                    "text": doc,
                    "timestamp": metadata.get("timestamp_range", "Unknown"),
                    "start_time": metadata.get("start_time", 0),
                    "end_time": metadata.get("end_time", 0),
                    "filename": metadata.get("filename", "Unknown")
                })

        return enhanced_results


# Global video processor instance
video_processor = VideoProcessor()


def get_video_processor():
    """Get the global video processor instance"""
    return video_processor


