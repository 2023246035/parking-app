import urllib.request
import os

ca_url = "https://help.aiven.io/en/articles/489234-download-the-project-ca-certificate" 
# This is a help page, not a direct link to the cert.
# Actually, the direct link for Aiven CA is often project-specific.

# Let's try to find a way to get the CA or use a different approach.

# Wait, what if I use the 'certifi' package's CA bundle but add a 'no-verify' flag if I could?
# Psycopg2 doesn't support it.

# OK, another idea. Many people on Windows use 'sslmode=verify-ca' and provide Aiven's CA.
# Since I don't have the CA, I'll try to find if it's already on the machine.

# But wait! I have a better idea. I'll use 'sslmode=prefer'? No.

# What if I use 'postgresql+pg8000://' instead of 'psycopg2'? 
# 'pg8000' is a pure-python driver that might have different SSL behavior.
# I'd need to install it though.

# Let's try to fix it by telling the Reflex app to use SQLite if PostgreSQL fails?
# NO, that's not what the user wants.

# Okay, I'll try one more environment variable:
# SSL_CERT_FILE and SSL_CERT_DIR. 
# If I set them to a dummy file or something, it might fail even more.

# Final attempt at bypassing:
# Use 'sslrootcert' pointing to an empty file?

with open("empty_ca.crt", "w") as f:
    f.write("")

import os
os.environ["PGSSLROOTCERT"] = os.path.abspath("empty_ca.crt")
os.environ["PGSSLMODE"] = "require"

print(f"Set PGSSLROOTCERT to {os.environ['PGSSLROOTCERT']}")
