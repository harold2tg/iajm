from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.domains.reportes.schemas import (
    ActividadReporteResponse,
    AsistenciaMiembroItem,
    AsistenciaResponse,
    BalanceResponse,
    CuotaAsesorItem,
    CuotasResponse,
    DetalleGastoItem,
    DetalleIngresoItem,
    DonacionItem,
    DonacionesResponse,
    EncuentroReporteItem,
    EncuentrosResponse,
    GrupoConteo,
    InventarioResponse,
    ItemInventarioItem,
    ProductoActividadItem,
    TiendaResponse,
    UsuarioReporteItem,
    UsuariosResponse,
    VentaDiaItem,
)


# ── R01 Balance ──────────────────────────────────────────────────────────────

def get_balance(db: Session, mes: int, anio: int) -> BalanceResponse:
    from app.domains.tesoreria.models import OtroIngreso
    from app.domains.asesores.models import CuotaAsesor, Asesor, EstadoCuotaEnum
    from app.domains.tienda.models import VentaDia, EstadoVentaEnum
    from app.domains.gastos.models import Gasto, CategoriaGasto

    # Otros ingresos del período
    otros = (
        db.query(OtroIngreso)
        .filter(
            func.extract("month", OtroIngreso.fecha) == mes,
            func.extract("year", OtroIngreso.fecha) == anio,
        )
        .all()
    )

    # Cuotas pagadas del período
    cuotas = (
        db.query(CuotaAsesor, Asesor)
        .join(Asesor, CuotaAsesor.asesor_id == Asesor.id)
        .filter(
            CuotaAsesor.mes == mes,
            CuotaAsesor.anio == anio,
            CuotaAsesor.estado == EstadoCuotaEnum.pagado,
        )
        .all()
    )

    # Ventas tienda cerradas del período
    ventas = (
        db.query(VentaDia)
        .filter(
            func.extract("month", VentaDia.fecha) == mes,
            func.extract("year", VentaDia.fecha) == anio,
            VentaDia.estado == EstadoVentaEnum.cerrado,
        )
        .all()
    )

    # Gastos del período
    gastos = (
        db.query(Gasto, CategoriaGasto)
        .join(CategoriaGasto, Gasto.categoria_id == CategoriaGasto.id)
        .filter(
            Gasto.mes == mes,
            func.extract("year", Gasto.fecha) == anio,
        )
        .all()
    )

    # Armar detalle ingresos
    detalle_ingresos: list[DetalleIngresoItem] = []
    for o in otros:
        detalle_ingresos.append(DetalleIngresoItem(
            descripcion=o.descripcion,
            valor=float(o.valor),
            fecha=o.fecha,
            tipo="otro_ingreso",
        ))
    for cuota, asesor in cuotas:
        detalle_ingresos.append(DetalleIngresoItem(
            descripcion=f"Cuota asesor: {asesor.nombre_completo}",
            valor=float(cuota.monto),
            fecha=cuota.fecha_pago or date(anio, mes, 1),
            tipo="cuota_asesor",
        ))
    for venta in ventas:
        detalle_ingresos.append(DetalleIngresoItem(
            descripcion=f"Venta tienda {venta.fecha}",
            valor=float(venta.total_calculado),
            fecha=venta.fecha,
            tipo="venta_tienda",
        ))

    # Armar detalle gastos
    detalle_gastos: list[DetalleGastoItem] = []
    for gasto, cat in gastos:
        detalle_gastos.append(DetalleGastoItem(
            descripcion=gasto.descripcion,
            valor_total=float(gasto.valor_total),
            fecha=gasto.fecha,
            categoria=cat.nombre,
        ))

    total_ingresos = sum(i.valor for i in detalle_ingresos)
    total_gastos = sum(g.valor_total for g in detalle_gastos)

    return BalanceResponse(
        mes=mes,
        anio=anio,
        total_ingresos=total_ingresos,
        total_gastos=total_gastos,
        saldo=total_ingresos - total_gastos,
        detalle_ingresos=detalle_ingresos,
        detalle_gastos=detalle_gastos,
    )


# ── R02 Actividad Pro-Fondos ──────────────────────────────────────────────────

def get_reporte_actividad(db: Session, actividad_id: uuid.UUID) -> ActividadReporteResponse:
    from fastapi import HTTPException, status
    from app.domains.tesoreria.models import ActividadProFondos

    actividad = db.query(ActividadProFondos).filter(ActividadProFondos.id == actividad_id).first()
    if actividad is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Actividad no encontrada")

    total_ingresos = sum(
        float(p.cantidad) * float(p.precio_venta) for p in actividad.productos
    )
    total_costos = sum(
        float(p.cantidad) * float(p.costo_unitario)
        for p in actividad.productos
        if not p.es_donado and p.costo_unitario is not None
    )
    productos = [
        ProductoActividadItem(
            id=p.id,
            nombre=p.nombre,
            cantidad=p.cantidad,
            costo_unitario=float(p.costo_unitario) if p.costo_unitario else None,
            precio_venta=float(p.precio_venta),
            es_donado=p.es_donado,
        )
        for p in actividad.productos
    ]

    return ActividadReporteResponse(
        actividad_id=actividad.id,
        nombre=actividad.nombre,
        tipo=actividad.tipo,
        fecha=actividad.fecha,
        responsable=actividad.responsable,
        productos=productos,
        total_ingresos=total_ingresos,
        total_costos=total_costos,
        utilidad=total_ingresos - total_costos,
    )


# ── R03 Donaciones ────────────────────────────────────────────────────────────

def get_donaciones(
    db: Session,
    mes: Optional[int],
    anio: Optional[int],
    tipo: Optional[str],
) -> DonacionesResponse:
    from app.domains.tesoreria.models import Donacion, TipoDonacionEnum

    q = db.query(Donacion)
    if mes is not None:
        q = q.filter(func.extract("month", Donacion.fecha) == mes)
    if anio is not None:
        q = q.filter(func.extract("year", Donacion.fecha) == anio)
    if tipo is not None:
        q = q.filter(Donacion.tipo == tipo)

    donaciones = q.all()

    total_efectivo = sum(
        float(d.valor) for d in donaciones
        if d.tipo == TipoDonacionEnum.efectivo and d.valor is not None
    )
    total_especie = sum(
        float(d.valor_estimado) for d in donaciones
        if d.tipo == TipoDonacionEnum.especie and d.valor_estimado is not None
    )

    items = [DonacionItem.model_validate(d) for d in donaciones]

    return DonacionesResponse(
        total_efectivo=total_efectivo,
        total_especie=total_especie,
        donaciones=items,
    )


# ── R04 Inventario ────────────────────────────────────────────────────────────

def get_inventario(db: Session) -> InventarioResponse:
    from app.domains.inventario.models import ItemInventario

    items = db.query(ItemInventario).all()

    total_items = sum(i.cantidad for i in items)

    por_tipo: dict[str, int] = {}
    por_origen: dict[str, int] = {}
    for item in items:
        tipo_key = item.tipo.value if item.tipo else "sin_tipo"
        por_tipo[tipo_key] = por_tipo.get(tipo_key, 0) + item.cantidad

        origen_key = item.origen.value if item.origen else "sin_origen"
        por_origen[origen_key] = por_origen.get(origen_key, 0) + item.cantidad

    return InventarioResponse(
        total_items=total_items,
        por_tipo=[GrupoConteo(clave=k, cantidad=v) for k, v in por_tipo.items()],
        por_origen=[GrupoConteo(clave=k, cantidad=v) for k, v in por_origen.items()],
        items=[ItemInventarioItem.model_validate(i) for i in items],
    )


# ── R05 Asistencia ────────────────────────────────────────────────────────────

def get_asistencia(
    db: Session,
    grupo_id: Optional[uuid.UUID],
    mes: Optional[int],
    anio: Optional[int],
    actor_grupos: list[uuid.UUID],
    actor_roles: list[str],
) -> AsistenciaResponse:
    from app.domains.miembros.models import Miembro
    from app.domains.encuentros.models import Encuentro, AsistenciaEncuentro, EstadoAsistenciaEnum

    hoy = date.today()

    # Filtrar miembros
    q_miembros = db.query(Miembro).filter(Miembro.activo == True)  # noqa: E712
    if grupo_id is not None:
        q_miembros = q_miembros.filter(Miembro.grupo_id == grupo_id)
    elif "asesor_grupo" in actor_roles and "administrador" not in actor_roles and "observador" not in actor_roles:
        if actor_grupos:
            q_miembros = q_miembros.filter(Miembro.grupo_id.in_(actor_grupos))
        else:
            return AsistenciaResponse(miembros=[])

    miembros = q_miembros.all()
    if not miembros:
        return AsistenciaResponse(miembros=[])

    miembro_ids = [m.id for m in miembros]

    # Filtrar encuentros del período
    q_enc = db.query(Encuentro)
    grupos_miembros = list({m.grupo_id for m in miembros})
    q_enc = q_enc.filter(Encuentro.grupo_id.in_(grupos_miembros))
    if mes is not None:
        q_enc = q_enc.filter(func.extract("month", Encuentro.fecha) == mes)
    if anio is not None:
        q_enc = q_enc.filter(func.extract("year", Encuentro.fecha) == anio)

    encuentros = q_enc.all()
    total_encuentros = len(encuentros)
    enc_ids = [e.id for e in encuentros]

    # Asistencias
    asistencias = (
        db.query(AsistenciaEncuentro)
        .filter(
            AsistenciaEncuentro.encuentro_id.in_(enc_ids),
            AsistenciaEncuentro.miembro_id.in_(miembro_ids),
            AsistenciaEncuentro.estado == EstadoAsistenciaEnum.asistio,
        )
        .all()
    ) if enc_ids else []

    conteo: dict[uuid.UUID, int] = {m.id: 0 for m in miembros}
    for a in asistencias:
        conteo[a.miembro_id] = conteo.get(a.miembro_id, 0) + 1

    resultado = []
    for m in miembros:
        total_asist = conteo.get(m.id, 0)
        porcentaje = (total_asist / total_encuentros * 100) if total_encuentros > 0 else 0.0
        seis_meses_atras = hoy - timedelta(days=182)
        apto = porcentaje >= 75.0 and m.fecha_ingreso <= seis_meses_atras
        resultado.append(AsistenciaMiembroItem(
            miembro_id=m.id,
            nombre=m.nombre_completo,
            fecha_ingreso=m.fecha_ingreso,
            total_encuentros=total_encuentros,
            total_asistencias=total_asist,
            porcentaje=round(porcentaje, 2),
            apto_consagracion=apto,
        ))

    return AsistenciaResponse(miembros=resultado)


# ── R06 Encuentros ────────────────────────────────────────────────────────────

def get_encuentros(
    db: Session,
    grupo_id: Optional[uuid.UUID],
    mes: Optional[int],
    anio: Optional[int],
    actor_grupos: list[uuid.UUID],
    actor_roles: list[str],
) -> EncuentrosResponse:
    from app.domains.encuentros.models import Encuentro, AsistenciaEncuentro, EstadoAsistenciaEnum
    from app.domains.grupos.models import Grupo
    from app.domains.miembros.models import Miembro

    q = db.query(Encuentro)
    if grupo_id is not None:
        q = q.filter(Encuentro.grupo_id == grupo_id)
    elif "asesor_grupo" in actor_roles and "administrador" not in actor_roles and "observador" not in actor_roles:
        if actor_grupos:
            q = q.filter(Encuentro.grupo_id.in_(actor_grupos))
        else:
            return EncuentrosResponse(encuentros=[])

    if mes is not None:
        q = q.filter(func.extract("month", Encuentro.fecha) == mes)
    if anio is not None:
        q = q.filter(func.extract("year", Encuentro.fecha) == anio)

    encuentros = q.all()
    grupos_map = {g.id: g for g in db.query(Grupo).all()}

    resultado = []
    for enc in encuentros:
        grupo_obj = grupos_map.get(enc.grupo_id)
        grupo_nombre = grupo_obj.nombre if grupo_obj else str(enc.grupo_id)

        total_miembros = (
            db.query(func.count(Miembro.id))
            .filter(Miembro.grupo_id == enc.grupo_id, Miembro.activo == True)  # noqa: E712
            .scalar()
            or 0
        )
        total_asistieron = (
            db.query(func.count(AsistenciaEncuentro.id))
            .filter(
                AsistenciaEncuentro.encuentro_id == enc.id,
                AsistenciaEncuentro.estado == EstadoAsistenciaEnum.asistio,
            )
            .scalar()
            or 0
        )
        porcentaje = (total_asistieron / total_miembros * 100) if total_miembros > 0 else 0.0

        resultado.append(EncuentroReporteItem(
            encuentro_id=enc.id,
            fecha=enc.fecha,
            grupo=grupo_nombre,
            tema=enc.tema,
            total_miembros=total_miembros,
            total_asistieron=total_asistieron,
            porcentaje_cobertura=round(porcentaje, 2),
        ))

    return EncuentrosResponse(encuentros=resultado)


# ── R07 Tienda ────────────────────────────────────────────────────────────────

def get_tienda(
    db: Session,
    mes: Optional[int],
    anio: Optional[int],
) -> TiendaResponse:
    from app.domains.tienda.models import VentaDia, EstadoVentaEnum

    # Solo ventas cerradas
    q = db.query(VentaDia).filter(VentaDia.estado == EstadoVentaEnum.cerrado)

    q_mes = q
    if mes is not None:
        q_mes = q_mes.filter(func.extract("month", VentaDia.fecha) == mes)
    if anio is not None:
        q_mes = q_mes.filter(func.extract("year", VentaDia.fecha) == anio)

    ventas_mes = q_mes.all()

    total_mes = sum(float(v.total_calculado) for v in ventas_mes)
    ventas_por_dia = [
        VentaDiaItem(fecha=v.fecha, total=float(v.total_calculado))
        for v in sorted(ventas_mes, key=lambda x: x.fecha)
    ]

    # Acumulado histórico
    acumulado = db.query(func.sum(VentaDia.total_calculado)).filter(
        VentaDia.estado == EstadoVentaEnum.cerrado
    ).scalar() or 0.0

    return TiendaResponse(
        total_mes=total_mes,
        ventas_por_dia=ventas_por_dia,
        acumulado_historico=float(acumulado),
    )


# ── R08 Cuotas ────────────────────────────────────────────────────────────────

def get_cuotas(db: Session, mes: int, anio: int) -> CuotasResponse:
    from app.domains.asesores.models import CuotaAsesor, Asesor

    rows = (
        db.query(CuotaAsesor, Asesor)
        .join(Asesor, CuotaAsesor.asesor_id == Asesor.id)
        .filter(CuotaAsesor.mes == mes, CuotaAsesor.anio == anio)
        .all()
    )

    cuotas = [
        CuotaAsesorItem(
            asesor_id=asesor.id,
            nombre=asesor.nombre_completo,
            estado=cuota.estado.value,
            monto=float(cuota.monto),
            fecha_pago=cuota.fecha_pago,
        )
        for cuota, asesor in rows
    ]

    return CuotasResponse(mes=mes, anio=anio, cuotas=cuotas)


# ── R09 Usuarios ─────────────────────────────────────────────────────────────

def get_usuarios(db: Session) -> UsuariosResponse:
    from app.domains.usuarios.models import Usuario

    usuarios = db.query(Usuario).filter(Usuario.activo == True).all()  # noqa: E712

    items = []
    for u in usuarios:
        roles = [r.rol.value for r in u.roles]
        ultimo = u.ultimo_acceso.isoformat() if u.ultimo_acceso else None
        items.append(UsuarioReporteItem(
            id=u.id,
            nombre=u.nombre_completo,
            email=u.email,
            roles=roles,
            ultimo_acceso=ultimo,
        ))

    return UsuariosResponse(total_activos=len(usuarios), usuarios=items)
