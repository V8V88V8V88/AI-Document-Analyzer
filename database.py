import os
import logging
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

# Database configuration
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://user:password@localhost/dbname")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class Document(Base):
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    content_hash = Column(String, unique=True, nullable=False)  # To avoid duplicate documents
    summary = Column(Text)
    word_count = Column(Integer)
    character_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    qa_sessions = relationship("QASession", back_populates="document")
    quiz_sessions = relationship("QuizSession", back_populates="document")

class QASession(Base):
    __tablename__ = "qa_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    session_id = Column(String, nullable=False)  # To group Q&A pairs in a session
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="qa_sessions")
    qa_pairs = relationship("QAPair", back_populates="qa_session")

class QAPair(Base):
    __tablename__ = "qa_pairs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    qa_session_id = Column(UUID(as_uuid=True), ForeignKey("qa_sessions.id"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    qa_session = relationship("QASession", back_populates="qa_pairs")

class QuizSession(Base):
    __tablename__ = "quiz_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    session_id = Column(String, nullable=False)
    total_questions = Column(Integer, nullable=False)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    document = relationship("Document", back_populates="quiz_sessions")
    quiz_answers = relationship("QuizAnswer", back_populates="quiz_session")

class QuizAnswer(Base):
    __tablename__ = "quiz_answers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_session_id = Column(UUID(as_uuid=True), ForeignKey("quiz_sessions.id"), nullable=False)
    question_number = Column(Integer, nullable=False)
    question = Column(Text, nullable=False)
    user_answer = Column(Text, nullable=False)
    correct_answer = Column(Text, nullable=False)
    ai_feedback = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    quiz_session = relationship("QuizSession", back_populates="quiz_answers")

# Database operations class
class DatabaseManager:
    def __init__(self):
        self.session = None
    
    def get_session(self) -> Session:
        """Get a database session"""
        if not self.session:
            self.session = SessionLocal()
        return self.session
    
    def close_session(self):
        """Close the database session"""
        if self.session:
            self.session.close()
            self.session = None
    
    def create_tables(self):
        """Create all database tables"""
        try:
            Base.metadata.create_all(bind=engine)
            logging.info("Database tables created successfully")
        except Exception as e:
            logging.error(f"Error creating database tables: {e}")
            raise
    
    def save_document(self, filename: str, content: str, summary: str = None) -> str:
        """Save a document to the database"""
        try:
            import hashlib
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            session = self.get_session()
            
            # Check if document already exists
            existing_doc = session.query(Document).filter_by(content_hash=content_hash).first()
            if existing_doc:
                return str(existing_doc.id)
            
            # Create new document
            document = Document(
                filename=filename,
                content=content,
                content_hash=content_hash,
                summary=summary,
                word_count=len(content.split()),
                character_count=len(content)
            )
            
            session.add(document)
            session.commit()
            
            return str(document.id)
            
        except Exception as e:
            session.rollback()
            logging.error(f"Error saving document: {e}")
            raise
    
    def get_document(self, document_id: str) -> Optional[Document]:
        """Get a document by ID"""
        try:
            session = self.get_session()
            return session.query(Document).filter_by(id=document_id).first()
        except Exception as e:
            logging.error(f"Error getting document: {e}")
            return None
    
    def get_recent_documents(self, limit: int = 10) -> List[Document]:
        """Get recently uploaded documents"""
        try:
            session = self.get_session()
            return session.query(Document).order_by(Document.created_at.desc()).limit(limit).all()
        except Exception as e:
            logging.error(f"Error getting recent documents: {e}")
            return []
    
    def save_qa_session(self, document_id: str, session_id: str, qa_pairs: List[Dict]) -> str:
        """Save a Q&A session"""
        try:
            session = self.get_session()
            
            # Create Q&A session
            qa_session = QASession(
                document_id=document_id,
                session_id=session_id
            )
            session.add(qa_session)
            session.flush()  # Get the ID
            
            # Add Q&A pairs
            for qa_pair in qa_pairs:
                qa_pair_record = QAPair(
                    qa_session_id=qa_session.id,
                    question=qa_pair['question'],
                    answer=qa_pair['answer']
                )
                session.add(qa_pair_record)
            
            session.commit()
            return str(qa_session.id)
            
        except Exception as e:
            session.rollback()
            logging.error(f"Error saving Q&A session: {e}")
            raise
    
    def get_qa_history(self, document_id: str, limit: int = 10) -> List[Dict]:
        """Get Q&A history for a document"""
        try:
            session = self.get_session()
            
            qa_pairs = session.query(QAPair).join(QASession).filter(
                QASession.document_id == document_id
            ).order_by(QAPair.created_at.desc()).limit(limit).all()
            
            return [
                {
                    'question': qa.question,
                    'answer': qa.answer,
                    'created_at': qa.created_at
                }
                for qa in qa_pairs
            ]
            
        except Exception as e:
            logging.error(f"Error getting Q&A history: {e}")
            return []
    
    def save_quiz_session(self, document_id: str, session_id: str, quiz_data: Dict) -> str:
        """Save a quiz session"""
        try:
            session = self.get_session()
            
            # Create quiz session
            quiz_session = QuizSession(
                document_id=document_id,
                session_id=session_id,
                total_questions=len(quiz_data.get('questions', [])),
                completed=quiz_data.get('completed', False)
            )
            session.add(quiz_session)
            session.flush()  # Get the ID
            
            # Add quiz answers
            for i, answer_data in enumerate(quiz_data.get('answers', [])):
                quiz_answer = QuizAnswer(
                    quiz_session_id=quiz_session.id,
                    question_number=i + 1,
                    question=answer_data['question'],
                    user_answer=answer_data['user_answer'],
                    correct_answer=answer_data['correct_answer'],
                    ai_feedback=answer_data.get('ai_feedback', '')
                )
                session.add(quiz_answer)
            
            session.commit()
            return str(quiz_session.id)
            
        except Exception as e:
            session.rollback()
            logging.error(f"Error saving quiz session: {e}")
            raise
    
    def get_quiz_history(self, document_id: str, limit: int = 5) -> List[Dict]:
        """Get quiz history for a document"""
        try:
            session = self.get_session()
            
            quiz_sessions = session.query(QuizSession).filter_by(
                document_id=document_id
            ).order_by(QuizSession.created_at.desc()).limit(limit).all()
            
            history = []
            for quiz_session in quiz_sessions:
                quiz_answers = session.query(QuizAnswer).filter_by(
                    quiz_session_id=quiz_session.id
                ).order_by(QuizAnswer.question_number).all()
                
                history.append({
                    'id': str(quiz_session.id),
                    'total_questions': quiz_session.total_questions,
                    'completed': quiz_session.completed,
                    'created_at': quiz_session.created_at,
                    'answers': [
                        {
                            'question': ans.question,
                            'user_answer': ans.user_answer,
                            'correct_answer': ans.correct_answer,
                            'ai_feedback': ans.ai_feedback
                        }
                        for ans in quiz_answers
                    ]
                })
            
            return history
            
        except Exception as e:
            logging.error(f"Error getting quiz history: {e}")
            return []
    
    def get_document_stats(self) -> Dict:
        """Get overall document statistics"""
        try:
            session = self.get_session()
            
            total_documents = session.query(Document).count()
            total_qa_sessions = session.query(QASession).count()
            total_quiz_sessions = session.query(QuizSession).count()
            
            return {
                'total_documents': total_documents,
                'total_qa_sessions': total_qa_sessions,
                'total_quiz_sessions': total_quiz_sessions
            }
            
        except Exception as e:
            logging.error(f"Error getting document stats: {e}")
            return {'total_documents': 0, 'total_qa_sessions': 0, 'total_quiz_sessions': 0}

# Initialize database manager
db_manager = DatabaseManager()

# Create tables on import
try:
    db_manager.create_tables()
    logging.info("Database initialized successfully")
except Exception as e:
    logging.error(f"Database initialization failed: {e}")