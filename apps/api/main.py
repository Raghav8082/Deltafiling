from fastapi import FastAPI 

app = FastAPI(title='Delta filing Backend is Running')

@app.get('/')
def root():
    return{"message": "DeltaFiling API is now running" }

    
