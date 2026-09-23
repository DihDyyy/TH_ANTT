import logging, logging.handlers, gzip, json, os, re, hashlib
from datetime import datetime, timezone

LOG_FILE = "secure.log"
SIGNATURE_FILE = "secure.log.sig"
MAX_LOG_SIZE = 1024 * 1024
BACKUP_COUNT = 2

PII_PATTERNS = {
    "email": r'[\w\.-]+@[\w\.-]+\.\w+',
    "token": r'(?i)(token|apikey|key|password)\s*=\s*["\']?[\w\-]{8,}["\']?',
}

def mask_pii(value):
    if isinstance(value, dict):
        return {key: mask_pii(val) for key, val in value.items()}
    if isinstance(value, list):
        return [mask_pii(item) for item in value]
    if isinstance(value, tuple):
        return tuple(mask_pii(item) for item in value)
    if isinstance(value, str):
        text = value
        for label, pattern in PII_PATTERNS.items():
            text = re.sub(pattern, f"<{label}_masked>", text, flags=re.IGNORECASE)
        return text
    return value

def hash_line(line):
    return hashlib.sha256(line.encode('utf-8')).hexdigest()

def append_signature(line):
    with open(SIGNATURE_FILE, "a", encoding="utf-8") as f:
        f.write(hash_line(line) + "\n")

class JSONFormatter(logging.Formatter):
    def format(self, record):
        if hasattr(record, "_formatted_json"):
            return record._formatted_json
        message = mask_pii(record.getMessage())
        record_dict = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "level": record.levelname,
            "message": message,
        }
        if hasattr(record, "data"):
            record_dict["data"] = mask_pii(record.data)
        if hasattr(record, "results"):
            record_dict["results"] = mask_pii(record.results)
        json_line = json.dumps(record_dict, ensure_ascii=False)
        record._formatted_json = json_line
        return json_line

class GZipRotator:
    def __call__(self, source, dest):
        with open(source, 'rb') as f_in, gzip.open(dest + ".gz", 'wb') as f_out:
            f_out.writelines(f_in)
        os.remove(source)

class SecureRotatingFileHandler(logging.handlers.RotatingFileHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            super().emit(record)
            append_signature(msg)
        except Exception:
            self.handleError(record)

def get_secure_logger():
    logger = logging.getLogger("secure_logger")
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        handler = SecureRotatingFileHandler(
            LOG_FILE, maxBytes=MAX_LOG_SIZE, backupCount=BACKUP_COUNT, encoding="utf-8")
        handler.setFormatter(JSONFormatter())
        handler.rotator = GZipRotator()
        logger.addHandler(handler)
    logger.propagate = False
    return logger

secure_logger = get_secure_logger()
