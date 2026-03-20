import os
import io
import logging
import qrcode
from flask import Flask, request, jsonify, send_file
from pathlib import Path

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = Flask(__name__, static_folder="public", static_url_path="")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

PORT = int(os.environ.get("APP_PORT", 5000))
HOST = os.environ.get("APP_HOST", "0.0.0.0")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Serve the frontend."""
    index_path = Path(__file__).parent / "public" / "index.html"
    with open(index_path, "r") as f:
        return f.read(), 200, {"Content-Type": "text/html"}


@app.route("/health")
def health():
    """Health check endpoint used by validate_service.sh and monitoring."""
    return jsonify({"status": "healthy", "service": "qrcode-generator"}), 200


@app.route("/generate", methods=["POST"])
def generate():
    """
    Generate a QR code from the provided data.

    Request JSON:
        {
            "data": "https://example.com",
            "size":  10,          // optional, box size in pixels (default 10)
            "border": 4           // optional, border thickness (default 4)
        }

    Response:
        PNG image binary
    """
    body = request.get_json(silent=True)

    if not body or "data" not in body:
        return jsonify({"error": "Missing required field: data"}), 400

    data = body["data"].strip()
    if not data:
        return jsonify({"error": "Field 'data' must not be empty"}), 400

    box_size = int(body.get("size", 10))
    border = int(body.get("border", 4))

    if box_size < 1 or box_size > 50:
        return jsonify({"error": "Field 'size' must be between 1 and 50"}), 400

    if border < 0 or border > 20:
        return jsonify({"error": "Field 'border' must be between 0 and 20"}), 400

    try:
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=box_size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        logger.info("QR code generated for data: %s", data[:80])
        return send_file(buf, mimetype="image/png")

    except Exception as e:
        logger.error("Failed to generate QR code: %s", str(e))
        return jsonify({"error": "Failed to generate QR code", "detail": str(e)}), 500


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed"}), 405


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    logger.info("Starting QR Code Generator on %s:%s", HOST, PORT)
    app.run(host=HOST, port=PORT, debug=False)