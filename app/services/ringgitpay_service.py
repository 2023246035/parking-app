import hashlib
import logging
from typing import Dict, Any

class RinggitPayService:
    """Service to handle RinggitPay payment gateway logic."""
    
    @staticmethod
    def generate_checksum(app_id: str, currency: str, amount: str, order_id: str, request_key: str) -> str:
        """
        Generate SHA-256 checksum for RinggitPay request.
        Format: appId|currency|amount|orderId|REQUESTKEY
        """
        raw_string = f"{app_id}|{currency}|{amount}|{order_id}|{request_key}"
        checksum = hashlib.sha256(raw_string.encode()).hexdigest()
        logging.info(f"Generated checksum for Order ID {order_id}")
        return checksum

    @staticmethod
    def verify_checksum(params: Dict[str, Any], response_key: str) -> bool:
        """
        Verify SHA-256 checksum from RinggitPay response.
        Format: appId|orderId|amount|statusCode|RESPONSEKEY
        """
        app_id = params.get("appId", "")
        order_id = params.get("orderId", "")
        amount = params.get("amount", "")
        status_code = params.get("statusCode", "")
        received_checksum = params.get("checkSum", "")
        
        raw_string = f"{app_id}|{order_id}|{amount}|{status_code}|{response_key}"
        calculated_checksum = hashlib.sha256(raw_string.encode()).hexdigest()
        
        is_valid = calculated_checksum.lower() == received_checksum.lower()
        if not is_valid:
            logging.error(f"Checksum mismatch for Order ID {order_id}. Calculated: {calculated_checksum}, Received: {received_checksum}")
        
        return is_valid
