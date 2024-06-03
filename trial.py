import jwt

token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJWRVIiOiI1cjVHQSIsImlzcyI6IkNhcHRjaGFNYW4iLCJleHAiOjE3MTczODU3OTZ9.flBmEGxCVacBz7ATx-w77FMk2_W3zj843sNAdWd4wO0"

decoded = jwt.decode(token, options={"verify_signature": False})['VER']
print(decoded)