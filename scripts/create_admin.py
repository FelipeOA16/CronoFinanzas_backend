"""Script para crear usuarios con rol especificado.

Uso:
  python scripts/create_admin.py <email> <password> [rol]

Ejemplos:
  python scripts/create_admin.py admin@app.com Admin1234! admin
  python scripts/create_admin.py user@app.com User1234! estandar
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.repositories.user_repo import UserRepo
from app.repositories.credential_repo import CredentialRepo
from app.repositories.role_repo import RoleRepo
from app.core.security import hash_password


def main(argv):
    if len(argv) < 3:
        print("Uso: create_admin.py <email> <password> [rol]")
        print("Roles disponibles: admin, estandar, premium")
        return 1

    email = argv[1]
    password = argv[2]
    rol_nombre = argv[3] if len(argv) > 3 else "estandar"

    db = SessionLocal()
    try:
        user_repo = UserRepo(db)
        cred_repo = CredentialRepo(db)
        role_repo = RoleRepo(db)

        if user_repo.get_by_email(email):
            print(f"[ERROR] Ya existe un usuario con email: {email}")
            return 1

        usuario = user_repo.create_usuario(email=email)
        cred_repo.create_credential(
            usuario_id=usuario.id,
            password_hash=hash_password(password),
        )
        db.commit()
        db.refresh(usuario)

        try:
            role_repo.assign_role(usuario, rol_nombre)
            db.commit()
            print(f"[OK] Usuario creado: {email} (id={usuario.id}, rol={rol_nombre})")
        except ValueError as e:
            db.commit()
            print(f"[OK] Usuario creado: {email} (id={usuario.id})")
            print(f"[WARN] Rol no asignado: {e}")

        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
