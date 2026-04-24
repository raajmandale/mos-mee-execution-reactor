cd backend
pip install -r requirements.txt
start cmd /k uvicorn main:app --reload

cd ../frontend
start index.html