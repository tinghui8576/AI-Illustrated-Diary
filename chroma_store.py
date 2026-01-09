import uuid
import chromadb
from datetime import date, datetime
from pathlib import Path

class ChromaDiaryStore:
    def __init__(
        self,
        persist_dir: str = "chroma_db",
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
        image,
        style: str,
        mood: str, 
        base_dir="images"
    ):
        
        diary_id = self._generate_diary_id(d)
        now = datetime.now()
        date_str = d.isoformat()
        time_str = now.strftime("%H-%M-%S")

        folder = Path(base_dir) / date_str
        folder.mkdir(parents=True, exist_ok=True)

        image_path = folder / f"{time_str}.png"
        image.save(image_path)

    
        metadata = {
            "date": d.isoformat(),
            "time": now.strftime("%H:%M"),
            "created_at": now.isoformat(),
            "image_path": str(image_path),
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

        query = self.collection.get(ids=[diary_id])

        if query["metadatas"]:
            metadata = query["metadatas"][0]
            image_path = metadata.get("image_path")

            if image_path:
                path = Path(image_path)
                if path.exists():
                    path.unlink() 

        self.collection.delete(ids=[diary_id])
    