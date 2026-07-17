from pydantic import BaseModel


class NotificacionOut(BaseModel):
    tipo: str             # "alerta" | "excedido"
    titulo: str
    mensaje: str
    presupuesto_id: int
    porcentaje: float
