import ssl

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
}

def format_mesos(n):
    if n is None:
        return "N/A"
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.2f}b"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.2f}m"
    if n >= 10_000:
        return f"{round(n / 1_000):,}k"
    return f"{n:,.0f}"

def format_full_mesos(n):
    if n is None:
        return "N/A"
    return f"{n:,.0f} mesos"
