import uuid as _uuid

from sqlalchemy import BigInteger, Boolean, Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    uuid = Column(PGUUID(as_uuid=True), unique=True, nullable=False, default=_uuid.uuid4, index=True)
    nombre = Column(String(120), nullable=True)
    apellido = Column(String(120), nullable=True)
    nombre_mostrar = Column(String(150), nullable=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    email_normalizado = Column(String(255), unique=True, nullable=False, index=True)
    telefono = Column(String(30), nullable=True)
    pais = Column(String(80), nullable=True)
    zona_horaria = Column(String(80), nullable=False, default="America/Lima", server_default="America/Lima")
    idioma = Column(String(20), nullable=False, default="es-PE", server_default="es-PE")
    estado_cuenta = Column(String(30), nullable=False, default="activo", server_default="activo")
    foto_url = Column(Text, nullable=True)
    onboarding_completado = Column(Boolean, nullable=False, default=False, server_default="false")
    ultimo_acceso_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # relationships
    credencial = relationship("CredencialUsuario", back_populates="usuario", uselist=False)
    proveedores_auth = relationship("UsuarioProveedorAuth", back_populates="usuario")
    sesiones = relationship("SesionUsuario", back_populates="usuario")
    roles = relationship("Rol", secondary="usuario_roles", back_populates="usuarios")
    cuentas = relationship("Cuenta", back_populates="usuario", order_by="Cuenta.id")
    categorias = relationship("Categoria", back_populates="usuario")
    transacciones = relationship("Transaccion", back_populates="usuario")
    presupuestos  = relationship("Presupuesto", back_populates="usuario")
    deudas_prestamos = relationship("DeudaPrestamo", back_populates="usuario")
    metas_financieras = relationship("MetaFinanciera", back_populates="usuario")
    capturas_rapidas = relationship("CapturaRapida", back_populates="usuario")

    @property
    def email_verificado(self) -> bool:
        return self.credencial.email_verificado if self.credencial else False
