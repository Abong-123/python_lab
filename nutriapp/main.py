#----------------------------------- main.py -----------------------------------#
from fastapi import FastAPI, HTTPException, Depends, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session, joinedload
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError
from starlette.middleware.sessions import SessionMiddleware
import os
from dotenv import load_dotenv
load_dotenv()
import cloudinary
import cloudinary.uploader
from cloudinary_config import cloudinary
import shutil
#------------------------------- import models and schemas -----------------------------------#
import models
import schemas
from database import SessionLocal, engine, get_db
from datetime import datetime, date
from typing import List
from security import hash_password, verify_password

#------------------------------- settings -----------------------------------#
app = FastAPI()
app.add_middleware(
    SessionMiddleware,
    secret_key="SECRET_YANG_RAHASIA_BANGET",
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Baru routes
templates = Jinja2Templates(directory="templates")



#------------------------------- Jinja -----------------------------------#
@app.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
def register(
    request: Request,
    nama: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):

    existing = db.query(models.User).filter(
        models.User.nama == nama
    ).first()

    if existing: 
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "nama sudah digunakan"}
        )
    
    existing = db.query(models.User).filter(
        models.User.email == email
    ).first()

    if existing: 
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "email sudah digunakan"}
        )
    
    hashed_password = hash_password(password)
    new_user = models.User(
        nama=nama,
        email=email,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()

    return RedirectResponse(url="/login", status_code=303)

@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.email == email
    ).first()

    if not user or not verify_password(user.password, password):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "email atau password salah"}
        )
    request.session["user_id"] = user.id
    request.session["user_name"] = user.nama
    return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    if "user_id" not in request.session:
        return RedirectResponse(url="/login", status_code=303)
    user_id = request.session["user_id"]
    user = db.query(models.User).filter(
        models.User.id == request.session["user_id"]
    ).first()
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "nama": request.session["user_name"],
            "user": user
        }
    )

@app.get("/profile", response_class=HTMLResponse)
def profile(request: Request, db: Session = Depends(get_db)):
    if "user_id" not in request.session:
        return RedirectResponse(url="/login", status_code=303)
    
    user = db.query(models.User).filter(
        models.User.id == request.session["user_id"]
    ).first()

    count = 2
    if user.photo:   count += 1
    if user.alamat:  count += 1
    if user.bio:     count += 1
    profile_pct = int(count / 5 * 100)

    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user,
        "profile_pct": profile_pct
    })

@app.get("/edit_profile", response_class=HTMLResponse)
def edit_profile(request: Request, db: Session = Depends(get_db)):
    if "user_id" not in request.session:
        return RedirectResponse(url="/login", status_code=303)
    user_id = request.session["user_id"]
    user = db.query(models.User).filter(models.User.id == user_id).first()

    return templates.TemplateResponse(
        "edit_profile.html",
        {
            "request": request,
            "user": user
        }
    )

@app.post("/edit_profile")
async def update_profile(
    request: Request,
    nama: str = Form(...),
    alamat: str = Form(...),
    bio: str = Form(...),
    photo: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    if "user_id" not in request.session:
        return RedirectResponse(url="/login", status_code=303)
    
    user_id = request.session["user_id"]
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        return RedirectResponse(url="/login", status_code=303)

    if nama != user.nama:
        existing = db.query(models.User).filter(
            models.User.nama == nama,
            models.User.id != user.id  # ← penting!
        ).first()

        if existing:
            return templates.TemplateResponse(
                "profile.html",
                {"request": request, "user": user, "error": "Nama sudah digunakan"}
            )

    if photo and photo.filename != "":
        print("filename:", photo.filename)  
        result = cloudinary.uploader.upload(
            await photo.read(),
            folder="nutriapp/profile",
            public_id=f"user_{user.id}",
            overwrite=True,
            resource_type="image"
        )
        print("url:", result["secure_url"])
        user.photo = result["secure_url"]
    else:
        print("tidak ada foto yang diupload")
    user.nama = nama
    user.alamat = alamat
    user.bio = bio

    db.commit()
    request.session["user_name"] = user.nama
    return RedirectResponse(url="/profile", status_code=303)

@app.get("/resep", response_class=HTMLResponse)
def list_resep(request: Request, db: Session = Depends(get_db)):

    reseps = db.query(
        Resep.id,
        Resep.nama,
        Resep.deskripsi,
        Resep.foto
    ).all()

    return templates.TemplateResponse(
        "reseps.html",
        {
            "request": request,
            "reseps": reseps
        }
    )

@app.get("/resep/{id}", response_class=HTMLResponse)
def resep_detail(id: int, request: Request, db: Session = Depends(get_db)):

    resep = db.query(Resep).filter(Resep.id == id).first()

    if not resep:
        raise HTTPException(status_code=404, detail="Resep tidak ditemukan")

    return templates.TemplateResponse(
        "resep_detail.html",
        {
            "request": request,
            "resep": resep
        }
    )

@app.get("/nutrisi/input", response_class=HTMLResponse)
def nutrisi_input_form(request: Request, db: Session = Depends(get_db)):
    if "user_id" not in request.session:
        return RedirectResponse(url="/login", status_code=303)
    user = db.query(models.User).filter(
        models.User.id == request.session["user_id"]
    ).first()
    return templates.TemplateResponse("nutrisi_input.html", {
        "request": request, "user": user
    })


@app.post("/nutrisi/input")
def nutrisi_input(
    request: Request,
    nama: str = Form(...),
    amount: float = Form(100),
    kalori: float = Form(None),
    karbohidrat: float = Form(None),
    protein: float = Form(None),
    lemak: float = Form(None),
    serat: float = Form(None),
    sodium: float = Form(None),
    kalium: float = Form(None),
    db: Session = Depends(get_db)
):
    if "user_id" not in request.session:
        return RedirectResponse(url="/login", status_code=303)

    user = db.query(models.User).filter(
        models.User.id == request.session["user_id"]
    ).first()

    # Cek duplikat nama per user
    existing = db.query(models.Nutrisi).filter(
        models.Nutrisi.nama == nama,
        models.Nutrisi.user_id == user.id
    ).first()
    if existing:
        return templates.TemplateResponse("nutrisi_input.html", {
            "request": request, "user": user,
            "error": f"Bahan '{nama}' sudah pernah kamu tambahkan"
        })

    # Simpan bahan
    nutrisi = models.Nutrisi(
        user_id=user.id,
        nama=nama, amount=amount,
        kalori=kalori, karbohidrat=karbohidrat,
        protein=protein, lemak=lemak,
        serat=serat, sodium=sodium, kalium=kalium
    )
    db.add(nutrisi)
    db.flush()  # biar keitung di query berikutnya

    # Hitung total bahan user setelah insert
    total = db.query(models.Nutrisi).filter(
        models.Nutrisi.user_id == user.id
    ).count()

    # Upgrade role kalau sudah 5 bahan dan masih normal
    if total >= 5 and user.role == models.UserRole.normal:
        user.role = models.UserRole.ahli_gizi
        request.session["user_role"] = "ahli_gizi"

    db.commit()

    success_msg = f"'{nama}' berhasil ditambahkan!"
    if total >= 5 and user.role == models.UserRole.ahli_gizi:
        success_msg = f"Selamat! Kamu mendapat lencana Ahli Gizi 🎉"

    return templates.TemplateResponse("nutrisi_input.html", {
        "request": request, "user": user,
        "success": success_msg
    })

@app.get("/nutrisi", response_class=HTMLResponse)
def nutrisi_list(request: Request, db: Session = Depends(get_db)):
    if "user_id" not in request.session:
        return RedirectResponse(url="/login", status_code=303)
    user = db.query(models.User).filter(
        models.User.id == request.session["user_id"]
    ).first()
    # Ambil semua nutrisi dari semua user (database publik)
    nutrisis = db.query(models.Nutrisi).order_by(models.Nutrisi.nama).all()
    return templates.TemplateResponse("nutrisi_list.html", {
        "request": request,
        "user": user,
        "nutrisis": nutrisis
    })


@app.get("/nutrisi/{id}", response_class=HTMLResponse)
def nutrisi_detail(id: int, request: Request, db: Session = Depends(get_db)):
    if "user_id" not in request.session:
        return RedirectResponse(url="/login", status_code=303)
    user = db.query(models.User).filter(
        models.User.id == request.session["user_id"]
    ).first()
    nutrisi = db.query(models.Nutrisi).filter(
        models.Nutrisi.id == id
    ).first()
    if not nutrisi:
        raise HTTPException(status_code=404, detail="Bahan tidak ditemukan")
    return templates.TemplateResponse("nutrisi_detail.html", {
        "request": request,
        "user": user,
        "nutrisi": nutrisi
    })

@app.post("/nutrisi/{id}/delete")
def nutrisi_delete(id: int, request: Request, db: Session = Depends(get_db)):
    if "user_id" not in request.session:
        return RedirectResponse(url="/login", status_code=303)
    nutrisi = db.query(models.Nutrisi).filter(models.Nutrisi.id == id).first()
    if not nutrisi:
        raise HTTPException(status_code=404)
    # Hanya pemilik atau admin
    user = db.query(models.User).filter(models.User.id == request.session["user_id"]).first()
    if nutrisi.user_id != user.id and user.role.value != "admin":
        raise HTTPException(status_code=403)
    db.delete(nutrisi)
    db.commit()
    return RedirectResponse(url="/nutrisi", status_code=303)

@app.get("/nutrisi/{id}/edit", response_class=HTMLResponse)
def nutrisi_edit_form(id: int, request: Request, db: Session = Depends(get_db)):
    if "user_id" not in request.session:
        return RedirectResponse(url="/login", status_code=303)
    user = db.query(models.User).filter(
        models.User.id == request.session["user_id"]
    ).first()
    nutrisi = db.query(models.Nutrisi).filter(models.Nutrisi.id == id).first()
    if not nutrisi:
        raise HTTPException(status_code=404)
    if nutrisi.user_id != user.id and user.role.value != "admin":
        raise HTTPException(status_code=403)
    return templates.TemplateResponse("nutrisi_edit.html", {
        "request": request, "user": user, "nutrisi": nutrisi
    })


@app.post("/nutrisi/{id}/edit")
def nutrisi_edit(
    id: int,
    request: Request,
    nama: str = Form(...),
    amount: float = Form(100),
    kalori: float = Form(None),
    karbohidrat: float = Form(None),
    protein: float = Form(None),
    lemak: float = Form(None),
    serat: float = Form(None),
    sodium: float = Form(None),
    kalium: float = Form(None),
    db: Session = Depends(get_db)
):
    if "user_id" not in request.session:
        return RedirectResponse(url="/login", status_code=303)
    user = db.query(models.User).filter(
        models.User.id == request.session["user_id"]
    ).first()
    nutrisi = db.query(models.Nutrisi).filter(models.Nutrisi.id == id).first()
    if not nutrisi:
        raise HTTPException(status_code=404)
    if nutrisi.user_id != user.id and user.role.value != "admin":
        raise HTTPException(status_code=403)

    # Cek duplikat nama (exclude diri sendiri)
    existing = db.query(models.Nutrisi).filter(
        models.Nutrisi.nama == nama,
        models.Nutrisi.user_id == user.id,
        models.Nutrisi.id != id
    ).first()
    if existing:
        return templates.TemplateResponse("nutrisi_edit.html", {
            "request": request, "user": user, "nutrisi": nutrisi,
            "error": f"Bahan '{nama}' sudah ada"
        })

    nutrisi.nama        = nama
    nutrisi.amount      = amount
    nutrisi.kalori      = kalori
    nutrisi.karbohidrat = karbohidrat
    nutrisi.protein     = protein
    nutrisi.lemak       = lemak
    nutrisi.serat       = serat
    nutrisi.sodium      = sodium
    nutrisi.kalium      = kalium

    db.commit()
    return RedirectResponse(url=f"/nutrisi/{id}", status_code=303)

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)



#------------------------------- Swagger -----------------------------------#
@app.post("/users")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(
        models.User.nama == user.nama
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Nama sudah digunakan")
    
    existing = db.query(models.User).filter(
        models.User.email == user.email
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email sudah digunakan")
    
    hashed_password = hash_password(user.password)
    new_user = models.User(
        nama=user.nama,
        email=user.email,
        password=hashed_password,
        alamat=user.alamat,
        photo=user.photo,
        bio=user.bio
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User berhasil didaftarkan", "user_id": new_user.id}

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    data = db.query(models.User).filter(models.User.id == user_id).first()

    if not data:
        return {"error": "data tidak ditemukan"}

    db.delete(data)
    db.commit()

    return{"message": "berhasil dihapus"}