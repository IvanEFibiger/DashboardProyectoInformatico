import jwt, flask
print("jwt file ->", getattr(jwt, "__file__", None))
print("jwt version ->", getattr(jwt, "__version__", None))
print("flask file ->", getattr(flask, "__file__", None))
print("flask version ->", getattr(flask, "__version__", None))
