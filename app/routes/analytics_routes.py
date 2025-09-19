from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
import json

from .. import crud, models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/heatmap", response_model=schemas.HeatmapResponse)
async def get_heatmap(
    level: str = Query(default="district", description="district or cluster"),
    district: Optional[str] = Query(None, description="Specific district for cluster view"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get heatmap data as GeoJSON"""
    
    if level == "district":
        # Get migrant counts by district
        district_counts = crud.get_migrants_by_district(db)
        
        # Mock district boundaries (in real implementation, load from districts_kerala.json)
        mock_districts = {
            "Thiruvananthapuram": {"lat": 8.5241, "lng": 76.9366},
            "Kollam": {"lat": 8.8932, "lng": 76.6141},
            "Pathanamthitta": {"lat": 9.2648, "lng": 76.7870},
            "Alappuzha": {"lat": 9.4981, "lng": 76.3388},
            "Kottayam": {"lat": 9.5916, "lng": 76.5222},
            "Idukki": {"lat": 9.8513, "lng": 76.9447},
            "Ernakulam": {"lat": 9.9312, "lng": 76.2673},
            "Thrissur": {"lat": 10.5276, "lng": 76.2144},
            "Palakkad": {"lat": 10.7867, "lng": 76.6548},
            "Malappuram": {"lat": 11.0510, "lng": 76.0711},
            "Kozhikode": {"lat": 11.2588, "lng": 75.7804},
            "Wayanad": {"lat": 11.6854, "lng": 76.1320},
            "Kannur": {"lat": 11.8745, "lng": 75.3704},
            "Kasaragod": {"lat": 12.4996, "lng": 74.9869}
        }
        
        features = []
        for district_name, count in district_counts:
            if district_name and district_name in mock_districts:
                coords = mock_districts[district_name]
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [coords["lng"], coords["lat"]]
                    },
                    "properties": {
                        "district": district_name,
                        "migrant_count": count,
                        "level": "district"
                    }
                }
                features.append(feature)
        
        return schemas.HeatmapResponse(features=features)
    
    elif level == "cluster":
        # Get encounter counts by district for clustering
        encounter_counts = crud.get_encounters_by_district(db)
        
        features = []
        for district_name, count in encounter_counts:
            if district_name:
                # Mock cluster points within district
                base_coords = {
                    "Thiruvananthapuram": {"lat": 8.5241, "lng": 76.9366},
                    "Kollam": {"lat": 8.8932, "lng": 76.6141},
                    "Ernakulam": {"lat": 9.9312, "lng": 76.2673}
                }.get(district_name, {"lat": 10.0, "lng": 76.0})
                
                # Create multiple cluster points
                for i in range(min(count, 5)):  # Max 5 clusters per district
                    feature = {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [
                                base_coords["lng"] + (i * 0.1),
                                base_coords["lat"] + (i * 0.1)
                            ]
                        },
                        "properties": {
                            "district": district_name,
                            "encounter_count": count // (i + 1),
                            "cluster_id": f"{district_name}_cluster_{i}",
                            "level": "cluster"
                        }
                    }
                    features.append(feature)
        
        return schemas.HeatmapResponse(features=features)
    
    else:
        raise HTTPException(status_code=400, detail="Invalid level. Use 'district' or 'cluster'")

@router.get("/stats")
async def get_analytics_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get general analytics statistics"""
    
    # Get total counts
    total_migrants = len(crud.get_migrants(db, limit=10000))
    total_encounters = len(crud.get_encounters(db, limit=10000))
    total_users = len(crud.get_users(db, limit=1000))
    
    # Get district breakdown
    district_counts = crud.get_migrants_by_district(db)
    
    return {
        "totals": {
            "migrants": total_migrants,
            "encounters": total_encounters,
            "users": total_users
        },
        "by_district": [
            {"district": district, "count": count}
            for district, count in district_counts
        ]
    }

@router.get("/trends")
async def get_trends(
    days: int = Query(default=30, description="Number of days for trend analysis"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_doctor_or_admin)
):
    """Get trend data for the last N days (requires doctor or admin role)"""
    
    # Mock trend data (in real implementation, query by date ranges)
    import random
    from datetime import datetime, timedelta
    
    trends = []
    base_date = datetime.now() - timedelta(days=days)
    
    for i in range(days):
        date = base_date + timedelta(days=i)
        trends.append({
            "date": date.strftime("%Y-%m-%d"),
            "new_migrants": random.randint(0, 10),
            "new_encounters": random.randint(0, 20),
            "active_users": random.randint(5, 15)
        })
    
    return {
        "period": f"Last {days} days",
        "trends": trends
    }
