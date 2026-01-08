import uuid
import chromadb
from datetime import date, datetime


class ChromaDiaryStore:
    def __init__(
        self,
        persist_dir: str = "/workspace/chroma_db",
        collection_name: str = "diary_entries"
    ):
        self.client = chromadb.PersistentClient(
            path=persist_dir
        )
        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )

    # ------------------------
    # ID helper
    # ------------------------
    def _generate_diary_id(self, d: date) -> str:
        return f"{d.isoformat()}_{uuid.uuid4().hex[:8]}"

    # ------------------------
    # Save diary
    # ------------------------
    def save_diary(
        self,
        diary_text: str,
        d: date,
        style: str,
        mood: str
    ):
        diary_id = self._generate_diary_id(d)
        now = datetime.now()

        metadata = {
            "date": d.isoformat(),
            "time": now.strftime("%H:%M"),
            "created_at": now.isoformat(),
            "style": style,
            "mood": mood
        }

        self.collection.add(
            ids=[diary_id],
            documents=[diary_text],
            metadatas=[metadata]
        )

    # ------------------------
    # Load diaries by date
    # ------------------------
    def load_diaries(self, d: date):
        result = self.collection.get(
            where={"date": d.isoformat()}
        )

        diaries = []

        for text, meta, diary_id in zip(
            result["documents"],
            result["metadatas"],
            result["ids"]
        ):
            diaries.append({
                "id": diary_id,
                "text": text,
                "metadata": meta
            })

        diaries.sort(key=lambda x: x["metadata"].get("created_at", ""))
        return diaries

    # ------------------------
    # Delete diary
    # ------------------------
    def delete_diary(self, diary_id: str):
        self.collection.delete(ids=[diary_id])

    # ------------------------
    # Check if diary exists on date
    # ------------------------
    def diary_exists(self, d: date) -> bool:
        result = self.collection.get(
            where={"date": d.isoformat()}
        )
        return bool(result["ids"])
