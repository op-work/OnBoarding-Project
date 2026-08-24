import base64
from pathlib import Path
from config import BASE_DIR

def get_logo_data_uri() -> str:
    """
    Finds and returns the company logo as a Base64 Data URI string.
    Checks the 'assets' directory for custom logo files:
    - logo.png, logo.svg, logo.jpg, logo.jpeg, logo.webp
    - company_logo.png, company_logo.svg, company_logo.jpg, company_logo.jpeg
    
    If a custom logo file is found, it is encoded to Base64.
    If no custom logo file exists, returns a high quality default SVG logo.
    """
    assets_dir = BASE_DIR / "assets"
    
    logo_names = [
        "logo.png", "logo.jpeg", "logo.jpg", "logo.webp", "logo.svg",
        "company_logo.png", "company_logo.jpeg", "company_logo.jpg", "company_logo.svg"
    ]
    
    for name in logo_names:
        file_path = assets_dir / name
        if file_path.exists() and file_path.is_file():
            try:
                suffix = file_path.suffix.lower()
                mime_types = {
                    ".png": "image/png",
                    ".svg": "image/svg+xml",
                    ".jpg": "image/jpeg",
                    ".jpeg": "image/jpeg",
                    ".webp": "image/webp"
                }
                mime_type = mime_types.get(suffix, "image/png")
                with open(file_path, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode("utf-8")
                return f"data:{mime_type};base64,{encoded}"
            except Exception:
                pass
                
    # Fallback SVG Logo
    default_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 70" width="320" height="70">
        <defs>
            <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#2563EB" />
                <stop offset="100%" stop-color="#1E40AF" />
            </linearGradient>
        </defs>
        <rect x="5" y="5" width="60" height="60" rx="14" fill="url(#logoGrad)"/>
        <circle cx="35" cy="35" r="16" fill="#60A5FA" opacity="0.4"/>
        <path d="M25 35 L35 23 L45 35 L35 47 Z" fill="#FFFFFF"/>
        <text x="82" y="44" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-weight="900" font-size="28" fill="#1E40AF" letter-spacing="1">COMPANY</text>
        <text x="238" y="44" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-weight="500" font-size="28" fill="#3B82F6" letter-spacing="1">LOGO</text>
    </svg>"""
    encoded_default = base64.b64encode(default_svg.encode("utf-8")).decode("utf-8")
    return f"data:image/svg+xml;base64,{encoded_default}"
