"""
Image processing tool - Scale photo processing for measurement recognition.
Based on photoScalePhoto webhook analysis from exported flows.
"""

import logging
from typing import Any, Dict, Optional
import httpx
import json
import hashlib
import base64

logger = logging.getLogger(__name__)


async def process_scale_image(
    user_id: str,
    image_data: str,
    mime_type: str = "image/jpeg"
) -> Dict[str, Any]:
    """
    Process scale photo to extract weight measurement.
    
    Based on photoScalePhoto webhook analysis:
    - Endpoint: https://n8n.clivi.com.mx/webhook/imgfile-measurement-recognition
    - Method: POST
    - Payload: {"mime_type": "image/jpeg", "image-file": "$session.params.image.sha256"}
    - Timeout: 5 seconds
    
    Args:
        user_id: User identifier
        image_data: Base64 encoded image data or file path
        mime_type: Image MIME type (default: image/jpeg)
        
    Returns:
        Dict with extracted measurement data
    """
    logger.info(f"Processing scale image for user {user_id}")
    
    try:
        # Calculate SHA256 hash of image data (as per webhook analysis)
        if image_data.startswith('data:'):
            # Remove data URL prefix if present
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        image_sha256 = hashlib.sha256(image_bytes).hexdigest()
        
        # Prepare payload matching the exported webhook format
        payload = {
            "mime_type": mime_type,
            "image-file": image_sha256,
            "user_id": user_id
        }
        
        # Call n8n webhook endpoint
        response = await _call_n8n_webhook(payload)
        
        if response.get("success"):
            extracted_data = response.get("data", {})
            
            logger.info(f"Successfully processed scale image for user {user_id}")
            return {
                "success": True,
                "measurement": {
                    "type": "weight",
                    "value": extracted_data.get("weight"),
                    "unit": extracted_data.get("unit", "kg"),
                    "confidence": extracted_data.get("confidence", 0.0),
                    "extracted_text": extracted_data.get("extracted_text")
                },
                "image_hash": image_sha256,
                "processing_time": response.get("processing_time")
            }
        else:
            logger.error(f"Failed to process scale image: {response.get('error')}")
            return {
                "success": False,
                "error": response.get("error", "Image processing failed"),
                "image_hash": image_sha256
            }
            
    except Exception as e:
        logger.error(f"Error processing scale image: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


async def process_measurement_image(
    user_id: str,
    image_data: str,
    measurement_type: str,
    mime_type: str = "image/jpeg"
) -> Dict[str, Any]:
    """
    Process measurement device image (glucometer, scale, etc.).
    
    Extended functionality for different measurement types.
    """
    logger.info(f"Processing {measurement_type} image for user {user_id}")
    
    try:
        # Calculate image hash
        if image_data.startswith('data:'):
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        image_sha256 = hashlib.sha256(image_bytes).hexdigest()
        
        # Prepare payload with measurement type
        payload = {
            "mime_type": mime_type,
            "image-file": image_sha256,
            "measurement_type": measurement_type,
            "user_id": user_id
        }
        
        # Route to appropriate processing endpoint
        if measurement_type == "weight":
            endpoint = "imgfile-measurement-recognition"
        elif measurement_type == "glucose":
            endpoint = "imgfile-glucose-recognition"
        else:
            endpoint = "imgfile-general-recognition"
        
        response = await _call_n8n_webhook(payload, endpoint)
        
        return {
            "success": response.get("success", False),
            "measurement": response.get("data", {}),
            "image_hash": image_sha256,
            "measurement_type": measurement_type
        }
        
    except Exception as e:
        logger.error(f"Error processing {measurement_type} image: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "measurement_type": measurement_type
        }


async def validate_image_quality(
    image_data: str,
    expected_content: str = "scale"
) -> Dict[str, Any]:
    """
    Validate image quality before processing.
    """
    try:
        # Basic image validation
        if image_data.startswith('data:'):
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        image_size = len(image_bytes)
        
        # Minimum size check (10KB)
        if image_size < 10240:
            return {
                "valid": False,
                "reason": "image_too_small",
                "message": "La imagen es muy pequeña. Por favor toma una foto más clara."
            }
        
        # Maximum size check (10MB)
        if image_size > 10485760:
            return {
                "valid": False,
                "reason": "image_too_large", 
                "message": "La imagen es muy grande. Por favor comprime la imagen."
            }
        
        return {
            "valid": True,
            "size": image_size,
            "message": "Imagen válida para procesamiento"
        }
        
    except Exception as e:
        return {
            "valid": False,
            "reason": "invalid_format",
            "message": "Formato de imagen no válido",
            "error": str(e)
        }


async def _call_n8n_webhook(
    payload: Dict[str, Any],
    endpoint: str = "imgfile-measurement-recognition"
) -> Dict[str, Any]:
    """
    Call n8n webhook endpoint for image processing.
    
    Based on webhook analysis:
    - Base URL: https://n8n.clivi.com.mx/webhook/
    - Timeout: 5 seconds
    - Method: POST
    """
    n8n_base_url = "https://n8n.clivi.com.mx/webhook"
    full_url = f"{n8n_base_url}/{endpoint}"
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                full_url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "DrClivi-ADK/1.0"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "data": result,
                    "processing_time": response.elapsed.total_seconds()
                }
            else:
                logger.error(f"n8n webhook error: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "status_code": response.status_code
                }
                
    except httpx.TimeoutException:
        logger.error("n8n webhook timeout")
        return {
            "success": False,
            "error": "Processing timeout - please try again",
            "timeout": True
        }
    except Exception as e:
        logger.error(f"n8n webhook exception: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


# Image processing utilities
def get_image_instructions(measurement_type: str) -> Dict[str, Any]:
    """Get image capture instructions by measurement type"""
    instructions = {
        "weight": {
            "title": "Foto de báscula",
            "steps": [
                "Coloca la báscula en superficie plana",
                "Asegúrate de que el display sea claramente visible",
                "Toma la foto con buena iluminación",
                "Mantén el teléfono horizontal y estable"
            ],
            "tips": [
                "Evita reflejos en el display",
                "No uses flash si no es necesario",
                "Acércate lo suficiente para leer el número"
            ]
        },
        "glucose": {
            "title": "Foto de glucómetro",
            "steps": [
                "Espera a que aparezca el resultado final",
                "Asegúrate de que el número sea visible",
                "Toma la foto directamente al display",
                "Verifica que se vea la unidad (mg/dL)"
            ],
            "tips": [
                "No muevas el glucómetro durante la foto",
                "Limpia el display si está empañado",
                "Toma la foto antes de que se apague"
            ]
        }
    }
    
    return instructions.get(measurement_type, {
        "title": "Foto de medición",
        "steps": ["Toma una foto clara del dispositivo"],
        "tips": ["Asegúrate de que el resultado sea visible"]
    })
