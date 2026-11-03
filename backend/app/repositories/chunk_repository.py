from sqlalchemy.orm import Session

from app.models.chunk import Chunk

class ChunkRepository:

    def __init__(self, db: Session):
        self.db = db


    def create_chunks(
        self,
        chunks: list[Chunk],
    ) -> list[Chunk]:

        self.db.add_all(chunks)

        self.db.commit()

        for chunk in chunks:
            self.db.refresh(chunk)

        return chunks
    
    
    '''def create_chunks(...):

    def get_chunks_by_document(...):

    def delete_chunks_by_document(...):'''