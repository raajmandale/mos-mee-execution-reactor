cd backend
pip install -r requirements.txt
uvicorn main:app --reload &

cd ../frontend
xdg-open index.html