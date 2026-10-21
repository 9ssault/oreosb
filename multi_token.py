"""Legacy entry — prefer main.py which auto-loads tokens.txt."""
import os
import sys
print("use: python main.py  (tokens.txt auto-loads as workers)")
print("redirecting...")
os.execv(sys.executable, [sys.executable, "main.py"])
