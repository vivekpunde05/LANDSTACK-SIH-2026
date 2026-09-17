import json

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session


def persist_priority(db: Session, result: dict) -> bool:
    try:
        db.execute(text("""
            INSERT INTO parcel_priority_scores (
                parcel_id, priority_score, priority_level, requires_field_verification,
                score_version, factor_breakdown, recommendation, calculated_at
            ) VALUES (
                :parcel_id, :priority_score, :priority_level, :requires_field_verification,
                :score_version, CAST(:factor_breakdown AS jsonb), :recommendation, :calculated_at
            ) ON CONFLICT (parcel_id, score_version) DO UPDATE SET
                priority_score=EXCLUDED.priority_score,
                priority_level=EXCLUDED.priority_level,
                requires_field_verification=EXCLUDED.requires_field_verification,
                factor_breakdown=EXCLUDED.factor_breakdown,
                recommendation=EXCLUDED.recommendation,
                calculated_at=EXCLUDED.calculated_at
        """), {**result, "factor_breakdown": json.dumps(result["factors"])})
        db.commit()
        return True
    except (SQLAlchemyError, AttributeError):
        db.rollback() if hasattr(db, "rollback") else None
        return False
