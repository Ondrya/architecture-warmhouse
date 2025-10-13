# app.py
import random
import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, status, Request
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI(
    title="Smart Home Sensor API",
    description="A FastAPI implementation of the Smart Home Sensor Management API",
    version="1.0.0"
)

# DB config
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "postgres"),
    "database": os.getenv("DB_NAME", "smarthome"),
    "user": os.getenv("DB_USER", "user"),
    "password": os.getenv("DB_PASSWORD", "password")
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

# Pydantic models
class SensorCreate(BaseModel):
    name: str
    type: str
    location: str
    unit: str

class SensorUpdate(SensorCreate):
    pass

class SensorValueUpdate(BaseModel):
    value: Optional[float] = None  # ignored in logic, but accepted
    status: str

class SensorResponse(BaseModel):
    id: int
    name: str
    type: str
    location: str
    unit: str
    status: str
    value: Optional[float] = None  # generated on read

# Helper
def get_random_value(sensor_type: str) -> Optional[float]:
    if sensor_type == "temperature":
        return round(random.uniform(18.0, 30.0), 1)
    return None

# --- Health Check ---
@app.get("/health", summary="Health check")
def health():
    try:
        conn = get_db_connection()
        conn.close()
        return {"status": "OK"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB connection failed: {str(e)}")

# --- GET /api/v1/sensors ---
@app.get("/api/v1/sensors", response_model=List[SensorResponse], summary="Get all sensors")
def get_all_sensors():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM sensors;")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    sensors = []
    for row in rows:
        row = dict(row)
        row["value"] = get_random_value(row["type"])
        sensors.append(row)
    return sensors

# --- GET /api/v1/sensors/{sensor_id} ---
@app.get("/api/v1/sensors/{sensor_id}", response_model=SensorResponse, summary="Get sensor by ID")
def get_sensor(sensor_id: int):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM sensors WHERE id = %s;", (sensor_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    sensor = dict(row)
    sensor["value"] = get_random_value(sensor["type"])
    return sensor

# --- POST /api/v1/sensors ---
@app.post("/api/v1/sensors", response_model=SensorResponse, status_code=status.HTTP_201_CREATED, summary="Create sensor")
def create_sensor(sensor: SensorCreate):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        INSERT INTO sensors (name, type, location, unit)
        VALUES (%s, %s, %s, %s) RETURNING *;
    """, (sensor.name, sensor.type, sensor.location, sensor.unit))
    new_sensor = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    result = dict(new_sensor)
    result["value"] = get_random_value(result["type"])
    return result

# --- PUT /api/v1/sensors/{sensor_id} ---
@app.put("/api/v1/sensors/{sensor_id}", response_model=SensorResponse, summary="Update sensor")
def update_sensor(sensor_id: int, sensor: SensorUpdate):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        UPDATE sensors
        SET name = %s, type = %s, location = %s, unit = %s
        WHERE id = %s RETURNING *;
    """, (sensor.name, sensor.type, sensor.location, sensor.unit, sensor_id))
    updated = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if not updated:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    result = dict(updated)
    result["value"] = get_random_value(result["type"])
    return result

# --- DELETE /api/v1/sensors/{sensor_id} ---
@app.delete("/api/v1/sensors/{sensor_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete sensor")
def delete_sensor(sensor_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM sensors WHERE id = %s;", (sensor_id,))
    deleted = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()

    if deleted == 0:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return

# --- PATCH /api/v1/sensors/{sensor_id}/value ---
@app.patch("/api/v1/sensors/{sensor_id}/value", summary="Update sensor value/status")
def update_sensor_value(sensor_id: int, update: SensorValueUpdate):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE sensors
        SET status = %s
        WHERE id = %s;
    """, (update.status, sensor_id))
    updated = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()

    if updated == 0:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    return {"message": "Sensor status updated"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)