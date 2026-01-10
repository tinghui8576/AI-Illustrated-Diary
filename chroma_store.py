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
    # Memory scoring
    # ------------------------
    def memory_score(self, metadata, distance,text, alpha=0.7):
        """Score memory by similarity and recency (0 < alpha < 1)."""
        sim_score = 1 - distance
        event_date = datetime.fromisoformat(metadata["date"])
        days_ago = (datetime.now() - event_date).days
        recency_score = 1 / (1 + days_ago)  
        
        return alpha * sim_score + (1 - alpha) * recency_score



    # ------------------------
    # Semantic search
    # ------------------------
    def retrieve_similar_diaries(
        self,
        query_text: str,
        n_results: int = 3,
        user_mood: str = None
    ):
        """
        Retrieve similar diary texts using embeddings.
        Optionally filter by mood.
        """
        where_filter = {"mood": user_mood} if user_mood else None
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where_filter
        )

        memories = []
        for docs, metas, dists, ids in zip(results["documents"], results["metadatas"], results["distances"], results["ids"]):
            # docs, metas, dists, ids are for one query
            for doc, meta, dist, _id in zip(docs, metas, dists, ids):
                if dist > 1:
                    continue
                memories.append((doc, meta, dist, _id))

        memories.sort(key=lambda x: self.memory_score(x[1], x[2], x[0]), reverse=True)

        top_memories = memories[:n_results]

        retrieved = [
            {"id": diary_id, "text": text, "metadata": meta}
            for text, meta, _, diary_id in top_memories
        ]

        return retrieved

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
    