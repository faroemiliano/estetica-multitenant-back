import os

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("SECRET_KEY", "test-secret")

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models
from app.database import Base, get_db
from app.main import app
from app.models.estetica import Estetica
from app.models.membership import Membership
from app.models.profesional import Profesional
from app.models.servicio import Servicio
from app.models.user import User
from app.security import create_access_token


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestingSession() as db:
        aura = Estetica(nombre="Aura", slug="aura")
        bel = Estetica(nombre="Bel", slug="bel")
        db.add_all([aura, bel])
        db.flush()

        admin_aura = User(email="admin-aura@test.com", estetica_id=aura.id, role="admin")
        admin_bel = User(email="admin-bel@test.com", estetica_id=bel.id, role="admin")
        multi = User(email="multi@test.com", estetica_id=aura.id, role="cliente")
        db.add_all([admin_aura, admin_bel, multi])
        db.flush()
        db.add_all([
            Membership(user_id=admin_aura.id, estetica_id=aura.id, role="admin"),
            Membership(user_id=admin_bel.id, estetica_id=bel.id, role="admin"),
            Membership(user_id=multi.id, estetica_id=aura.id, role="cliente"),
            Membership(user_id=multi.id, estetica_id=bel.id, role="admin"),
        ])
        profesional_bel = Profesional(nombre="Profesional Bel", estetica_id=bel.id)
        db.add(profesional_bel)
        db.flush()
        db.add(Servicio(
            nombre="Servicio Bel",
            descripcion="Solo Bel",
            duracion=30,
            precio=100,
            estetica_id=bel.id,
            profesional_id=profesional_bel.id,
        ))
        db.commit()


def token_for(email: str, tenant_slug: str, claimed_role: str | None = None):
    with TestingSession() as db:
        user = db.query(User).filter(User.email == email).one()
        tenant = db.query(Estetica).filter(Estetica.slug == tenant_slug).one()
        membership = db.query(Membership).filter_by(
            user_id=user.id, estetica_id=tenant.id
        ).one()
        return create_access_token({
            "sub": str(user.id),
            "estetica_id": tenant.id,
            "slug": tenant.slug,
            "role": claimed_role or membership.role,
        })


def auth(token: str):
    return {"Authorization": f"Bearer {token}"}


def test_admin_cannot_update_another_tenant_by_changing_slug():
    response = client.put(
        "/esteticas/bel",
        json={"whatsapp": "123"},
        headers=auth(token_for("admin-aura@test.com", "aura")),
    )
    assert response.status_code == 404


def test_admin_cannot_edit_service_from_another_tenant():
    with TestingSession() as db:
        servicio_bel = db.query(Servicio).filter(Servicio.nombre == "Servicio Bel").one()
    response = client.put(
        f"/servicios/{servicio_bel.id}",
        json={
            "nombre": "Hack",
            "descripcion": "Hack",
            "duracion": 30,
            "precio": 1,
            "profesional_id": None,
        },
        headers=auth(token_for("admin-aura@test.com", "aura")),
    )
    assert response.status_code == 404


def test_membership_role_overrides_forged_role_in_token():
    forged = token_for("multi@test.com", "aura", claimed_role="admin")
    response = client.post(
        "/profesionales",
        json={"nombre": "No autorizado"},
        headers=auth(forged),
    )
    assert response.status_code == 403


def test_same_identity_can_have_different_roles_per_tenant():
    aura_response = client.get("/dashboard/stats", headers=auth(token_for("multi@test.com", "aura")))
    bel_response = client.get("/dashboard/stats", headers=auth(token_for("multi@test.com", "bel")))
    assert aura_response.status_code == 403
    assert bel_response.status_code == 200


def test_token_without_membership_is_rejected():
    with TestingSession() as db:
        user = db.query(User).filter(User.email == "admin-aura@test.com").one()
        bel = db.query(Estetica).filter(Estetica.slug == "bel").one()
    token = create_access_token({
        "sub": str(user.id), "estetica_id": bel.id, "role": "admin", "slug": "bel"
    })
    response = client.get("/dashboard/stats", headers=auth(token))
    assert response.status_code == 401


def test_google_login_creates_one_identity_with_membership_per_slug(monkeypatch):
    google_data = {
        "email": "nueva@test.com",
        "sub": "google-123",
        "name": "Nueva Cliente",
        "picture": "https://example.com/foto.jpg",
    }
    monkeypatch.setattr(
        "app.routes.auth.id_token.verify_oauth2_token",
        lambda *args, **kwargs: google_data,
    )

    aura_response = client.post(
        "/google-login", json={"credential": "fake", "slug": "aura"}
    )
    bel_response = client.post(
        "/google-login", json={"credential": "fake", "slug": "bel"}
    )

    assert aura_response.status_code == 200
    assert bel_response.status_code == 200
    assert aura_response.json()["user"]["id"] == bel_response.json()["user"]["id"]
    with TestingSession() as db:
        user = db.query(User).filter(User.email == "nueva@test.com").one()
        assert db.query(Membership).filter(Membership.user_id == user.id).count() == 2
