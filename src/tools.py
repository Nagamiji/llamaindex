# # src/tools.py
# import os
# import logging
# from dotenv import load_dotenv
# from sqlalchemy import create_engine, text
# from sqlalchemy.exc import SQLAlchemyError

# from llama_index.core.tools import QueryEngineTool, FunctionTool
# from llama_index.core.indices.struct_store import NLSQLTableQueryEngine
# from llama_index.llms.openai import OpenAI

# from database import get_sql_database

# # ——— Setup —————————————————————————————————————————————
# logging.basicConfig(level=logging.INFO)
# load_dotenv()

# def _get_engine():
#     """Factory for a SQLAlchemy engine, with env‐var checks."""
#     user = os.getenv("POSTGRES_USER")
#     pwd  = os.getenv("POSTGRES_PASSWORD")
#     host = os.getenv("POSTGRES_HOST")
#     db   = os.getenv("POSTGRES_DB")
#     if not all([user, pwd, host, db]):
#         msg = "Postgres env vars incomplete (POSTGRES_USER, PASSWORD, HOST, DB)."
#         logging.error(msg)
#         raise RuntimeError(msg)
#     uri = f"postgresql://{user}:{pwd}@{host}:5432/{db}"
#     return create_engine(uri, future=True)

# # ——— Query Tool ————————————————————————————————————————————
# def get_query_tool():
#     """
#     Builds a text-to-SQL query engine over your department schema.
#     """
#     sql_db = get_sql_database()
#     query_engine = NLSQLTableQueryEngine(
#         sql_database=sql_db,
#         tables=[
#             "student", "subject_score", "subject",
#             "group_schedule", "instructor", "room", "department"
#         ],
#         llm=OpenAI(model="gpt-3.5-turbo", temperature=0.0)
#     )
#     return QueryEngineTool.from_defaults(
#         query_engine=query_engine,
#         name="sql_query_tool",
#         description=(
#             "Executes natural-language queries by translating them to SQL "
#             "against the department database."
#         ),
#     )

# # ——— Update Score Tool —————————————————————————————————————
# def update_score(student_id: int, subject_id: int, score: float) -> str:
#     """
#     Validates inputs, checks that the student & subject exist, then updates
#     an existing score row (0–100). Returns a success or error message.
#     """
#     # 1) Input validation
#     if not isinstance(student_id, int) or not isinstance(subject_id, int):
#         return "❗ student_id and subject_id must be integers."
#     if not isinstance(score, (int, float)) or not (0 <= score <= 100):
#         return "❗ score must be a number between 0 and 100."

#     engine = _get_engine()
#     try:
#         with engine.begin() as conn:
#             # 2) Existence checks
#             exists = conn.execute(
#                 text("SELECT 1 FROM student WHERE id = :id"),
#                 {"id": student_id}
#             ).scalar_one_or_none()
#             if not exists:
#                 return f"❗ No student with ID {student_id}."

#             exists = conn.execute(
#                 text("SELECT 1 FROM subject WHERE id = :id"),
#                 {"id": subject_id}
#             ).scalar_one_or_none()
#             if not exists:
#                 return f"❗ No subject with ID {subject_id}."

#             # 3) Perform update
#             result = conn.execute(
#                 text("""
#                     UPDATE subject_score
#                        SET score = :score
#                      WHERE student_id = :sid
#                        AND subject_id = :subid
#                 """),
#                 {"score": score, "sid": student_id, "subid": subject_id}
#             )
#             if result.rowcount == 0:
#                 return (
#                     f"⚠️ No existing score record for student {student_id} "
#                     f"in subject {subject_id}."
#                 )

#         return f"✅ Updated student {student_id}’s score in subject {subject_id} to {score}."
#     except SQLAlchemyError as e:
#         logging.exception("Failed to update score")
#         return "❗ Database error while updating score."

# update_score_tool = FunctionTool.from_defaults(
#     fn=update_score,
#     name="update_score",
#     description=(
#         "Usage: update_score(student_id: int, subject_id: int, score: float)\n"
#         "Updates a student’s score (0–100) for a given subject."
#     ),
# )

# # ——— Enroll Student Tool ————————————————————————————————————
# def enroll_student(student_name: str, subject_name: str) -> str:
#     """
#     Validates inputs, checks that the student & subject exist, then enrolls
#     the student (score=0) if not already enrolled.
#     """
#     # 1) Input validation
#     if not student_name or not subject_name:
#         return "❗ Both student_name and subject_name must be provided."

#     engine = _get_engine()
#     try:
#         with engine.begin() as conn:
#             # 2) Lookup IDs
#             row = conn.execute(
#                 text("SELECT id FROM student WHERE name = :name"),
#                 {"name": student_name}
#             ).fetchone()
#             if not row:
#                 return f"❗ Student '{student_name}' not found."
#             student_id = row.id

#             row = conn.execute(
#                 text("SELECT id FROM subject WHERE name = :name"),
#                 {"name": subject_name}
#             ).fetchone()
#             if not row:
#                 return f"❗ Subject '{subject_name}' not found."
#             subject_id = row.id

#             # 3) Already enrolled?
#             exists = conn.execute(
#                 text("""
#                     SELECT 1 FROM subject_score
#                      WHERE student_id = :sid
#                        AND subject_id = :subid
#                 """),
#                 {"sid": student_id, "subid": subject_id}
#             ).scalar_one_or_none()
#             if exists:
#                 return f"⚠️ '{student_name}' is already enrolled in '{subject_name}'."

#             # 4) Enroll
#             conn.execute(
#                 text("""
#                     INSERT INTO subject_score
#                         (student_id, subject_id, score, semester, year)
#                     VALUES
#                         (:sid, :subid, 0.0, 1, extract(year FROM CURRENT_DATE)::int)
#                 """),
#                 {"sid": student_id, "subid": subject_id}
#             )

#         return f"✅ Enrolled '{student_name}' in '{subject_name}'."
#     except SQLAlchemyError:
#         logging.exception("Failed to enroll student")
#         return "❗ Database error while enrolling student."

# enroll_student_tool = FunctionTool.from_defaults(
#     fn=enroll_student,
#     name="enroll_student",
#     description=(
#         "Usage: enroll_student(student_name: str, subject_name: str)\n"
#         "Enrolls a named student in a named subject (score initialized to 0)."
#     ),
# )
# src/tools.py
# src/tools.py

import os
import logging
import time
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseModel, validator, ValidationError
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from llama_index.core.tools import QueryEngineTool, FunctionTool
from llama_index.core.indices.struct_store import NLSQLTableQueryEngine
from llama_index.llms.openai import OpenAI

from database import get_sql_database

# ——— Init —————————————————————————————————————————————————————————
load_dotenv()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ——— LLM & Defaults ——————————————————————————————————————————————————
LLM_MODEL    = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
LLM_TEMP     = float(os.getenv("LLM_TEMPERATURE", 0.0))
DEFAULT_SEM  = int(os.getenv("DEFAULT_SEMESTER", 1))
DEFAULT_YEAR = int(os.getenv("DEFAULT_YEAR", 2023))


# ——— Engine Factory ——————————————————————————————————————————————————
@lru_cache(maxsize=1)
def _get_engine():
    """
    Build a SQLAlchemy engine from POSTGRES_* env vars.
    """
    user = os.getenv("POSTGRES_USER")
    pwd  = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST")
    db   = os.getenv("POSTGRES_DB")
    if not all([user, pwd, host, db]):
        msg = "❗ Must set POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_DB in .env"
        logger.error(msg)
        raise RuntimeError(msg)
    uri = f"postgresql://{user}:{pwd}@{host}:5432/{db}"
    engine = create_engine(uri, future=True, pool_pre_ping=True)
    logger.info("Created DB engine for %s@%s/%s", user, host, db)
    return engine


# ——— Query Tool ————————————————————————————————————————————————————
def get_query_tool() -> QueryEngineTool:
    """
    Builds a text→SQL engine over your department tables.
    """
    # 1) Build engine & LLM
    sql_db = get_sql_database()
    llm    = OpenAI(model=LLM_MODEL, temperature=LLM_TEMP)
    table_list = [
        "student", "subject_score", "subject",
        "group_schedule", "instructor", "room", "department"
    ]

    # 2) Instantiate the SQL query engine
    query_engine = NLSQLTableQueryEngine(
        sql_database=sql_db,
        tables=table_list,
        llm=llm
    )
    logger.info("Initialized SQL query engine on tables: %s", table_list)

    # 3) Wrap as a LlamaIndex tool
    return QueryEngineTool.from_defaults(
        query_engine=query_engine,
        name="sql_query_tool",
        description=(
            "Translate natural-language queries to SQL and execute them "
            "against the department database."
        ),
    )


# ——— Input Schemas ——————————————————————————————————————————————————
class UpdateScoreArgs(BaseModel):
    student_id: int
    subject_id: int
    score: float

    @validator("score")
    def check_score(cls, v):
        if not (0 <= v <= 100):
            raise ValueError("score must be between 0 and 100")
        return v


class EnrollArgs(BaseModel):
    student_name: str
    subject_name: str

    @validator("student_name", "subject_name")
    def non_empty(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("must not be empty")
        return v


# ——— Update Score Tool —————————————————————————————————————————————————
def update_score(student_id: int, subject_id: int, score: float) -> str:
    """
    Validate & update an existing subject_score row. Returns status message.
    """
    start = time.time()
    # Validate inputs
    try:
        args = UpdateScoreArgs(
            student_id=student_id,
            subject_id=subject_id,
            score=score
        )
    except ValidationError as ve:
        return f"❗ Invalid arguments: {ve}"

    engine = _get_engine()
    try:
        with engine.begin() as conn:
            # Existence checks
            for tbl, key in [("student", args.student_id), ("subject", args.subject_id)]:
                exists = conn.execute(
                    text(f"SELECT 1 FROM {tbl} WHERE id = :id"),
                    {"id": key}
                ).scalar_one_or_none()
                if not exists:
                    return f"❗ No {tbl} with ID {key}."

            # Perform update
            res = conn.execute(
                text("""
                    UPDATE subject_score
                       SET score = :score
                     WHERE student_id = :sid
                       AND subject_id = :subid
                """),
                {"score": args.score, "sid": args.student_id, "subid": args.subject_id}
            )

        elapsed = time.time() - start
        logger.info("update_score completed in %.2f s", elapsed)

        if res.rowcount == 0:
            return (
                f"⚠️ No existing record for student {args.student_id} "
                f"in subject {args.subject_id}."
            )
        return (
            f"✅ Updated score to {args.score} "
            f"for student {args.student_id} in subject {args.subject_id}."
        )
    except SQLAlchemyError:
        logger.exception("Database error in update_score")
        return "❗ Database error while updating score."


update_score_tool = FunctionTool.from_defaults(
    fn=update_score,
    name="update_score",
    description=(
        "update_score(student_id: int, subject_id: int, score: float) → str\n"
        "Validate and update an existing score (0–100)."
    ),
)


# ——— Enroll Student Tool —————————————————————————————————————————————————
def enroll_student(student_name: str, subject_name: str) -> str:
    """
    Validate & enroll a student by name into a subject by name (initial score=0).
    """
    start = time.time()
    # Validate inputs
    try:
        args = EnrollArgs(
            student_name=student_name,
            subject_name=subject_name
        )
    except ValidationError as ve:
        return f"❗ Invalid arguments: {ve}"

    engine = _get_engine()
    try:
        with engine.begin() as conn:
            # Lookup student ID
            row = conn.execute(
                text("SELECT id FROM student WHERE name = :nm"),
                {"nm": args.student_name}
            ).fetchone()
            if not row:
                return f"❗ Student '{args.student_name}' not found."
            sid = row.id

            # Lookup subject ID
            row = conn.execute(
                text("SELECT id FROM subject WHERE name = :nm"),
                {"nm": args.subject_name}
            ).fetchone()
            if not row:
                return f"❗ Subject '{args.subject_name}' not found."
            subid = row.id

            # Already enrolled check
            exists = conn.execute(
                text("""
                    SELECT 1 FROM subject_score
                     WHERE student_id = :sid
                       AND subject_id = :subid
                """),
                {"sid": sid, "subid": subid}
            ).scalar_one_or_none()
            if exists:
                return (
                    f"⚠️ '{args.student_name}' is already "
                    f"enrolled in '{args.subject_name}'."
                )

            # Perform enrollment
            conn.execute(
                text("""
                    INSERT INTO subject_score
                      (student_id, subject_id, score, semester, year)
                    VALUES
                      (:sid, :subid, 0.0, :sem, :yr)
                """),
                {
                    "sid": sid,
                    "subid": subid,
                    "sem": DEFAULT_SEM,
                    "yr": DEFAULT_YEAR
                }
            )

        elapsed = time.time() - start
        logger.info("enroll_student completed in %.2f s", elapsed)
        return f"✅ Enrolled '{args.student_name}' in '{args.subject_name}'."
    except SQLAlchemyError:
        logger.exception("Database error in enroll_student")
        return "❗ Database error while enrolling student."


enroll_student_tool = FunctionTool.from_defaults(
    fn=enroll_student,
    name="enroll_student",
    description=(
        "enroll_student(student_name: str, subject_name: str) → str\n"
        "Validate and enroll the named student (initial score=0)."
    ),
)
